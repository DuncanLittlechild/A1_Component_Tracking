Feature: current_inventory
    As a user, I want to be able to perform the full range of CRUD operations
    on the current_inventory database. These operations should all be recorded
    in the activity_log database

    Background:
        Given the test database is clear
        And a new database object has been initialised
        And the target database is current_inventory
        And the following entries exist in stock_data:
            | # | name    | restock_quantity |
            | 1 | SCREWS  | 5                |
            | 2 | CHAIRS  | 10               |
            | 3 | WIDGETS | 20               |
        And the following entries exist in location_data:
            | # | name      |
            | 1 | WAREHOUSE |
            | 2 | WORKSHOP  |
            | 3 | HANGER    |


        Scenario: M1a, M6a - Add instance to current_inventory
            Given I want to add the following entry to current_inventory:
                | stock_name | location_name | quantity |
                | SCREWS     | WORKSHOP      | 20       |
            When I run add_data
            Then the following entry can be found in current_inventory:
                | stock_name | location_name | quantity |
                | SCREWS     | WORKSHOP      | 20               |
            And the following entry can be found in activity_log:
                | # | instance_id | stock_id | stock_name | location_id | location_name | activity_type | update_details | quantity_change |
                | 1 | 1           | 1        | SCREWS     | 2           | WORKSHOP      | Created       | N/A            | 20              |

        Scenario: M1b, M6b - Instance not added if any field is missing
            Given I want to add the following entry to current_inventory:
                | stock_name | quantity |
                | SCREWS     | 20       |
            But this does not contain all the necessary data
            When I run add_data
            Then current_inventory is not altered
            And the following error message is returned:
                | title               | message                                                |
                | All fields required | All fields must be filled in to perform this operation |
            And activity_log is empty

        Scenario: M8a, M6a - Instance not added if its stock_name is not in stock_data
            Given I want to add the following entry to current_inventory:
                | stock_name  | location_name | quantity |
                | GADGETS     | WORKSHOP      | 20       |
            But GADGETS does not exist in stock_data
            When I run add_data
            Then current_inventory is not altered
            And the following error message is returned:
                | title                | message                            |
                | Parameters not found | Stock type not present in database |
            And activity_log is empty

        Scenario: M9a, M6b - Instance not added if its location_name is not in location_data
            Given I want to add the following entry to current_inventory:
                | stock_name  | location_name | quantity |
                | WIDGETS     | GARAGE        | 20       |
            But GARAGE does not exist in location_data
            When I run add_data
            Then current_inventory is not altered
            And the following error message is returned:
                | title                | message                          |
                | Parameters not found | Location not present in database |
            And activity_log is empty

        Scenario: M2a, M6a - Edit instance in current_inventory
            Given the following entries exist in current_inventory:
                | # | stock_name | location_name | quantity |
                | 1 | SCREWS     | WORKSHOP      | 20       |
            And I want to set the quantity of entry #1 to 5
            When I run update_data
            Then the following entry can be found in current_inventory:
                | # | stock_name | location_name | quantity |
                | 1 | SCREWS     | WORKSHOP      | 5                |
            And the following entry can be found in activity_log:
                | # | instance_id | stock_id | stock_name | location_id | location_name | activity_type | update_details | quantity_change |
                | 1 | 1           | 1        | SCREWS     | 2           | WORKSHOP      | Updated       | Quantity       | 15              |

        Scenario: M10a, M6a - Delete instance from current_inventory
            Given the following entries exist in current_inventory:
                | # | stock_name | location_name | quantity |
                | 1 | SCREWS     | WORKSHOP      | 20       |
            And I want to delete entry #1 from current_inventory
            When I run delete_data
            Then current_inventory no longer contains entry #1
            And the following entry can be found in activity_log:
                | # | instance_id | stock_id | stock_name | location_id | location_name | activity_type | update_details | quantity_change |
                | 1 | 1           | 1        | SCREWS     | 2           | WORKSHOP      | Removed       | N/A            | 20              |