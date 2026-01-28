Feature: stock_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the stock_data database.

    Background:
        Given the test database is clear
        And a new database object has been initialised

        Scenario: Add item to stock_data database
            Given I want to add the following item to stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |
            When I run add_data
            Then the following item can be found in stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |

        Scenario: Edit item in stock_data database
            Given the following item has been added to stock_data:
                | name   | restock_quantity |
                | CHAIRS | 5                |
            And I want to update the restock_quantity to 10
            When I run update_data
            Then the following item can be found in stock_data:
                | name   | restock_quantity |
                | CHAIRS | 10               |

        Scenario: Delete item from stock_data database
            Given the following items exist in stock_data
                | name   | restock_quantity |
                | CHAIRS | 5                |
            And I want to delete it
            When I run delete_data
