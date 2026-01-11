import sqlite3 as sql
from contextlib import contextmanager
import data_structures as ds

from tkinter import messagebox


from platformdirs import user_data_dir
import sqlite3 as sql
from pathlib import Path

_G_CREATE_STR = "add"
_G_READ_STR = "read"
_G_UPDATE_STR = "update"
_G_DELETE_STR = "delete"

class Database:
    _add_log_string = 'Created'
    _delete_log_string = 'Removed'
    _update_log_string = 'Updated'

    def __init__(self):
        # Gets the user data directory, creates a directory to hold the database and gets a path to where the databse should be created 
        data_dir = Path(user_data_dir("A1_component_tracking"))
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "stock_database.db"
        self._db_path = db_path
        self.initialise_db()

    #########################
    ## def initialiseDb () ##
    #########################
    def initialise_db(self):
        """
        Runs the sql script found at ./dbs/db_sqlite_code.sql
        Creates databases if they are not present in the user data directory
        """
        # Find the path to the sql code for the database
        path = Path(__file__).parent / "dbs/db_sqlite_code.sql"

        conn = sql.connect(self._db_path)
        sqlScript = ""
        with open(path) as f:
            sqlScript = f.read()
        cursor = conn.cursor()
        cursor.executescript(sqlScript)
        conn.commit()
        conn.close()

    @contextmanager
    def get_database_connection(self):
        conn = sql.connect(self._db_path)
        # This row ensures that each row of a query is returned as a dictionary
        conn.row_factory = sql.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def check_restock(self):
        """
        Check if any items of stock need a restock
        Returns a list of items that need restocking
        """
        # Use a blank datastructure to get the quantity of all stock
        total_quantities = self.fetch_quantity_data(ds.QuantityData())
        restock_list = []
        for row in total_quantities:
            if row["restock_quantity"] >= row["current_quantity"]:
                restock_list.append(row)

        return restock_list



    ######################
    ## Add Data Methods ##
    ######################
    def add_data(self, data: ds.SqlData):
        """
        Helper to direct add queries to the correct subfunction
        Logdata is not a case as this should always be directly called from sucessful database operations   
        """
        match data:
            case ds.StockData():
                return self.add_stock_data(data)
            case ds.LocationData():
                return self.add_location_data(data)
            case ds.InventoryData():
                return self.add_inventory_data(data)
            
    def add_stock_data(self, data: ds.StockData):
        with self.get_database_connection() as conn:
            cur = conn.execute("INSERT INTO stock_data (name, base_quantity, restock_quantity)", (data._name, data._base_quantity, data._restock_quantity))

    def add_location_data(self, data: ds.LocationData):
        """
        Adds new locations to location_data        
        """
        with self.get_database_connection() as conn:
            cur = conn.execute("INSERT INTO location_data (name) VALUES (?)", (data._name,))

    def add_inventory_data(self, data: ds.InventoryData):
        query = """
            INSERT INTO
                current_inventory (stock_id, location_id, current_quantity)
            VALUES ((SELECT id FROM stock_data WHERE name = ?),(SELECT id FROM location_data WHERE name = ?), (SELECT base_quantity FROM stock_data WHERE name = ?))
        """
        stock_name = data._stock_type._name
        location_name = data._location._name

        params = (stock_name, location_name, stock_name)
        with self.get_database_connection() as conn:
            cur = conn.execute(query, params)
            log_data = ds.LogData(stock_name=stock_name, location_name=location_name, activity_type=self._add_log_string,update_details=None)
            self.add_log_data(log_data, conn)

    def add_log_data(self, data: ds.LogData, conn: sql.Connection):
        """
        Dynamically adds the relevant data to the activity_logs
        """
        # Gets the relevant keywords
        fields_to_insert = "stock_id, location_id, activity_type"
        values_to_insert = """
            (SELECT id FROM stock_data WHERE name = ?),
            (SELECT id FROM location_data WHERE name = ?),
            ?
            """
        params = [data._stock_name, data._location_name, data._activity_type]

        if data._update_details:
            fields_to_insert += ", update_details"
            values_to_insert += ", ?"
            params.append(data._update_details)

        if data._quantity_change:
            fields_to_insert += ", quantity_change"
            values_to_insert += ", ?"
            params.append(data._quantity_change)

        query = f"""
            INSERT INTO
                activity_logs
                ({fields_to_insert})
            VALUES
                ({values_to_insert})
        """

        conn.execute(query, tuple(params))
            

    ########################
    ## Fetch Data Methods ##
    ########################
    def fetch_data(self, data: ds.SqlData):
        """
        Helper to divert fetch queries to the correct subfunction
        """
        match data:
            case ds.StockData():
                return self.fetch_stock_data(data)
            case ds.LocationData():
                return self.fetch_location_data(data)
            case ds.InventoryData():
                return self.fetch_inventory_data(data)
            case ds.QuantityData():
                return self.fetch_quantity_data(data)
            case _:
                raise Exception("Unrecognised type in fetch_data")
            
    def fetch_stock_data(self, data: ds.StockData):
        """
        Dynamically constructs a query to find the necessary data on known stock types
        """
        query = """
            SELECT
                *
            FROM
                stock_data
            WHERE 1=1
        """
        params = []
        if data._id_str:
            query += " AND id = ?"
            params.append(data._id_str)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]


    def fetch_location_data(self, data: ds.LocationData):
        """
        Dynamically constructs a query to find the necessary data on known locations
        """
        query = """
            SELECT
                *
            FROM
                location_data
            WHERE 1=1
        """
        params = []
        if data._id_str:
            query += " AND id = ?"
            params.append(data._id_str)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]


    def fetch_inventory_data(self, data: ds.InventoryData):
        """
        Dynamically constructs a query to find the necessary data on current inventory contents
        """
        query = """
            SELECT
                current_inventory.id AS id,
                current_inventory.current_quantity AS current_quantity,
                location_data.name AS location_name,
                stock_data.name AS stock_name
            FROM
                current_inventory
            INNER JOIN location_data ON current_inventory.location_id = location_data.id
            INNER JOIN stock_data ON current_inventory.stock_id = stock_data.id
            WHERE 1=1
        """
        params = []

        if data._id_str is not None:
            query += " AND current_inventory.stock_id = ?"
            params.append(data._id_str)

        if data._location._name is not None :
            query += " AND location_data.name = ?"
            params.append(data._location._name)

        if data._stock_type._name is not None:
            query += " AND stock_data.name = ?"
            params.append(data._stock_type._name)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]
        
    def fetch_quantity_data(self, data: ds.QuantityData):
        """
        Fetches data on current stock quantity filtered by type and location
        """
        # For each stock type, sum the current quantities of every stock instance of that type
        query = """
            SELECT
                stock_data.id AS id
                stock_data.name AS name
                stock_data.restock_quantity as restock_quantity
                SUM(current_inventory.current_quantity) AS total_quantity
            FROM
                stock_data
            INNER JOIN current_inventory ON current_inventory.stock_id = stock_data.id
            WHERE 1=1
        """
        params = []
        if data._stock_name:
            query += " AND stock_data.name = ?"
            params.append(data._stock_name)

        if data._location_name:
            query += " AND current_inventory.location_id = (SELECT id FROM location_data WHERE name = ?)"
            params.append(data._location_name)

        query += """
            GROUP_BY stock_data.name
            ORDER_BY stock_data.name
        """
        with self.get_database_connection() as conn:
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

        
    def fetch_log_data(self,data: ds.LogData):
        """
        Fetches relevant logs from the activity logs database
        """
        query = """
            SELECT
                *
            FROM 
                activity_logs
            WHERE 1=1
        """
        params = []

        if data._stock_id is not None :
            query += " AND stock_id = ?"
            params.append(data._stock_id)

        if data._location_id is not None :
            query += " AND location_id = ?"
            params.append(data._location_id)

        if data._activity_type is not None :
            query += " AND activity_type = ?"
            params.append(data._activity_type)

        if data._update_details is not None :
            query += " AND update_details = ?"
            params.append(data._update_details)
        
        if data._quantity_change is not None :
            query += " AND quantity_change = ?"
            params.append(data._quantity_change)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]
        
    
    #########################
    ## Update Data Methods ##
    #########################
    # There is no update method for logs, as these should never be edited after creation
    def update_data(self, data: ds.SqlData):
        """
        Helper to direct update queries to the correct subfunction        
        """
        match data:
            case ds.StockData():
                return self.update_stock_data(data)
            case ds.LocationData():
                return self.update_location_data(data)
            case ds.InventoryData():
                return self.update_inventory_data(data)
            
    def update_stock_data(self, data: ds.StockData):
        """
        Updates the name, base quantity, or restock quantity of a specific location
        Prevents stock being given duplicate names
        """
        query = """
            UPDATE stock_data
            SET id = ?
        """
        params = [data._id_str]
        # Check to see if a name already exists. If it does, do noat allow this operation
        if data._name:
            already_exists = self.fetch_data(ds.StockData(name=data._name))
            if len(already_exists) > 0:
                messagebox.showerror(title="Name already exists", message="Another stock type already has that name. Please choose a different one.")
                return
            query += ", name = ?"
            params.append(data._name)

        if data._restock_quantity:
            query += ", restock_quantity = ?"
            params.append(data._restock_quantity)

        if data._base_quantity:
            query += ", base_quantity = ?"
            params.append(data._base_quantity)

        query += " WHERE id = ?"
        params.append(data._id_str)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))

    def update_location_data(self, data: ds.LocationData):
        """
        Updates the name of a specific location
        Prevents locations from being given duplicate names
        """
        query = """
            UPDATE stock_data
            SET id = ?
        """
        params = [data._id_str]
        # Check to see if a name already exists. If it does, do noat allow this operation
        if data._name:
            already_exists = self.fetch_data(ds.LocationData(name=data._name))
            if len(already_exists) > 0:
                messagebox.showerror(title="Name already exists", message="Another location already has that name. Please choose a different one.")
                return
            query += ", name = ?"
            params.append(data._name)

        if data._restock_quantity:
            query += ", restock_quantity = ?"
            params.append(data._restock_quantity)

        if data._base_quantity:
            query += ", base_quantity = ?"
            params.append(data._base_quantity)

        query += " WHERE id = ?"
        params.append(data._id_str)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))

    def update_inventory_data(self, data: ds.InventoryData):
        query = """
            UPDATE current_inventory
            SET id = ?
        """
        params = [data._id_str]
        if data._location._name:
            query += ", location_id = (SELECT id FROM location_data WHERE name = ?)"
            params.append(data._location._name)

        if data._quantity:
            query += ", current_quantity = ?"
            params.append(data._quantity)

        query += " WHERE id = ?"
        params.append(data._id_str)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return len(cur.fetchall()) > 0


    #########################
    ## Delete Data Methods ##
    #########################
    # There is no delete method for logs, as these should never be deleted
    def delete_data(self, data: ds.SqlData):
        """
        Helper to direct add queries to the correct subfunction        
        """
        match data:
            case ds.StockData():
                return self.delete_stock_data(data)
            case ds.LocationData():
                return self.delete_location_data(data)
            case ds.InventoryData():
                return self.delete_inventory_data(data)
            
    def delete_stock_data(self, data: ds.StockData):
        """
        Deletes stock data.
        This action is prevented if any existing instances reference the stock data
        """
        currently_used = self.fetch_data(ds.InventoryData(stock_type=ds.StockData(name=data._name)))
        if len(currently_used) > 0:
            messagebox.showerror(title="Stock in use", message="This data entry cannot be deleted, as there are stock instances that currently use it")
            return
        
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM stock_data WHERE id = ?", (data._id_str,))

    def delete_location_data(self, data: ds.LocationData):
        """
        Deletes location data.
        This action is prevented if any existing instances reference the location data
        """
        currently_used = self.fetch_data(ds.InventoryData(location=ds.LocationData(name=data._name)))
        if len(currently_used) > 0:
            messagebox.showerror(title="Stock in use", message="This data entry cannot be deleted, as there are stock instances that currently use it")
            return
        
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM location_data WHERE id = ?", (data._id_str,))

    def delete_inventory_data(self, data: ds.InventoryData):
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM current_inventory WHERE id = ?", (data._id_str,))

    #############
    ## Logging ##
    #############


