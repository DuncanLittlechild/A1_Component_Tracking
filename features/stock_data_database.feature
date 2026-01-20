Feature: stock_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the stock_data database.

    Background:
        Given the test database is clear
        And a new database object has been initialised

        Scenario: Add item to stock_data database
            Given I want to store screws in my inventory
            And they need restocking when there are fewer than 20 of them
            When I add them as a stock type
            Then screws that restock at 20 can be found in the database "stock_data"