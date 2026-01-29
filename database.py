import sqlite3 as sql
from contextlib import contextmanager
import data_structures as ds
from tkinter import messagebox

from platformdirs import user_data_dir
import sqlite3 as sql
from pathlib import Path
from utils import MsgBoxGenerator

_G_CREATE_STR = "add"
_G_READ_STR = "read"
_G_UPDATE_STR = "update"
_G_DELETE_STR = "delete"

class Database:
    _add_log_string = 'Created'
    _delete_log_string = 'Removed'
    _update_log_string = 'Updated'

    def __init__(self, test_data = False):
        if test_data:
            data_dir = Path("./features/test_data")
        else:
        # Gets the user data directory, creates a directory to hold the database and gets a path to where the databse should be created 
            data_dir = Path(user_data_dir("A1_component_tracking"))
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "stock_database.db"
        self._db_path = db_path
        self.initialise_db()

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
            if row["restock_quantity"] >= row["total_quantity"]:
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
        """
        Adds new stock types to stock_data
        """
        if not data._name or not data._restock_quantity:
            return self.missing_data_popup()
        
        # Check to see if a name already exists. If it does, do not allow this operation
        already_exists = self.fetch_data(ds.StockData(name=data._name))
        if len(already_exists) > 0:
            return MsgBoxGenerator(title="Name already exists", message="Another stock type already has that name.")

        # id may be inserted manually for testing purposes
        if data._id:
            fields = "(id, name, restock_quantity)"
            values = "(?,?,?)"
            params = (data._id, data._name, data._restock_quantity)
        else:
            fields = "(name, restock_quantity)"
            values = "(?,?)"
            params = (data._name, data._restock_quantity)

        with self.get_database_connection() as conn:
            cur = conn.execute(f"INSERT INTO stock_data {fields} VALUES {values}", params)
        return True

    def add_location_data(self, data: ds.LocationData):
        """
        Adds new locations to location_data        
        """
        if not data._name:
            return self.missing_data_popup()
        
        # Check to see if a name already exists. If it does, do not allow this operation
        already_exists = self.fetch_data(ds.LocationData(name=data._name))
        if len(already_exists) > 0:
            return MsgBoxGenerator(title="Name already exists", message="Another location already has that name.")
        
        # id may be inserted manually for testing purposes
        if data._id:
            fields = "(id, name)"
            values = "(?,?)"
            params = (data._id, data._name)
        else:
            fields = "(name)"
            values = "(?)"
            params = (data._name,)

        with self.get_database_connection() as conn:
            cur = conn.execute(f"INSERT INTO location_data {fields} VALUES {values}", params)
        return True

    def add_inventory_data(self, data: ds.InventoryData):
        """
        Adds new stock instances to current_inventory
        """

        stock_name = data._stock_type._name
        location_name = data._location._name
        initial_quantity = data._quantity

        # ensure that all parameters are present
        # If any are missing, then show a warning and return
        if not stock_name or not location_name or not initial_quantity:
            return self.missing_data_popup()
        
        # Check that the name of the stock type and location is in the database
        name_exists = self.fetch_data(ds.StockData(name=stock_name))
        location_exists = self.fetch_data(ds.LocationData(name=location_name))

        if len(name_exists) == 0 and len(location_exists) == 0:
            return MsgBoxGenerator(title="Parameters not found", message="Name and location not present in database")
        elif len(location_exists) == 0:
            return MsgBoxGenerator(title="Parameters not found", message="Location not present in database")
        elif len(name_exists) == 0:
            return MsgBoxGenerator(title="Parameters not found", message="Stock type not present in database")
        
        # id may be inserted manually for testing purposes
        if data._id:
            fields = "(id, stock_id, location_id, current_quantity)"
            values = "(?,(SELECT id FROM stock_data WHERE name = ?),(SELECT id FROM location_data WHERE name = ?), ?)"
            params = (data._id, stock_name, location_name, initial_quantity)
        else:
            fields = "(stock_id, location_id, current_quantity)"
            values = "((SELECT id FROM stock_data WHERE name = ?),(SELECT id FROM location_data WHERE name = ?), ?)"
            params = (stock_name, location_name, initial_quantity)

        query = f"""
            INSERT INTO
                current_inventory {fields}
            VALUES {values}
        """
        with self.get_database_connection() as conn:
            cur = conn.execute(query, params)
            # Log the new instance
            # This gets the id of the newly generated instance by searching for
            # the instance of stock_name with the highest id. This works
            # because sqlite autoincrements the id each time.
            id_str_list = conn.execute("SELECT id FROM current_inventory WHERE stock_id = (SELECT id FROM stock_data WHERE name = ?) ORDER BY id DESC", (stock_name,))
            log_data = ds.LogData(id_str=id_str_list.fetchall()[0],stock_name=stock_name, location_name=location_name, activity_type=self._add_log_string,update_details=None, quantity_change=initial_quantity)
            self.add_log_data(log_data, conn)

        return True

    def add_log_data(self, data: ds.LogData, conn: sql.Connection):
        """
        Dynamically adds the relevant data to the activity_logs
        Note that this must only be called when a database is active
        """
        # Gets the relevant keywords
        fields_to_insert = "instance_id, stock_id, stock_name, location_id, location_name, activity_type"
        instance_id_param = data._id
        # If there is no id, retrieve it
        if not data._stock_id:
            stock_id_param = data._stock_name
            stock_id_query = "(SELECT id FROM stock_data WHERE name = ?)"
        else:
            stock_id_param = data._stock_id
            stock_id_query = "?"
        
        stock_name_param = data._stock_name
        
        if not data._location_id:
            location_id_param = data._location_name
            location_id_query = "(SELECT id FROM location_data WHERE name = ?)"
        else:
            location_id_param = data._location_id
            location_id_query = "?"

        location_name_param = data._location_name

        values_to_insert = f"""
            {stock_id_query},
            ?,
            {location_id_query},
            ?,
            ?
            """
        params = [instance_id_param, stock_id_param, stock_name_param, location_id_param, location_name_param, data._activity_type]

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
            case ds.LogData():
                return self.fetch_log_data(data)
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
        if data._id:
            query += " AND id = ?"
            params.append(data._id)

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
        if data._id:
            query += " AND id = ?"
            params.append(data._id)

        if data._name:
            query += " AND name = ?"
            params.append(data._name)

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

        if data._id is not None:
            query += " AND current_inventory.stock_id = ?"
            params.append(data._id)

        if data._location._name is not None :
            query += " AND location_data.name = ?"
            params.append(data._location._name)

        if data._stock_type._name is not None:
            query += " AND stock_data.name = ?"
            params.append(data._stock_type._name)

        print(query)

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
                stock_data.id AS id,
                stock_data.name AS name,
                stock_data.restock_quantity as restock_quantity,
                COALESCE(SUM(current_inventory.current_quantity),0) AS total_quantity
            FROM
                stock_data
            LEFT JOIN current_inventory ON current_inventory.stock_id = stock_data.id
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
            GROUP BY stock_data.id, stock_data.name, stock_data.restock_quantity
        """

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            vals = cur.fetchall()
            return [dict(row) for row in vals]
      
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
        if not data._restock_quantity:
            return self.missing_data_popup()

        query = """
            UPDATE stock_data
            SET restock_quantity = ?
            WHERE id = ?
        """
        params = (data._restock_quantity, data._id)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, params)

        return True

    def update_location_data(self, data: ds.LocationData):
        """
        Updates the name of a specific location
        Prevents locations from being given duplicate names
        """
        if not data._name:
            return self.missing_data_popup()
        
        query = """
            UPDATE stock_data
            SET id = ?
        """
        params = [data._id]
        # Check to see if a name already exists. If it does, do not allow this operation
        if data._name:
            already_exists = self.fetch_data(ds.LocationData(name=data._name))
            # Allow the name to be "changed" to the current name
            if len(already_exists) > 0 and already_exists[0]["name"] != data._name:
                return MsgBoxGenerator(title="Name already exists", message="Another location already has that name.")
            query += ", name = ?"
            params.append(data._name)

        query += " WHERE id = ?"
        params.append(data._id)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))

        return True

    def update_inventory_data(self, data: ds.InventoryData):
        """
        Update a stock instance, and log the change that has occured
        """
        # get the current values of the stock item being updated
        # also get location_id from the database for ease of operations
        # Updates need to have all necessary data to ensure comprehensive logging

        query = """
            UPDATE current_inventory
            SET id = ?
        """
        params = [data._id]
        if data._location._name:
            query += ", location_id = (SELECT id FROM location_data WHERE name = ?)"
            params.append(data._location._name)

        if data._quantity:
            query += ", current_quantity = ?"
            params.append(data._quantity)

        query += " WHERE id = ?"
        params.append(data._id)

        # Set up the logdata object to be altered
        log_data = ds.LogData(instance_id=data._id, stock_name=data._stock_type._name, location_name=data._location._name, activity_type='Updated')

        with self.get_database_connection() as conn:
            # Get the original values before the query is sent off
            # This is to allow for comprehensive logging
            original_values = self.get_original_values(data, conn)

            # Work out what was changed and use to construct an update code
            # Also checks to make sure a change has been made
            # This helps to detect if a query was submitted where no values had been changed
            if data._location._name != original_values["name"] and data._quantity != original_values["current_quantity"]:
                log_data._update_details = "Both"
            elif data._location._name != original_values["name"]:
                log_data._update_details = "Location"
            elif data._quantity != original_values["current_quantity"]:
                log_data._update_details = "Quantity"
            else:
                return MsgBoxGenerator(title="No value change", message="Please update either location or quantity")

            # Execute the main query
            cur = conn.execute(query, tuple(params))

            # If there was a quantity change, get the quantity change
            if data._quantity:
                log_data._quantity_change = int(original_values["current_quantity"]) - int(data._quantity)

            log_data._stock_name = data._stock_type._name

            # create the log
            self.add_log_data(log_data, conn)

        return True

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
            return MsgBoxGenerator(title="Stock type in use", message="This data entry cannot be deleted, as there are stock instances that currently use it")
        
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM stock_data WHERE id = ?", (data._id,))

        return True

    def delete_location_data(self, data: ds.LocationData):
        """
        Deletes location data.
        This action is prevented if any existing instances reference the location data
        """
        currently_used = self.fetch_data(ds.InventoryData(location=ds.LocationData(name=data._name)))
        if len(currently_used) > 0:
            return MsgBoxGenerator(title="Location in use", message="This data entry cannot be deleted, as there are stock instances that currently use it")
        
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM location_data WHERE id = ?", (data._id,))
        
        return True

    def delete_inventory_data(self, data: ds.InventoryData):
        with self.get_database_connection() as conn:
            ov = self.get_original_values(data, conn)

            cur = conn.execute("DELETE FROM current_inventory WHERE id = ?", (data._id,))

            log_data = ds.LogData(stock_id=ov["stock_id"], location_id=ov["location_id"], activity_type='Removed')

            self.add_log_data(log_data, conn)
        
        return True
    
    #############
    ## utils ##
    #############
    def get_original_values(self, data: ds.SqlData, conn: sql.Connection):
        """
        Fetches the original data from the database
        """
        cur = conn.execute("SELECT * FROM current_inventory WHERE id=", (data._id,))
        return {key: value for key, value in cur.fetchone().enumerate()}

    def missing_data_popup(self):
        """
        Shows an error message if needed fields are not filled in
        """
        return MsgBoxGenerator(title="All fields required", message="All fields must be filled in to perform this operation")

    def reset_tables(self):
        """
        WARNING: only for testing purposes
        """
        with self.get_database_connection() as conn:
            # Drop old tables
            conn.execute("DROP TABLE IF EXISTS activity_logs")
            conn.execute("DROP TABLE IF EXISTS current_inventory")
            conn.execute("DROP TABLE IF EXISTS location_data")
            conn.execute("DROP TABLE IF EXISTS stock_data")
