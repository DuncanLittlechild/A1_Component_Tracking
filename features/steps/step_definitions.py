from behave import given, when, then
from database import Database
import data_structures as ds

@given("the test database is clear")
def step_impl(context):
    db = Database(test_data=True)
    db.reset_tables()

@given("a new database object has been initialised")
def step_impl(context):
    context.db = Database(test_data=True)

@given("I want to store {stock_type} in my inventory")
def step_impl(context, stock_type):
    context.stock_name = stock_type

@given("they need restocking when there are fewer than {restock_quantity} of them")
def step_impl(context, restock_quantity):
    context.restock_quantity = restock_quantity

@when("I add them as a stock type")
def step_impl(context):
    stock = ds.StockData(restock_quantity=context.restock_quantity, name=context.stock_name)
    context.db.add_data(stock)

@then('{stock_type} that restock at {restock_quantity} can be found in the database "stock_data"')
def step_impl(context, stock_type, restock_quantity):
    stock_query = ds.StockData(restock_quantity=restock_quantity, name=stock_type)
    actual_stock = context.db.fetch_data(stock_query)
    assert len(actual_stock) == 1
    assert actual_stock[0]["name"] == stock_type
    assert actual_stock[0]["restock_quantity"] == int(restock_quantity)
