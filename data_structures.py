from datetime import datetime
import tkinter as tk

#######################
## class CreateDb ##
#######################
# The function to create database entries and the classes to hold the information for them

class SqlData:
    """
    Blank class that classes whose job it is to pass data between the ui and the database can inherit from
    """
    pass

class StockData(SqlData):
    """
    Passes data on stock types between the ui and the database
    """
    def __init__(self, restock_quantity: str = None, id_str: str = None, name: str = None, base_quantity: str = None):
        self._id = id_str
        self._name = name
        self._restock_quantity = restock_quantity
        self._base_quantity = base_quantity

class LocationData(SqlData):
    """
    Passes data on locations between the ui and the database
    """
    def __init__(self, name: str = None, id_str: str = None):
        self._id_str = id_str
        self._name = name

class InventoryData(SqlData):
    """
    Passes data on current inventory between the ui and the database
    """
    def __init__(self, id_str: str = None, location: LocationData = LocationData(), stock_type: StockData = StockData()):
        self._id_str = id_str
        self._location = location
        self._stock_type = stock_type
