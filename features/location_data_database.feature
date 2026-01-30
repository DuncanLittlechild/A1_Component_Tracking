Feature: location_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the location_data database.

    Background:
        Given the test database is clear
        And a new database object has been initialised
        And the target database is location_data

        Scenario: S1a - Add location to location_data database
            Given I want to add the following entry to location_data:
                | name     |
                | HANGER 1 |
            When I run add_data
            Then the following entry can be found in location_data:
                | name     |
                | HANGER 1 |

        Scenario: S1b - Location not added if name field is missing
            Given I want to add the following entry to location_data:
                | |
                | |
            But this does not contain all the necessary data
            When I run add_data
            Then location_data is not altered
            And the following error message is returned:
                | title               | message                                                |
                | All fields required | All fields must be filled in to perform this operation |

        Scenario: S3b - Location not added if it shares a name with a eisting type
            Given the following entries exist in location_data:
                | # | name      |
                | 1 | WAREHOUSE |
            And I want to add the following entry to location_data:
                | name      |
                | WAREHOUSE |
            But an entry with that name already exists
            When I run add_data
            Then location_data is not altered
            And the following error message is returned:
                | title               | message                                 |
                | Name already exists | Another location already has that name. |

        Scenario: S2c - Edit location in location_data database
            Given the following entries exist in location_data:
                | # | name      |
                | 1 | WAREHOUSE |
            And I want to set the name of entry #1 to WORKSHOP
            When I run update_data
            Then the following entry can be found in location_data:
                | # | name     |
                | 1 | WORKSHOP |

        Scenario: C1a - Delete location from location_data database
            Given the following entries exist in location_data:
                | # | name      |
                | 1 | WAREHOUSE |
            And I want to delete entry #1 from location_data
            When I run delete_data
            Then location_data no longer contains entry #1

        Scenario: C1b - Location not deleted if any instance is of that type
            Given the following entries exist in stock_data:
                | # | name   | restock_quantity |
                | 1 | CHAIRS | 5                |
            And the following entries exist in location_data:
                | # | name     |
                | 1 | WORKSHOP |
            And the following entries exist in current_inventory:
                | # | stock_name | location_name | quantity |
                | 1 | CHAIRS     | WORKSHOP      | 20       |
            And I want to delete entry #1 from location_data
            But it is used by other entries
            When I run delete_data
            Then location_data is not altered
            And the following error message is returned:
                | title           | message                                                                               |
                | Location in use | This data entry cannot be deleted, as there are stock instances that currently use it |
