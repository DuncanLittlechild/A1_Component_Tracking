from behave import given, when, then
from database import Database
import data_structures as ds

def dict_to_dto(row, dto_type):
    """
    Converts feature table row to the appropriate dto
    """
    dto = dto_type()
    for field in row:
        if row[field]:
            setattr(dto, f"_{field}", row[field])
    return dto

def row_to_dict(row):
    return {row.headings[i]: (int(row.cells[i]) if row.cells[i].isdigit() else row.cells[i]) for i in range(len(row.headings))}

def db_name_to_dto(db_name: str):
    match db_name:
        case "stock_data":
            return ds.StockData
        case "location_data":
            return ds.LocationData
        case "current_inventory":
            return ds.InventoryData
        case "log_data":
            return ds.LogData
        case "stock_quantity":
            return ds.QuantityData
        case _:
            raise Exception("invalid database name")


@given("the test database is clear")
def step_impl(context):
    db = Database(test_data=True)
    db.reset_tables()

@given("a new database object has been initialised")
def step_impl(context):
    context.db = Database(test_data=True)

@given("the following items exist in {db_name}:")
def step_impl(context, db_name):
    for r in context.table:
        row = row_to_dict(r)
        dto_type = db_name_to_dto(db_name)
        dto = dict_to_dto(row, dto_type)

        try:
            context.db.add_data(dto)
        except Exception as e:
            raise e

@given("I want to update the {db_field} to {new_value}")
def step_impl(context, db_field, new_value):
    setattr(context.dto, f"_{db_field}", new_value)

@given("I want to add the following item to {db_name}:")
def step_impl(context, db_name):
    """
    Create the requisitte dto from the feature table
    """
    dto_type = db_name_to_dto(db_name)
        
    row = context.table[0]
    print(type(row))
    row_dict = row_to_dict(row)

    context.row = row_dict
    context.dto = dict_to_dto(row_dict, dto_type)


@when("I run {db_method}")
def step_impl(context, db_method):
    """
    Runs the appropriate database method with the data provided
    """
    method = getattr(context.db, db_method)
    if not db_method == "fetch_data":
        context.result = method(context.dto)
    else:
        context.fetch_result = (method(context.dto))


@then('the following item can be found in {db_name}:')
def step_impl(context, db_name):
    expected_result = row_to_dict(context.table[0])
    db = context.db

    dto_type = db_name_to_dto(db_name)

    dto = dict_to_dto(expected_result, dto_type)
    actual_result = db.fetch_data(dto)[0]
    del actual_result["id"]
    assert expected_result == actual_result

@then('the following error will be returned to the gui:')
def step_impl(context, db_name):
    expected_result = row_to_dict(context.table[0])

    assert expected_result == context.result