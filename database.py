import sqlite3 as sql
from contextlib import contextmanager
import data_structures as ds


from platformdirs import user_data_dir
import sqlite3 as sql
from pathlib import Path

_G_CREATE_STR = "add"
_G_READ_STR = "read"
_G_UPDATE_STR = "update"
_G_DELETE_STR = "delete"

class Database:
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
        """


    ######################
    ## Add Data Methods ##
    ######################
    def add_data(self, data: ds.SqlData):
        """
        Helper to direct add queries to the correct subfunction        
        """
        match data:
            case ds.StockData():
                return self.add_stock_data(data)
            case ds.LocationData():
                return self.add_location_data(data)
            case ds.InventoryData():
                return self.add_inventory_data(data)
            
    def add_stock_data(self, data: ds.StockData):
        pass

    def add_location_data(self, data: ds.LocationData):
        pass

    def add_inventory_data(self, data: ds.InventoryData):
        query = """
            INSERT INTO
                current_inventory (stock_id, location_id, current_quantity)
            VALUES ((SELECT id FROM stock_data WHERE name = ?),(SELECT id FROM location_data WHERE name = ?), (SELECT base_quantity FROM stock_data WHERE name = ?))
        """
        params = (data._stock_type._name, data._location._name, data._stock_type._name)
        with self.get_database_connection() as conn:
            cur = conn.execute(query, params)

    def add_log_data(self, data: ds.LogData):
        pass
            

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
                print("diverted")
                return self.fetch_inventory_data(data)
            
    def fetch_stock_data(self, data: ds.StockData):
        pass

    def fetch_location_data(self, data: ds.LocationData):
        pass

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
        query = """
            SELECT

        """
        
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
        pass

    def update_location_data(self, data: ds.LocationData):
        pass

    def update_inventory_data(self, data: ds.InventoryData):
        query = """
            UPDATE current_inventory
            SET stock_id = ?
        """
        params = [data._id_str]
        if data._location._name:
            query += ", location_id = (SELECT id FROM location_data WHERE name = ?)"
            params.append(data._location._name)

        if data._quantity:
            query += ", current_quantity = ?"
            params.append(data._quantity)

        query += " WHERE stock_id = ?"
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
        pass

    def delete_location_data(self, data: ds.LocationData):
        pass

    def delete_inventory_data(self, data: ds.InventoryData):
        with self.get_database_connection() as conn:
            cur = conn.execute("DELETE FROM current_inventory WHERE id = ?", (data._id_str))

    #############
    ## Logging ##
    #############


