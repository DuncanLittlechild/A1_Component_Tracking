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
                current_inventory.stock_id AS id,
                current_inventory.current_quantity AS current_quantity,
                location_data.name AS location_name,
                stock_data.name AS stock_name
            FROM
                current_inventory
            INNER JOIN location_data ON current_inventory.location_id = location_data.id
            INNER JOIN stock_ids ON current_inventory.stock_id = stock_ids.id
            INNER JOIN stock_data ON stock_ids.stock_data_id = stock_data.id
            WHERE 1=1
        """
        params = []

        if data._location._name is not None :
            query += " AND location_data.name = ?"
            params.append(data._location._name)

        if data._stock_type._name is not None:
            query += " AND stock_data.name = ?"
            params.append(data._stock_type._name)

        with self.get_database_connection() as conn:
            cur = conn.execute(query, tuple(params))
            return [dict(row) for row in cur.fetchall()]
        

#############
## Logging ##
#############
def log_query(activity_type: str, stock_id: str, quantity_change: str, cur: sql.Cursor):
    cur.execute("INSERT INTO activity_logs (stock_id, activity_type, quantity_change) VALUES (?,?,?)", (stock_id, activity_type, quantity_change))

