from behave import given, when, then
from database import Database
import data_structures as ds

def dict_to_dto(row, dto_type):
    """
    Converts feature table row to the appropriate dto
    """
    dto = dto_type()
    if dto_type == ds.InventoryData:
        if "id" in row:
            dto._id = row["id"]
        if "stock_name" in row:
            dto._stock_type._name = row["stock_name"]
        if "location_name" in row:
            dto._location._name = row["location_name"]
        if "quantity" in row:
            dto._quantity = row["quantity"]
    else:
        for field in row:
            if row[field]:
                setattr(dto, f"_{field}", row[field])
    return dto

def row_to_dict(row):
    return {(row.headings[i] if row.headings[i] != "#" else "id"): (int(row.cells[i]) if row.cells[i].isdigit() else row.cells[i]) for i in range(len(row.headings))}

def db_name_to_dto_type(db_name: str):
    match db_name:
        case "stock_data":
            return ds.StockData
        case "location_data":
            return ds.LocationData
        case "current_inventory":
            return ds.InventoryData
        case "activity_log":
            return ds.LogData
        case "stock_quantity":
            return ds.QuantityData
        case _:
            raise Exception("invalid database name")
        
def table_to_dict_list(table):
    return [row_to_dict(row) for row in table]


@given("the test database is clear")
def step_impl(context):
    db = Database(test_data=True)
    db.reset_tables()

@given("a new database object has been initialised")
def step_impl(context):
    context.db = Database(test_data=True)

@given("the target database is {db_name}")
def step_impl(context, db_name):
    context.db_name = db_name

@given("the following entries exist in {db_name}:")
def step_impl(context, db_name):
    main_db = context.db_name == db_name
    if main_db:
        context.row_list = []
    context.row_list = []
    for r in context.table:
        row = row_to_dict(r)
        if main_db:
            context.row_list.append(row)
        dto_type = db_name_to_dto_type(db_name)
        dto = dict_to_dto(row, dto_type)

        try:
            context.db.add_data(dto)
        except:
            assert False

@given("{db_name} is empty")
def step_impl(context, db_name):
    dto = db_name_to_dto_type(db_name)()
    try:
        result = context.db.fetch_data(dto)
        assert len(result) == 0
    except:
        assert False

@given("I want to set the {db_field} of entry #{id} to {new_value}")
def step_impl(context,id, db_field, new_value):
    dict_to_change = [row for row in context.row_list if row["id"] == int(id)][0]
    dto_type = db_name_to_dto_type(context.db_name)
    dto = dict_to_dto(dict_to_change, dto_type)
    setattr(dto, f"_{db_field}", new_value)
    context.dto = dto


@given("I want to delete entry #{id} from {db_name}")
def step_impl(context, id, db_name):
    context.dto = db_name_to_dto_type(context.db_name)()
    setattr(context.dto, "_id", id)


@given("I want to add the following entry to {db_name}:")
def step_impl(context, db_name):
    """
    Create the requisite dto from the feature table
    """
    dto_type = db_name_to_dto_type(db_name)
        
    row = context.table[0]

    row_dict = row_to_dict(row)

    context.row = row_dict
    context.dto = dict_to_dto(row_dict, dto_type)

@given("I want to find out how many {item} we have")
def step_impl(context, item):
    quantity_dto = db_name_to_dto_type("stock_quantity")()
    quantity_dto._stock_name = item
    context.dto = quantity_dto

@given("I want to find out how much total stock we have")
def step_impl(context):
    context.dto= db_name_to_dto_type("stock_quantity")()


@given("an entry with that name already exists")
@given("it is used by other entries")
@given("this does not contain all the necessary data")
def step_impl(context):
    """
    Saves the current database state before the when step modifies it
    """
    dto = db_name_to_dto_type(context.db_name)()
    try:
        context.initial_db_state = context.db.fetch_data(dto)
    except:
        assert False

@given("{item} does not exist in {db_name}")
def step_impl(context, item, db_name):
    """
    Saves the current database state before the when step modifies it
    """
    dto = db_name_to_dto_type(context.db_name)()
    try:
        context.initial_db_state = context.db.fetch_data(dto)
    except:
        assert False

@when("I run {db_method}")
def step_impl(context, db_method):
    """
    Runs the appropriate database method with the data provided
    """
    method = getattr(context.db, db_method)
    try:
        if not db_method == "fetch_data":
            context.result = method(context.dto)
        else:
            context.fetch_result = (method(context.dto))
    except:
        assert False

@when("I check what needs restocking")
def step_impl(context):
    try:
        context.result = context.db.check_restock()
    except:
        assert False

@then('the following entry can be found in {db_name}:')
def step_impl(context, db_name):
    expected_result = row_to_dict(context.table[0])
    db = context.db

    dto_type = db_name_to_dto_type(db_name)

    dto = dict_to_dto(expected_result, dto_type)
    db_list = db.fetch_data(dto)
    assert len(db_list) > 0
    actual_result = db_list[0]

    if "id" in expected_result:
        del expected_result["id"]
    if "id" in actual_result:
        del actual_result["id"]

    if db_name == "activity_log":
        del actual_result["date_occured"]
    if db_name == "current_inventory":
        actual_result = {(key if key != "current_quantity" else "quantity"): value for key, value in actual_result.items()}
        
    for key in actual_result:
        assert expected_result[key]
        assert actual_result[key] == expected_result[key]

@then("{db_name} no longer contains entry #{value}")
def step_impl(context, db_name, value):
    dto = db_name_to_dto_type(db_name)()
    dto._id = value

    result = context.db.fetch_data(dto)

    assert len(result) == 0

@then("{db_name} no longer contains an entry with {field} {value}")
def step_impl(context, db_name, field, value):
    dto = db_name_to_dto_type(db_name)()
    setattr(dto, f"_{field}", value)

    result = context.db.fetch_data(dto)

    assert len(result) == 0

@then('the following error will be returned to the gui:')
def step_impl(context, db_name):
    expected_result = row_to_dict(context.table[0])

    assert expected_result == context.result

@then("{db_name} is not altered")
def step_impl(context, db_name):
    dto = db_name_to_dto_type(db_name)()
    current_db_state = context.db.fetch_data(dto)
    assert context.initial_db_state == current_db_state

@then("the following data is returned:")
def step_impl(context):
    table_list = table_to_dict_list(context.table)
    assert table_list == context.fetch_result

@then("the following error message is returned:")
def step_impl(context):
    row = row_to_dict(context.table[0])
    assert row["title"] == context.result.title
    assert row["message"] == context.result.message

@then("I see that {item_name} needs restocking")
@then("I see that {item_name} need restocking")
def step_impl(context, item_name):
    if item_name == "everything":
        dto = db_name_to_dto_type("stock_quantity")()
        all_stock_types = context.db.fetch_data(dto)
        assert all_stock_types == context.result
    else:
        assert item_name in context.result[0].values()

@then("{db_name} is empty")
def step_impl(context, db_name):
    dto = db_name_to_dto_type(db_name)()
    try:
        result = context.db.fetch_data(dto)
        assert len(result) == 0
    except:
        assert False
