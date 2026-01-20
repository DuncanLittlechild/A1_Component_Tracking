"""
Feature: current_inventory
    As a user, I want to be able to perform the full range of CRUD operations
    on the current_inventory database, and ensure tha matching log files are created

    Background:
        Given the test database is clear
        And a new database object has been initialised
        And the following stock types exist:

        And the following locations exist:

        Scenario: Add item to current_inventory database
            Given I have recieved a shipment of 20 screws
            And I want to store them in the location "Warehouse"
            When I add them to the database
            Then a new item is added to current_inventory with the following data:

            And a new activity log is created with the following data
            """