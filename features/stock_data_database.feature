Feature: stock_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the stock_data database.

    Background:
        Given the test database is clear
        And a new database object has been initialised
        And the target database is stock_data

        Scenario: S1a - Add stock type to stock_data database
            Given I want to add the following entry to stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |
            When I run add_data
            Then the following entry can be found in stock_data:
                | name   | restock_quantity |
                | SCREWS | 20               |
        
        Scenario: S1b - Stock type not added if any field is missing
            Given I want to add the following entry to stock_data:
                | name    |
                | WIDGETS |
            But this does not contain all the necessary data
            When I run add_data
            Then stock_data is not altered
            And the following error message is returned:
                | title               | message                                                |
                | All fields required | All fields must be filled in to perform this operation |

        Scenario: S3a - Stock type not added if it shares a name with an existing type
            Given the following entries exist in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 5                |
            And I want to add the following entry to stock_data:
                | name   | restock_quantity |
                | CHAIRS | 20               |
            But an entry with that name already exists
            When I run add_data
            Then stock_data is not altered
            And the following error message is returned:
                | title               | message                                   |
                | Name already exists | Another stock type already has that name. |

        Scenario: S2a - Edit stock type in stock_data database
            Given the following entries exist in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 5                |
            And I want to set the restock_quantity of entry #1 to 10
            When I run update_data
            Then the following entry can be found in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 10               |

        Scenario: C2a - Delete stock type from stock_data database
            Given the following entries exist in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 5                |
            And I want to delete entry #1 from stock_data
            When I run delete_data
            Then stock_data no longer contains an entry with id 1

        Scenario: C2b - Stock type not deleted if any instance is of that type
            Given the following entries exist in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 5                |
            And the following entries exist in location_data:
                | # | name     |
                | 1 | WORKSHOP |
            And the following entries exist in current_inventory:
                | # | stock_name | location_name | quantity |
                | 1 | CHAIRS     | WORKSHOP      | 20               |
            And I want to delete entry #1 from stock_data
            But it is used by other entries
            When I run delete_data
            Then stock_data is not altered
            And the following error message is returned:
                | title             | message                                                                               |
                | Stock type in use | This data entry cannot be deleted, as there are stock instances that currently use it |

