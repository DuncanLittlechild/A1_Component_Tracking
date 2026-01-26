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
    def __init__(self, restock_quantity: str = None, id_str: str = None, name: str = None):
        self._id_str = id_str
        self._name = name
        self._restock_quantity = restock_quantity

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
    def __init__(self, id_str: str = None, location: LocationData = LocationData(), stock_type: StockData = StockData(), quantity: str = None):
        self._id_str = id_str
        self._location = location
        self._stock_type = stock_type
        self._quantity = quantity

class QuantityData(SqlData):
    """
    Passes data on current stock quantity query between the ui and the database
    """
    def __init__(self, stock_name: str = None, location_name: str = None):
        self._stock_name = stock_name
        self._location_name = location_name

class LogData(SqlData):
    """
    Passes data on log query between the ui and the database
    """
    def __init__(self, id_str: str = None, instance_id: str = None, stock_name: str = None, stock_id:str = None, location_name: str = None, location_id: str = None, activity_type: str = None, update_details: str = None, quantity_change: str = None, date_occured:str = datetime.now().strftime("%Y-%m-%d %H:%M%S")):
        if not stock_name or not location_name:
            raise Exception("Trying to generate log without stock or location name")
        self._id_str = id_str
        self._instance_id = instance_id
        self._stock_name = stock_name
        self._stock_id = stock_id
        self._location_name = location_name
        self._location_id = location_id
        self._activity_type = activity_type
        self._update_details = update_details
        self._quantity_change = quantity_change
        self._date_occured = date_occured
