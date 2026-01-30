Feature: quantity_data
    As a user, I want to be able to quickly obtain information about total 
    stock quantities, and flag which items need restocking.

    Background:
        Given the test database is clear
        And a new database object has been initialised
        And the target database is current_inventory
        And the following entries exist in location_data:
            | # | name      |
            | 1 | WAREHOUSE |
            | 2 | WORKSHOP  |
        And the following entries exist in stock_data:
            | # | name    | restock_quantity |
            | 1 | WIDGETS | 20               |
            | 2 | SCREWS  | 5                |

        Scenario: M4a - Get the quantity of one specific item
            Given the following entries exist in current_inventory:
                | # | stock_name | location_name  | quantity |
                | 1 | SCREWS     | WORKSHOP       | 10       |
                | 2 | SCREWS     | WORKSHOP       | 5        |
            And I want to find out how many SCREWS we have
            When I run fetch_data
            Then the following data is returned:
                | # | name    | restock_quantity | total_quantity |
                | 2 | SCREWS  | 5                | 15             |

        Scenario: M4b - Calculate quantity for items in different instances and locations
            Given the following entries exist in current_inventory:
                | # | stock_name   | location_name  | quantity |
                | 1 | WIDGETS      | WORKSHOP       | 10       |
                | 2 | WIDGETS      | WORKSHOP       | 5        |
                | 3 | WIDGETS      | WAREHOUSE      | 6        |
                | 4 | SCREWS       | WORKSHOP       | 1        |
                | 5 | SCREWS       | WAREHOUSE      | 2        |
            And I want to find out how much total stock we have
            When I run fetch_data
            Then the following data is returned:
                | # | name    | restock_quantity | total_quantity |
                | 1 | WIDGETS | 20               | 21             |
                | 2 | SCREWS  | 5                | 3              |

        Scenario: M5a - Flag all types without instances as needing restocking
            Given current_inventory is empty
            When I check what needs restocking
            Then I see that everything needs restocking

        Scenario: M5a - Flag items that need restocking in different instances and locations
            Given the following entries exist in current_inventory:
                | # | stock_name   | location_name  | quantity |
                | 1 | WIDGETS      | WORKSHOP       | 10       |
                | 2 | WIDGETS      | WORKSHOP       | 5        |
                | 3 | WIDGETS      | WAREHOUSE      | 6        |
                | 4 | SCREWS       | WORKSHOP       | 1        |
                | 5 | SCREWS       | WAREHOUSE      | 2        |
            When I check what needs restocking
            Then I see that SCREWS need restocking 
