"""
Feature: location_data
    As a user, I want to be able to perform the full range of CRUD operations
    on the location database.

    Background:
        Given the test database is clear
        And a new database object has been initialised

        Scenario: Add item to location database
            Given I want to store stock in the location named "Warehouse"
            When I add them as a location
            Then Warehouse can be found in the database "location_data"
            """