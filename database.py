import sqlite3 as sql
import datetime


from platformdirs import user_data_dir
import sqlite3 as sql
from pathlib import Path

# Gets the user data directory, creates a directory to hold the database and gets a path to where the databse should be created 
_G_DATA_DIR = Path(user_data_dir("A1_component_tracking"))
_G_DATA_DIR.mkdir(parents=True, exist_ok=True)
_G_DB_PATH = _G_DATA_DIR / "stock_database.db"

_G_CREATE_STR = "add"
_G_READ_STR = "read"
_G_UPDATE_STR = "update"
_G_DELETE_STR = "delete"

#########################
## def initialiseDb () ##
#########################
def initialiseDb():
    """
    Runs the sql script found at ./dbs/db_sqlite_code.sql
    Creates databases if they are not present in the user data directory
    """
    # Find the path to the sql code for the database
    path = Path(__file__).parent / "dbs/db_sqlite_code.sql"


    conn = sql.connect(_G_DB_PATH)
    sqlScript = ""
    with open(path) as f:
        sqlScript = f.read()
    cursor = conn.cursor()
    cursor.executescript(sqlScript)
    conn.commit()
    conn.close()


#################
## class Query ##
#################
# Parent class to set up and submit queries

class Query:
    """
    Holds the data and submits the queries
    Uses dependency injection to allow for a wide range of queries to be submitted
    """
    def __init__(self, data):
        self._data = data
        match data:
            case AddStockData():
                self._query_type = stock_create_db
            case AddLocationData():
                self._query_type = location_create_db
            case AddInventoryData():
                self._query_type = inventory_create_db
        self._result = QueryResult()
    
    def run(self):
        self._query_type(self._data, self._result)

#####################
## Validity checks ##
#####################
# Functions to check that parameters are valid
def is_valid_name(name: str)->bool:
    """
    Checks to see if the name is valid
    Names shouldn't include non-alphanumeric characters except for whitespace
    Future feature: this will switch to using regexes to ensure that the name follows a logical format
    """
    return all(c.isalnum() or c.isspace() for c in name)

def in_database(db: str, param: str, param_name: str, cur: sql.Cursor) -> bool:
    # Check to see if the name is already in the database
    cur.execute("SELECT * FROM ? WHERE ? = ?", (db, param, param_name))
    return len(cur.fetchall()) > 0


#######################
## class QueryResult ##
#######################
class QueryResult:
    """
    Holds the result of a database query, and any relevant error messages
    """
    def __init__(self):
        self._success = True
        self._msg = ""

    def error(self, msg: str):
        self._success = False
        if self._msg == "":
            self._msg = msg
        else:
            self._msg += f"; {msg}"

#############
## Logging ##
#############
def log_query(activity_type: str, stock_id: str, quantity_change: str, cur: sql.Cursor):
    cur.execute("INSERT INTO activity_logs (stock_id, activity_type, quantity_change) VALUES (?,?,?)", (stock_id, activity_type, quantity_change))

#######################
## class CreateDb ##
#######################
# The function to create database entries and the classes to hold the information for them

class AddData:
    """
    Blank class that classes whose purpose is to provide data for a CREATE query can inherit from.
    This exists to make it easy to indicate the subset of classes create_db should take as parameters
    """
    pass

class AddStockData(AddData):
    """
    Holds the data for a query to add a new type of stock to the stock database
    Quantity will be entered as a string, and therefore is passed in here as one
    """
    def __init__(self, name: str, base_quantity: str = "1"):
        self._name = name
        self._base_quantity = base_quantity

class AddLocationData(AddData):
    """
    Holds the data for a query to add a new location to the location database
    """
    def __init__(self, name: str):
        self._name = name

class AddInventoryData(AddData):
    """
    Holds the data for a query to add a new stock instance to the current stock database
    """
    def __init__(self, stock_name: str, location_name: str, occured_at: datetime = datetime.now()):
        self._stock_name = stock_name
        self._location_name = location_name
        self._occured_at = occured_at


