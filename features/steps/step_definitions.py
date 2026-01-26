from behave import given, when, then
from database import Database
import data_structures as ds

def row_to_dto(row, dto_type):
    """
    Converts feature table row to the appropriate dto
    """
    dto = dto_type()
    for field in row:
        if row[field]:
            setattr(dto, field, row[field])
    return dto

# Helpers to standardise step syntax
def get_stock_data(db: Database, row: dict):
    pass

def get_location_data(db: Database):
    pass

def get_current_inventory(db: Database):
    pass


@given("the test database is clear")
def step_impl(context):
    db = Database(test_data=True)
    db.reset_tables()

@given("a new database object has been initialised")
def step_impl(context):
    context.db = Database(test_data=True)

@given("I want to add the following item to {db_name}:")
def step_impl(context, db_name):
    """
    Check the database type, generate the requisite dto, and then create one of
    them per row in the context table.
    Sets up context.row_list (list of rows from the input table)
            context.dto_list (list of dtos generated from the input table)
    """
    match db_name:
        case "stock_data":
            dto_type = ds.StockData
        case "location_data":
            dto_type = ds.LocationData
        case "current_inventory":
            dto_type = ds.InventoryData
        case _:
            raise Exception("invalid database name")
    
    row = dict(context.table[0])

    context.row = row
    context.dto = row_to_dto(row, dto_type)


@when("I run {db_method}")
def step_impl(context, db_method):
    """
    Runs the appropriate database method with the data provided
    """
    method = getattr(context.db, db_method)
    if not db_method == "fetch_data":
        method(context.dto)
    else:
        context.fetch_result = (method(context.dto))


@then('the following item can be found in {db_name}')
def step_impl(context, db_name):
    expected_result = dict(context.table[0])
    row = context.row
    db = context.db
    match db_name:
        case "stock_data":
            actual_result = get_stock_data(db, row)
        case "location_data":
            actual_result = get_location_data(db, row)
        case "current_inventory":
            actual_result = get_current_inventory(db, row)

    assert len(actual_result) == len(expected_result)
    assert actual_result == expected_result
