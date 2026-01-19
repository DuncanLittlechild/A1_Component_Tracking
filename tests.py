from database import Database
from data_structures import InventoryData


def reset_table():
    db = Database()
    db.reset_tables()

def test_inventory_database_fetch():
    db = Database()
    try:
        db.fetch_data(InventoryData())
    except Exception as e:
        raise e

test_inventory_database_fetch()