def stock_create_db(data: AddStockData, result: QueryResult):
    """
    Submits a database query to add a new stock type to stock_data
    Args:
        data: AddStockData - contains the name and initial quantity of the new stock data
    """
    # Get data from the data object
    name = data._name.lower()
    base_quantity = data._base_quantity

    # validate data from data object
    if not is_valid_name(name):
        result.error("Name is invalid.")

    if not base_quantity.isdigit():
        result.error("Base_quantity is invalid.")

    # If either validation step failed, return the error message
    if not result._success:
        return result

    # Check to see if the name is already in the database
    conn = sql.connect(_G_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM stock_data WHERE name = ?", name)
    if in_database("stock_data", "name", name, cur):
        result.error("Name already present in database")
        return result

    # Run the query
    try:
        cur.execute("INSERT INTO stock_data (name, base_quantity) VALUES(?,?)",
                    (name, base_quantity))
    except sql.Error:
        conn.close()
        result.error("Failed to add to stock_data")
        return result
    
    conn.commit()
    conn.close()
    result._msg(f"A new stock type was created with name {name} and base quantity {base_quantity}")

def location_create_db(data: AddLocationData, result: QueryResult):
    """
    Submits a database query to add a new location to location_data
    Args:
        data: AddLocationData - contains the name of the new location
    """
    # Get data from the data object
    name = data._name.lower()

    # validate data from data object
    if not is_valid_name(name):
        result.error("Name is invalid.")
        return result

    # Check to see if the name is already in the database
    conn = sql.connect(_G_DB_PATH)
    cur = conn.cursor()
    if in_database("location_data", "name", name, cur):
        result.error("Name already present in database")
        return result

    # Run the query
    try:
        cur.execute("INSERT INTO location_data (name) VALUES(?)",
                    (name,))
    except sql.Error:
        conn.close()
        result.error("Failed to add to location_data")
        return result
    
    conn.commit()
    conn.close()
    result._msg(f"A new stock type was created with name {name}")

def inventory_create_db(data: AddInventoryData, result: QueryResult):
    """
    Submits a database query to add a new stock instance to current_inventory
    Args:
        data: AddInventoryData - contains the stock type, location, and timestamp added of the new stock instance
    """
    # Get data from the data object
    stock_name = data._stock_name.lower()
    location_name = data._location_name.lower()
    occured_at = data._occured_at

    # validate data from data object
    if not is_valid_name(stock_name):
        result.error("Stock name is invalid.")

    if not is_valid_name(location_name):
        result.error("Location name is invalid.")

    if not is_valid_date(occured_at):
        result.error("Date occured is invalid.")

    # If any validation step failed, return the error message
    if not result._success:
        return

    # try to get both ids from database
    conn = sql.connect(_G_DB_PATH)
    cur = conn.cursor()
    stock_data_list = cur.execute("SELECT id, base_quantity FROM stock_data WHERE name = ?", (stock_name)).fetchone()

    location_id_list = cur.execute("SELECT id FROM location_data WHERE name = ?", (location_name)).fetchone()

    # If either id is not present in the database, log the error/s then return
    if len(stock_data_list) == 0:
        result.error("Stock name not found in database")

    if len(location_id_list) == 0:
        result.error("Location name not found in database")

    if not result._success:
        return

    # Run the query
    # The nature of sqlite3 ensures that the database is only changed if commit is called, ensuring that all updates are transactional
    # Logging is also done here to ensure that the database is not updated if the log fails to create
    try:
        # Create a new stock instance in the stock_ids db
        cur.execute("INSERT INTO stock_ids (stock_data_id) VALUES(?)", (stock_data_list[0]))
        # get the id of the new stock instance
        stock_id = cur.execute("SELECT id FROM stock_ids WHERE stock_data_id = ?", stock_data_list[0]).fetchone[0]
        # Insert the new data into the current_stock table
        cur.execute("INSERT INTO current_stock (stock_id, location_id, current_quantity, occured_at) VALUES (?,?,?,?)", (stock_id, location_id_list[0], stock_data_list[1], occured_at))
        # Log the transaction
        log_query(_G_CREATE_STR, stock_id, stock_data_list[1], cur)

    except sql.Error:
        conn.close()
        result.error("Failed to add to stock_data")
        return
    
    # Commit and close the connection
    conn.commit()
    conn.close()
    # Update the results message
    result._msg(f"A new instance of {stock_name} at location {location_name} has been recorded. This operation was sucessfully logged")


#######################
## class RetrieveDb ##
#######################
# Class to retrieve data from the database
class RetrieveInventoryData:
    def __init__(self):
        pass


####################
## class UpdateDb ##
####################
# Class to update the database


####################
## class DeleteDb ##
####################
# Class to delete part of the database


##########################
## class ReplenishCheck ##
##########################
# Class to run the check to see if a product needs replenishment

