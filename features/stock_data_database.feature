Feature: stock_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the stock_data database.

    Background:
        Given the test database is clear
        And a new database object has been initialised

        Scenario: Add item to stock_data database
            Given I want to add the following item(s) to stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |
            When I run add_data
            Then the following item(s) can be found in stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |
        
        Scenario: Retrieve item from stock_data database
            Given the following item(s) exist in stock_data
                | | |

            And I want to search for {}
            When I run fetch_data
            Then the following item(s) can be found in stock data
                |||

        Scenario: Edit item in stock_data database
            Given the following item(s) exist in stock_data

            And I want to edit {}

            And I want it to restock at {}

            When I run update_data

            Then the following item(s) can be found in stock_data

        Scenario: Delete item from stock_data database
            Given the following item(s) exist in stock_data
            And I want to delete {}
            When I 