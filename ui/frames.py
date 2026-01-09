import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import data_structures as ds
import validation as valid

########################
## class ChooseFrame  ##
########################
# Frame to display operation choice
class ChooseFrame(ttk.Frame):
    """
    Frame to display the choice of database to operate on.
    Inventory database is the main one here
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Labels and options to perform different queries
        self.options_label = ttk.Label(self, text="What database would you like to check?").pack()
    
        self.inventory_button = ttk.Button(self, text=f"Inventory", command=lambda: self.controller.show_frame(InventoryFrame)).pack()
        self.location_button = ttk.Button(self, text=f"Locations", command=lambda: self.controller.show_frame(LocationFrame)).pack()
    
        self.stock_button = ttk.Button(self, text=f"Stock Types", command=lambda: self.controller.show_frame(StockFrame)).pack()
        self.log_button = ttk.Button(self, text=f"Activity Logs", command=lambda: self.controller.show_frame(LogFrame)).pack()
        # Exit button
        self.exitButton = ttk.Button(self, text="exit", command=self.controller.destroy).pack()


class InventoryFrame(ttk.Frame):
    """
    Frame to display the main inventory
    All operations on this page allow the user to perform CRUD operations on stock instances
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller

        self._search_params = {
            "name": tk.StringVar(),
            "location" : tk.StringVar()
        }

        self._validity_log = valid.ValidityCheck()

        self.create_widgets()

        self.load_data()


    def create_widgets(self):
        """
        Creates the widgets needed for the inventory frame
        """
        title_label = ttk.Label(self, text="Current Inventory")
        title_label.pack()

        ## Create search bars ##
        search_bars = ttk.Frame(self)
        search_bars.pack(fill="x", padx=10, pady=5)

        # Bar to search for name
        name_search_label = ttk.Label(search_bars, text="Name:")
        name_search_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        name_search_entry = ttk.Entry(search_bars, textvariable=self._search_params["name"])
        name_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Bar to search for location
        location_search_label = ttk.Label(search_bars, text="Location:")
        location_search_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        location_search_entry = ttk.Entry(search_bars, textvariable=self._search_params["location"])
        location_search_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Buttons to submit search query
        search_button = ttk.Button(search_bars, text="Search", command=self.load_data)
        search_button.grid(row=3, column=0, padx=5, pady=5)
        clear_button = ttk.Button(search_bars, text="Clear", command=self.clear_search)
        clear_button.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ## Create table ##
        table_display = ttk.Frame(self)
        table_display.pack(fill="both", expand=True, padx=10, pady=5)

        # Setup scroll bars
        vertical_scroll = ttk.Scrollbar(table_display, orient="vertical")
        horizontal_scroll = ttk.Scrollbar(table_display, orient="horizontal")

        # Setup treeview as table
        self._table = ttk.Treeview(
            table_display,
            columns=("id", "stock_name", "location_name", "current_quantity"),
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # Ensure the table scrolls when the bar is moved
        vertical_scroll.config(command=self._table.yview)
        horizontal_scroll.config(command=self._table.xview)

        # Setup column headings
        self._table.heading("id", text="ID")
        self._table.heading("stock_name", text="Name")
        self._table.heading("location_name", text="Location")
        self._table.heading("current_quantity", text="Quantity")

        # Setup column appearances
        self._table.column("id",width=50, anchor="center")
        self._table.column("stock_name", width=200)
        self._table.column("location_name", width=200)
        self._table.column("current_quantity", width=50, anchor="center")

        # Place the table and the scrollbars in the frame
        self._table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        # Ensure the table resizes automatically when the window is resized
        table_display.grid_rowconfigure(0,weight=1)
        table_display.grid_columnconfigure(0, weight=1)

        # Create custom behaviour for when a table row is clicked
        self._table.bind("<Double-1>", self.on_double_click)


        ## Create buttons ##
        button_display = ttk.Frame(self)
        button_display.pack(fill="x", padx=10, pady=5)

        # Button to add stock
        add_button = ttk.Button(button_display, text="Add Stock", command=self.add_stock)
        add_button.pack(side="left", padx=5)
        # Button to edit stock
        edit_button = ttk.Button(button_display, text="Edit Stock", command=self.edit_stock)
        edit_button.pack(side="left", padx=5)
        # Button to delete stock
        delete_button = ttk.Button(button_display, text="Delete Stock", command=self.delete_stock)
        delete_button.pack(side="left", padx=5)

    def on_double_click(self):
        self.edit_stock

    def add_stock(self):
        pass
    
    def edit_stock(self):
        pass
    
    def delete_stock(self):
        pass


    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log._msg)
            return

        # Construct an InventoryData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        stock_data = ds.StockData(name=self._search_params["name"]) if self._search_params["name"] else ds.StockData()
        location_data = ds.LocationData(name=self._search_params["location"]) if self._search_params["location"] else ds.LocationData()
        # TODO: Check that the data is valid

        query = ds.InventoryData(stock_type=stock_data, location=location_data)

        # Send it to the database
        try:
            results = self._controller._database.fetch_data(query)
        except Exception as e:
            messagebox.showerror(title="Operation failed", message="Failed to retrieve from database")
            return

        # Delete the current results of the table
        for row in self._table.get_children():
            self._table.delete(row)

        # Display the new results in the table
        for r in results:
            self._table.insert("", "end", values=(
                r["id"],
                r["stock_name"],
                r["location_name"],
                r["current_quantity"]
            ))

    def clear_search(self):
        """
        Clears the search params and then gets all data from the database

        """
        for p in self._search_params:
            p.set("")

        self.load_data()

    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_params(self._search_params)

        self._validity_log.success = True

        stock_name = self._search_params["name"]
        location_name = self._search_params["location"]

        if not valid.is_valid_name(stock_name):
            self._validity_log.error(f"Stock name {stock_name} is invalid")
        
        if not valid.is_valid_name(location_name):
            self._validity_log.error(f"Location name {location_name} is invalid")


class LocationFrame(ttk.Frame):
    def __init__(self, parent, controller):
        pass

class StockFrame(ttk.Frame):
    def __init__(self, parent, controller):
        pass


class LogFrame(ttk.Frame):
    def __init__(self, parent, controller):
        pass

