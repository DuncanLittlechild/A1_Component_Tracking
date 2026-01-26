import tkinter as tk
import copy
from tkinter import ttk
from tkinter import messagebox
import data_structures as ds
import utils as valid
from abc import ABC, abstractmethod
from database import Database
###############
## class App ##
###############
# Main Tkinter window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Tracking System")

        self._database = Database()

        self.create_menu_bar()
        
        # set height and width
        self.width = 300
        self.height = 500

        # Get screen height and width
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        #find the offsets needed to centre the window
        offset_x = int(screen_width/2 - self.width / 2)
        offset_y = int(screen_height / 2 - self.height / 2)
    
        # Set the window to the centre of the screen
        self.geometry(f'{self.width}x{self.height}+{offset_x}+{offset_y}')

        # Create container for active frames
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand="true")

        self.show_frame(ChooseFrame)
        # Every time the program is started, the database is checked to see if any items need restocking
        # If they do, an error message is displayed with the names of the relevant stock items
        to_restock = self._database.check_restock()
        if len(to_restock) > 0:
            need_restock_list = [row["name"] for row in to_restock]
            need_restock_str = ";\n".join(need_restock_list)
            messagebox.showwarning(title="Items need restocking!", message=f"The following items need restocking:\n {need_restock_str}")

    def create_menu_bar(self):
        """
        Creates the global app menu bar
        Each command calls the relevant data frame with the necessary datatype
        This ensures that although the fields on the window may look the same,
        the correct database operation is called each time
        """
        menu_bar = tk.Menu(self)

        # Create menu to modify stock and location data
        go_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Go to", menu=go_menu)
        go_menu.add_command(label="Inventory", command=lambda: self.show_frame(InventoryFrame))
        go_menu.add_command(label="Locations", command=lambda: self.show_frame(LocationFrame))
        go_menu.add_command(label="Stock Types", command=lambda: self.show_frame(StockFrame))
        go_menu.add_command(label="Log", command=lambda: self.show_frame(LogFrame))

        self.config(menu=menu_bar)

    # Method to display a new frame of a set class
    def show_frame(self, frame_class: tk.Frame):
        """Remove a prior frame and display a new one of the class frameClass

        Args:
            frameClass (class <ttk.Frame>): the name of the class of the frame
              to be instantiated
        """        
        # Reset the container to the default size
        self.centre_window()
        # Clear the current frame from the container
        for widget in self.container.winfo_children():
            widget.destroy()
        # create a new frame attached to the container
        frame = frame_class(self.container, self)
        # display the new frame
        frame.pack(fill="both", expand="true")

    def centre_window(self, width = None, height = None):
        # Get window height and width
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        # Get screen height and width
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        #find the offsets needed to centre the window
        offset_x = int(screen_width/2 - width / 2)
        offset_y = int(screen_height / 2 - height / 2)
    
        # Set the window to the centre of the screen
        self.geometry(f'{width}x{height}+{offset_x}+{offset_y}')



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

################
## DataFrames ##
################
# Frames to display in the main app window
# These allow the databases to be searched, as well as allowing create, update and delete operations through opening toplevel windows

class DataFrame(ttk.Frame, ABC):
    """
    Base frame to define the set of methods all dataframe must instantiate
    """
    def on_double_click(self, **args):
        """
        Sets behaviour for when a table entry is double clicked
        """
        self.edit_item()
    
    def clear_search(self):
        """
        Clears the search params and then gets all data from the database
        """
        for p in self._search_params:
            self._search_params[p].set("")

        self.load_data()

    def get_selected_item(self):
        """
        Gets the id of the currently selected item on the treeview
        """
        selected = self._table.selection()
        if not selected:
            messagebox.showwarning("No Item Selected", "Choose an item to edit first")
            return None
        item = self._table.item(selected[0])
        return item["values"][0]

    @abstractmethod
    def create_widgets(self):
        """
        Create the widgets for the frame
        """
        pass

    @abstractmethod
    def load_data(self):
        """
        Retreive data from the database, and use it to reconstruct the treeview
        """
        pass

    @abstractmethod
    def valid_params(self):
        """
        Ensure that all parameters are valid
        """
        pass


class InventoryFrame(DataFrame):
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
        clear_button = ttk.Button(search_bars, text="Clear", command=super().clear_search)
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
        self._table.bind("<Double-1>", super().on_double_click)


        ## Create buttons ##
        button_display = ttk.Frame(self)
        button_display.pack(fill="x", padx=10, pady=5)

        # Button to add stock
        add_button = ttk.Button(button_display, text="Add Stock", command=self.add_item)
        add_button.pack(side="left", padx=5)
        # Button to edit stock
        edit_button = ttk.Button(button_display, text="Edit Stock", command=self.edit_item)
        edit_button.pack(side="left", padx=5)
        # Button to delete stock
        delete_button = ttk.Button(button_display, text="Delete Stock", command=self.delete_item)
        delete_button.pack(side="left", padx=5)

    def add_item(self):
        new_window = InventoryPopup(self, self._controller)

        self.wait_window(new_window)

        self.load_data()
    
    def edit_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        inventory_query = ds.InventoryData(id_str=id)

        # Fetch the specific data entry from the database
        try:
            item_data = self._controller._database.fetch_data(inventory_query)
        except:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch item from database")


        inventory_query._location._name = item_data[0]["location"]
        inventory_query._stock_type._name = item_data[0]["stock_name"]
        inventory_query._quantity = item_data[0]["current_quantity"]

        # Open a window to edit the existing data
        new_window = InventoryPopup(self, self._controller, inventory_query)

        # Freeze the main window while the edit window is open
        self.wait_window(new_window)

        # Refresh the data after the edit window closes
        self.load_data()
    
    def delete_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        inventory_query = ds.InventoryData(id_str=id)

        if messagebox.askokcancel(title="Confirm delete", message="This will delete the selected entry. Are you sure?"):
            self._controller._database.delete_data(inventory_query)

        self.load_data()
        
    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        # Construct an InventoryData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        stock_data = ds.StockData(name=self._search_params["name"].get()) if self._search_params["name"].get() != "" else ds.StockData()
        location_data = ds.LocationData(name=self._search_params["location"].get()) if self._search_params["location"].get() != "" else ds.LocationData()

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

    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_stringvar_params(self._search_params)

        self._validity_log.reset()

        stock_name = self._search_params["name"].get()
        location_name = self._search_params["location"].get()

        if not valid.is_valid_name(stock_name):
            self._validity_log.error(f"Stock name {stock_name} is invalid")
        
        if not valid.is_valid_name(location_name):
            self._validity_log.error(f"Location name {location_name} is invalid")


class LocationFrame(DataFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller

        self._search_params = {
            "name": tk.StringVar(),
        }

        self._validity_log = valid.ValidityCheck()

        self.create_widgets()

        self.load_data()

    def create_widgets(self):
        """
        Creates the widgets needed for the location frame
        """
        title_label = ttk.Label(self, text="Locations")
        title_label.pack()

        ## Create search bars ##
        search_bars = ttk.Frame(self)
        search_bars.pack(fill="x", padx=10, pady=5)

        # Bar to search for name
        name_search_label = ttk.Label(search_bars, text="Name:")
        name_search_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        name_search_entry = ttk.Entry(search_bars, textvariable=self._search_params["name"])
        name_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Buttons to submit search query
        search_button = ttk.Button(search_bars, text="Search", command=self.load_data)
        search_button.grid(row=3, column=0, padx=5, pady=5)
        clear_button = ttk.Button(search_bars, text="Clear", command=super().clear_search)
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
            columns=("id", "name"),
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # Ensure the table scrolls when the bar is moved
        vertical_scroll.config(command=self._table.yview)
        horizontal_scroll.config(command=self._table.xview)

        # Setup column headings
        self._table.heading("id", text="ID")
        self._table.heading("name", text="Name")

        # Setup column appearances
        self._table.column("id",width=50, anchor="center")
        self._table.column("name", width=200)

        # Place the table and the scrollbars in the frame
        self._table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        # Ensure the table resizes automatically when the window is resized
        table_display.grid_rowconfigure(0,weight=1)
        table_display.grid_columnconfigure(0, weight=1)

        # Create custom behaviour for when a table row is clicked
        self._table.bind("<Double-1>", super().on_double_click)


        ## Create buttons ##
        button_display = ttk.Frame(self)
        button_display.pack(fill="x", padx=10, pady=5)

        # Button to add stock
        add_button = ttk.Button(button_display, text="Add Location", command=self.add_item)
        add_button.pack(side="left", padx=5)
        # Button to edit stock
        edit_button = ttk.Button(button_display, text="Edit Location", command=self.edit_item)
        edit_button.pack(side="left", padx=5)
        # Button to delete stock
        delete_button = ttk.Button(button_display, text="Delete Location", command=self.delete_item)
        delete_button.pack(side="left", padx=5)

    def add_item(self):
        new_window = LocationPopup(self, self._controller)

        self.wait_window(new_window)

        self.load_data()
    
    def edit_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        location_query = ds.LocationData(id_str=id)

        # Fetch the specific data entry from the database
        try:
            item_data = self._controller._database.fetch_data(location_query)
        except:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch item from database")

        location_query._name = item_data[0]["name"]

        # Open a window to edit the existing data
        new_window = LocationPopup(self, self._controller, location_query)

        # Freeze the main window while the edit window is open
        self.wait_window(new_window)

        # Refresh the data after the edit window closes
        self.load_data()
    
    def delete_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        location_query = ds.LocationData(id_str=id)

        if messagebox.askokcancel(title="Confirm delete", message="This will delete the selected entry. Are you sure?"):
            try:
                self._controller._database.delete_data(location_query)
            except:
                messagebox.showerror(title="Fetch failed", message="Failed to fetch item from database")

        self.load_data()

    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        # Construct an InventoryData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        name = self._search_params["name"].get() if self._search_params["name"].get() != "" else None

        query = ds.LocationData(name=name)

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
                r["name"],
            ))
        
    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_stringvar_params(self._search_params)

        self._validity_log.reset()

        stock_name = self._search_params["name"].get()

        if not valid.is_valid_name(stock_name):
            self._validity_log.error(f"Stock name {stock_name} is invalid")


class StockFrame(DataFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller

        self._search_params = {
            "name": tk.StringVar(),
            "restock_quantity": tk.StringVar()
        }

        self._validity_log = valid.ValidityCheck()

        self.create_widgets()

        self.load_data()

    def create_widgets(self):
        """
        Creates the widgets needed for the stock types frame
        """
        title_label = ttk.Label(self, text="Stock types")
        title_label.pack()

        ## Create search bars ##
        search_bars = ttk.Frame(self)
        search_bars.pack(fill="x", padx=10, pady=5)

        # Bar to search for name
        name_search_label = ttk.Label(search_bars, text="Name:")
        name_search_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        name_search_entry = ttk.Entry(search_bars, textvariable=self._search_params["name"])
        name_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        self._show_restock = tk.BooleanVar()

        restock_checkbox = ttk.Checkbutton(
            search_bars,
            text='Need restock',
            command=self.load_data,
            variable=self._show_restock,
        )
        restock_checkbox.grid(row=1, column=0, padx=5, pady=2)

        # Buttons to submit search query
        search_button = ttk.Button(search_bars, text="Search", command=self.load_data)
        search_button.grid(row=3, column=0, padx=5, pady=5)
        clear_button = ttk.Button(search_bars, text="Clear", command=super().clear_search)
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
            columns=("id", "name", "restock_quantity"),
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # Ensure the table scrolls when the bar is moved
        vertical_scroll.config(command=self._table.yview)
        horizontal_scroll.config(command=self._table.xview)

        # Setup column headings
        self._table.heading("id", text="ID")
        self._table.heading("name", text="Name")
        self._table.heading("restock_quantity", text="Restock quantity")

        # Setup column appearances
        self._table.column("id",width=50, anchor="center")
        self._table.column("name", width=200)
        self._table.column("restock_quantity", width=200)

        # Place the table and the scrollbars in the frame
        self._table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        # Ensure the table resizes automatically when the window is resized
        table_display.grid_rowconfigure(0,weight=1)
        table_display.grid_columnconfigure(0, weight=1)

        # Create custom behaviour for when a table row is clicked
        self._table.bind("<Double-1>", super().on_double_click)

        ## Create buttons ##
        button_display = ttk.Frame(self)
        button_display.pack(fill="x", padx=10, pady=5)

        # Button to add stock type
        add_button = ttk.Button(button_display, text="Add Stock Type", command=self.add_item)
        add_button.pack(side="left", padx=5)
        # Button to edit stock type
        edit_button = ttk.Button(button_display, text="Edit Stock Type", command=self.edit_item)
        edit_button.pack(side="left", padx=5)
        # Button to delete stock type
        delete_button = ttk.Button(button_display, text="Delete Stock Type", command=self.delete_item)
        delete_button.pack(side="left", padx=5)

    def add_item(self):
        new_window = StockPopup(self, self._controller)

        self.wait_window(new_window)

        self.load_data()
    
    def edit_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        stock_query = ds.StockData(id_str=id)
        
        # Fetch the specific data entry from the database
        try:
            item_data = self._controller._database.fetch_data(stock_query)
        except:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch item from database")

        stock_query._name = item_data[0]["name"]
        stock_query._restock_quantity = item_data[0]["restock_quantity"]

        # Open a window to edit the existing data
        new_window = StockPopup(self, self._controller, stock_query)

        # Freeze the main window while the edit window is open
        self.wait_window(new_window)

        # Refresh the data after the edit window closes
        self.load_data()
    
    def delete_item(self):
        id = super().get_selected_item()
        if id is None:
            return
        
        stock_query = ds.StockData(id_str=id)

        if messagebox.askokcancel(title="Confirm delete", message="This will delete the selected entry. Are you sure?"):
            try:
                self._controller._database.delete_data(stock_query)
            except:
                messagebox.showerror(title="Delete failed", message="Failed to delete item from database")

        self.load_data()

    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        # Construct a StockData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        name = self._search_params["name"].get() if self._search_params["name"].get() != "" else None
        
        query = ds.StockData(name=name)

        # Send it to the database
        try:
            results = self._controller._database.fetch_data(query)
            # If the option to only show items that need restocking is on, get the list of items that need restocking, and create a sub-list containing only those values that intersect
            if self._show_restock.get():
                need_restock_dict = self._controller._database.check_restock()
                need_restock_name_set = {stock["id"] for stock in need_restock_dict}
                results = [r for r in results if r["id"] in need_restock_name_set]
        except Exception as e:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch from database")
            return

        # Delete the current results of the table
        for row in self._table.get_children():
            self._table.delete(row)

        # Display the new results in the table
        for r in results:
            self._table.insert("", "end", values=(
                r["id"],
                r["name"],
                r["restock_quantity"]
            ))
        
    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_stringvar_params(self._search_params)

        self._validity_log.reset()

        stock_name = self._search_params["name"].get()
        
        if not valid.is_valid_name(stock_name):
            self._validity_log.error(f"Stock name {stock_name} is invalid")

class QuantityFrame(DataFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller

        self._search_params = {
            "name": tk.StringVar(),
            "location": tk.StringVar()
        }

        self._validity_log = valid.ValidityCheck()

        self.create_widgets()

        self.load_data()

    def create_widgets(self):
        """
        Creates the widgets needed for the stock types frame
        """
        title_label = ttk.Label(self, text="Stock quantities")
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
        
        self._show_restock = tk.BooleanVar()

        restock_checkbox = ttk.Checkbutton(
            search_bars,
            text='Need restock',
            command=self.load_data,
            variable=self._show_restock,
        )
        restock_checkbox.grid(row=2, column=0, padx=5, pady=2)

        # Buttons to submit search query
        search_button = ttk.Button(search_bars, text="Search", command=self.load_data)
        search_button.grid(row=3, column=0, padx=5, pady=5)
        clear_button = ttk.Button(search_bars, text="Clear", command=super().clear_search)
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
            columns=("id", "name", "current_quantity"),
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # Ensure the table scrolls when the bar is moved
        vertical_scroll.config(command=self._table.yview)
        horizontal_scroll.config(command=self._table.xview)

        # Setup column headings
        self._table.heading("id", text="ID")
        self._table.heading("name", text="Name")
        self._table.heading("current_quantity", text="Current quantity")

        # Setup column appearances
        self._table.column("id",width=50, anchor="center")
        self._table.column("name", width=200)
        self._table.column("current_quantity", width=200)

        # Place the table and the scrollbars in the frame
        self._table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        # Ensure the table resizes automatically when the window is resized
        table_display.grid_rowconfigure(0,weight=1)
        table_display.grid_columnconfigure(0, weight=1)

        ## Create buttons ##
        button_display = ttk.Frame(self)
        button_display.pack(fill="x", padx=10, pady=5)

    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        # Construct a QuantityData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        name = self._search_params["name"].get() if self._search_params["name"].get() != "" else None
        
        query = ds.QuantityData(name=name)

        # Send it to the database
        try:
            results = self._controller._database.fetch_data(query)
            # If the option to only show items that need restocking is on, get the list of items that need restocking, and create a sub-list containing only those values that intersect
            if not self._show_restock.get():
                need_restock_dict = self._controller._database.check_restock()
                need_restock_name_set = {stock["id"] for stock in need_restock_dict}
                results = [r for r in results if r["id"] in need_restock_name_set]
        except Exception as e:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch from database")
            return

        # Delete the current results of the table
        for row in self._table.get_children():
            self._table.delete(row)

        # Display the new results in the table
        for r in results:
            self._table.insert("", "end", values=(
                r["id"],
                r["name"],
                r["total_quantity"]
            ))
        
    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_stringvar_params(self._search_params)

        self._validity_log.reset()

        name = self._search_params["name"].get()
        location=self._search_params["location"].get()
        
        if not valid.is_valid_name(name):
            self._validity_log.error(f"Stock name {name} is invalid")

        if not valid.is_valid_name(location):
            self._validity_log.error(f"Location name {location} is invalid")
        

class LogFrame(DataFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller

        self._search_params = {
            "name": tk.StringVar(),
        }

        self._validity_log = valid.ValidityCheck()

        self.create_widgets()

        self.load_data()

    def create_widgets(self):
        """
        Creates the widgets needed for the stock types frame
        """
        title_label = ttk.Label(self, text="Activity logs")
        title_label.pack()

        ## Create search bars ##
        search_bars = ttk.Frame(self)
        search_bars.pack(fill="x", padx=10, pady=5)

        # Bar to search for name
        name_search_label = ttk.Label(search_bars, text="Stock Name:")
        name_search_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        name_search_entry = ttk.Entry(search_bars, textvariable=self._search_params["name"])
        name_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Buttons to submit search query
        search_button = ttk.Button(search_bars, text="Search", command=self.load_data)
        search_button.grid(row=1, column=0, padx=5, pady=5)
        clear_button = ttk.Button(search_bars, text="Clear", command=super().clear_search)
        clear_button.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ## Create table ##
        table_display = ttk.Frame(self)
        table_display.pack(fill="both", expand=True, padx=10, pady=5)

        # Setup scroll bars
        vertical_scroll = ttk.Scrollbar(table_display, orient="vertical")
        horizontal_scroll = ttk.Scrollbar(table_display, orient="horizontal")

        # Setup treeview as table
        self._table = ttk.Treeview(
            table_display,
            columns=("id", "stock_name", "location_name", "activity_type", "update_details", "date_occurred"),
            show="headings",
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # Ensure the table scrolls when the bar is moved
        vertical_scroll.config(command=self._table.yview)
        horizontal_scroll.config(command=self._table.xview)

        # Setup column headings
        self._table.heading("id", text="ID")
        self._table.heading("stock_name", text="Stock Name")
        self._table.heading("location_name", text="Location Name")
        self._table.heading("activity_type", text="Activity Type")
        self._table.heading("update_details", text="Update details")
        self._table.heading("date_occurred", text="Date Occurred")

        # Setup column appearances
        self._table.column("id",width=50, anchor="center")
        self._table.column("stock_name", width=200)
        self._table.column("location_name", width=200)
        self._table.column("activity_type", width=200)
        self._table.column("update_details", width=200)
        self._table.column("date_occurred", width=200)

        # Place the table and the scrollbars in the frame
        self._table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        # Ensure the table resizes automatically when the window is resized
        table_display.grid_rowconfigure(0,weight=1)
        table_display.grid_columnconfigure(0, weight=1)

    def load_data(self):
        """
        Loads data from the database according to the search parameters and updates the table
        """
        # Check that the inputted data is valid
        self.valid_params()
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        # Construct a StockData object
        # If no params are given, a blank object will be generated, which will return all possible datapoints
        name = self._search_params["name"].get() if self._search_params["name"].get() != "" else None
        
        query = ds.LogData(stock_name=name)

        # Send it to the database
        try:
            results = self._controller._database.fetch_data(query)
        except Exception as e:
            messagebox.showerror(title="Fetch failed", message="Failed to fetch from database")
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
                r["activity_type"],
                r["update_details"],
                r["date_occurred"]
            ))
        
    def valid_params(self):
        """
        Checks the search params to make sure they are valid
        """
        valid.normalise_stringvar_params(self._search_params)

        self._validity_log.success = True

        stock_name = self._search_params["name"].get()
        
        if not valid.is_valid_name(stock_name):
            self._validity_log.error(f"Stock name {stock_name} is invalid")

###############
## TopLevels ##
###############
# Toplevels to allow databases to be edited and added to

class Popup(tk.Toplevel, ABC):
    """
    Base frame to define all the methods other toplevel popup windows must implement
    """
    @abstractmethod
    def create_widgets(self):
        """
        Creates widgets to display the relevant data
        """
        pass

    @abstractmethod
    def populate_fields(self):
        """
        If data is provided, populates the relevant fields with this data
        """
        pass

    @abstractmethod
    def edit_or_create(self, database_method):
        """
        Constructs the relevant data object using inputted and existing information, then sends it to Database.update_data
        """
        pass

    @abstractmethod
    def valid_params(self):
        """
        Normalises the relevant data, then checks to make sure it is all valid
        """
        pass

class InventoryPopup(Popup):
    """
    Toplevel window that allows users to either add to or edit items in the current_inventory db
    """
    def __init__(self, parent: tk.Tk, controller, inventory_data: ds.InventoryData = None):
        super().__init__(parent)
        self._controller = controller

        self._validity_log = valid.ValidityCheck()

        # If inventory_data is None, then this is in create mod. Otherwise, it is in edit mode
        self._inventory_data = inventory_data

        if inventory_data:
            self.title("Edit stock instance")
        else:
            self.title("Create stock instance")

        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        if inventory_data:
            self.populate_fields()

    def create_widgets(self):
        ttk.Label(self, text="Stock Instance").pack(pady=10)
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="both", expand=True, padx=5, pady=10)

        name_label = tk.Label(entry_frame, text="Name:")
        name_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)

        self._name_var = tk.StringVar()

        name_entry = ttk.Entry(entry_frame, textvariable=self._name_var, width=30)

        # If we are editing, we should not be able to edit the type of stock
        if self._inventory_data:
            name_entry.config(state="disabled")

        name_entry.grid(row=0, column=1, padx=10, pady=5)

        location_label = tk.Label(entry_frame, text="Location:")
        location_label.grid(row=1, column=0, sticky="e", padx=10, pady=5)

        self._location = tk.StringVar()

        location_entry = ttk.Entry(entry_frame, textvariable=self._location, width=30)
        location_entry.grid(row=1, column=1, padx=10, pady=5)

        # If we are editing, have seperate boxes for the old and new locations
        # This makes it easy to compare old and new spellings
        # Quantity can also only be set in an update, as initial quantity is linked to the stock type
        if self._inventory_data:
            location_entry.config(state="disabled")
            self._new_location = tk.StringVar()

            new_location_label = tk.Label(entry_frame, text="New Location:")
            new_location_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

            new_location_entry = ttk.Entry(entry_frame, textvariable=self._new_location, width=30)
            new_location_entry.grid(row=2, column=1, padx=10, pady=5)

        quantity_label = tk.Label(entry_frame, text="Quantity:")
        quantity_label.grid(row=3, column=0, sticky="e", padx=10, pady=5)

        self._current_quantity = tk.StringVar()

        quantity_entry = ttk.Entry(entry_frame, textvariable=self._current_quantity, width=30)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5)

        # Have a seperate box for the previous quantity
        if self._inventory_data:
            quantity_entry.config(state="disabled")

            self._new_quantity = tk.StringVar()

            quantity_label = tk.Label(entry_frame, text="New Quantity:")
            quantity_label.grid(row=4, column=0, sticky="e", padx=10, pady=5)

            quantity_entry = ttk.Entry(entry_frame, textvariable=self._new_quantity, width=30)
            quantity_entry.grid(row=4, column=1, padx=10, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", expand=True, padx=10, pady=10)

        # Create buttons with different labels depending on if data has been given
        if self._inventory_data:
            submit_btn = ttk.Button(btn_frame, text="Edit", command=lambda: self.edit_or_create(self._controller._database.update_data))
        else:
            submit_btn = ttk.Button(btn_frame, text="Create", command=lambda: self.edit_or_create(self._controller._database.add_data))
        
        submit_btn.pack(side="left", padx=5)

        # Create exit button
        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.destroy).pack(side="left", padx=5)

    def populate_fields(self):
        """
        If data was passed to this topwindow on creation, populate the entry fields with the relevant data
        """
        # Check just in case this function is accidentally called from the wrong place
        if not self._inventory_data:
            return None
        name = self._inventory_data._stock_type._name
        location = self._inventory_data._location._name
        quantity = self._inventory_data._quantity

        self._name_var.set(name)
        self._location.set(location)
        self._new_location.set(location)
        self._current_quantity.set(quantity)
        self._new_quantity.set(quantity)


    def edit_or_create(self, database_method):
        """
        Uses given data to edit or create an existing database entry depending on the window's function
        """
        if self._inventory_data:
            self._query = copy.deepcopy(self._inventory_data)
            self._query._location._name = self._new_location.get()
            self._query._quantity = self._new_quantity.get()
        else:
            self._query = ds.InventoryData()
            self._query._location._name = self._location.get()
            self._query._quantity = self._current_quantity.get()

        self._query._stock_type._name = self._name_var.get()
        
        self.valid_params()
        
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        try:
            database_method(self._query)
        except:
            messagebox.showerror(title="Database Error", message="Unable to update database")
    

    def valid_params(self):
        """
        Checks to make sure all parameters are valid, and logs all invalid parameters
        """
        self._validity_log.reset()
        normalised_params = valid.normalise_params({"name": self._query._stock_type._name, "location": self._query._location._name, "current_quantity": self._query._quantity})

        name = normalised_params["name"]
        location = normalised_params["location"]
        current_quantity = normalised_params["current_quantity"]

        self._query._stock_type._name = name
        self._query._location._name = location
        self._query._quantity = current_quantity

        # Check that all values are formatted correctly
        if not valid.is_valid_name(name):
            self._validity_log.error(f"Stock name {name} is invalid")
        
        if not valid.is_valid_name(location):
            self._validity_log.error(f"Location name {location} is invalid")

        if not valid.is_valid_num(current_quantity):
            self._validity_log.error(f"Quantity entered is invalid")

        # Check that the name of the stock type is in the database
        name_exists = self._controller._database.fetch_data(ds.StockData(name=name))

        if len(name_exists) == 0:
            self._validity_log.error("Stock name not found in database")

        # check that the name of the location is in the database
        location_exists = self._controller._database.fetch_data(ds.LocationData(name=location))

        if len(location_exists) == 0:
            self._validity_log.error("Location not found in database")


class LocationPopup(Popup):
    """
    Toplevel window that allows users to either add to or edit items in the location_data db
    """
    def __init__(self, parent: tk.Tk, controller, location_data: ds.LocationData = None):
        super().__init__(parent)
        self._controller = controller

        self._validity_log = valid.ValidityCheck()

        # If location_data is None, then this is in create mod. Otherwise, it is in edit mode
        self._location_data = location_data

        if location_data:
            self.title("Edit location")
        else:
            self.title("Create location")

        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        if location_data:
            self.populate_fields()

    def create_widgets(self):
        ttk.Label(self, text="Location").pack(pady=10)
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="both", expand=True, padx=5, pady=10)

        name_label = tk.Label(entry_frame, text="Name:")
        name_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)

        self._name_var = tk.StringVar()

        name_entry = ttk.Entry(entry_frame, textvariable=self._name_var, width=30)
        
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        if self._location_data:
            name_entry.config(state="disabled")
            self._new_name = tk.StringVar()

            new_name_label = tk.Label(entry_frame, text="New Name:")
            new_name_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

            new_name_entry = ttk.Entry(entry_frame, textvariable=self._new_name, width=30)
            new_name_entry.grid(row=2, column=1, padx=10, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", expand=True, padx=10, pady=10)

        # Create buttons with different labels depending on if data has been given
        if self._location_data:
            submit_btn = ttk.Button(btn_frame, text="Edit", command=lambda: self.edit_or_create(self._controller._database.update_data))
        else:
            submit_btn = ttk.Button(btn_frame, text="Create", command=lambda: self.edit_or_create(self._controller._database.add_data))
        
        submit_btn.pack(side="left", padx=5)

        # Create exit button
        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.destroy).pack(side="left", padx=5)

    def populate_fields(self):
        """
        If data was passed to this topwindow on creation, populate the entry fields with the relevant data
        """
        # Check just in case this function is accidentally called from the wrong place
        if not self._location_data:
            return None
        name = self._location_data._name

        self._name_var.set(name)
        self._new_name.set(name)

    def edit_or_create(self, database_method):
        """
        Uses given data to edit or create an existing database entry depending on the window's function
        """
        if self._location_data:
            self._query = copy.deepcopy(self._location_data)
            self._query._name = self._new_name.get()
        else:
            self._query = ds.LocationData()
            self._query._name = self._name_var.get()
        
        self.valid_params()
        
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return
        
        try:
            database_method(self._query)
        except:
            messagebox.showerror(title="Database Error", message="Unable to update database")
    
    def valid_params(self):
        """
        Checks to make sure all parameters are valid, and logs all invalid parameters
        """
        self._validity_log.reset()
        
        normalised_params = valid.normalise_params({"name": self._query._name})
        name = normalised_params["name"]

        self._query._name = name

        # Check that all values are formatted correctly
        if not valid.is_valid_name(name):
            self._validity_log.error(f"Location name {name} is invalid")


class StockPopup(Popup):
    """
    Toplevel window that allows users to either add to or edit items in the stock_data db
    """
    def __init__(self, parent: tk.Tk, controller, stock_data: ds.StockData = None):
        super().__init__(parent)
        self._controller = controller

        self._validity_log = valid.ValidityCheck()

        # If stock_data is None, then this is in create mod. Otherwise, it is in edit mode
        self._stock_data = stock_data

        if stock_data:
            self.title("Edit stock")
        else:
            self.title("Create stock")

        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        if stock_data:
            self.populate_fields()

    def create_widgets(self):
        ttk.Label(self, text="Stock").pack(pady=10)
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="both", expand=True, padx=5, pady=10)

        name_label = tk.Label(entry_frame, text="Name:")
        name_label.grid(row=0, column=0, sticky="e", padx=10, pady=5)

        self._name_var = tk.StringVar()

        name_entry = ttk.Entry(entry_frame, textvariable=self._name_var, width=30)
        
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        if self._stock_data:
            name_entry.config(state="disabled")
            self._new_name = tk.StringVar()

            new_name_label = tk.Label(entry_frame, text="New Name:")
            new_name_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

            new_name_entry = ttk.Entry(entry_frame, textvariable=self._new_name, width=30)
            new_name_entry.grid(row=2, column=1, padx=10, pady=5)

        restock_label = tk.Label(entry_frame, text="Restock level:")
        restock_label.grid(row=3, column=0, sticky="e", padx=10, pady=5)

        self._restock_quantity = tk.StringVar()

        restock_entry = ttk.Entry(entry_frame, textvariable=self._restock_quantity, width=30)
        
        restock_entry.grid(row=3, column=1, padx=10, pady=5)

        if self._stock_data:
            restock_entry.config(state="disabled")
            self._new_restock = tk.StringVar()

            new_restock_label = tk.Label(entry_frame, text="New restock level:")
            new_restock_label.grid(row=2, column=0, sticky="e", padx=10, pady=5)

            new_restock_entry = ttk.Entry(entry_frame, textvariable=self._new_restock, width=30)
            new_restock_entry.grid(row=2, column=1, padx=10, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", expand=True, padx=10, pady=10)

        # Create buttons with different labels depending on if data has been given
        if self._stock_data:
            submit_btn = ttk.Button(btn_frame, text="Edit", command=lambda: self.edit_or_create(self._controller._database.update_data))
        else:
            submit_btn = ttk.Button(btn_frame, text="Create", command=lambda: self.edit_or_create(self._controller._database.add_data))
        
        submit_btn.pack(side="left", padx=5)

        # Create exit button
        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.destroy).pack(side="left", padx=5)

    def populate_fields(self):
        """
        If data was passed to this topwindow on creation, populate the entry fields with the relevant data
        """
        # Check just in case this function is accidentally called from the wrong place
        if not self._stock_data:
            return None
        name = self._stock_data._name
        restock_quantity = self._stock_data._restock_quantity

        self._name_var.set(name)
        self._new_name.set(name)
        self._restock_quantity.set(restock_quantity)
        self._new_restock.set(restock_quantity)

    def edit_or_create(self, database_method):
        """
        Uses given data to edit or create an existing database entry depending on the window's function
        """
        if self._stock_data:
            self._query = copy.deepcopy(self._stock_data)
            self._query._name = self._new_name.get()
            self._query._restock_quantity = self._new_restock.get()
        else:
            self._query = ds.StockData()
            self._query._name = self._name_var.get()
            self._query._restock_quantity = self._restock_quantity.get()
        
        self.valid_params()
        
        if not self._validity_log.success:
            messagebox.showerror(title="Invalid Parameters", message=self._validity_log.msg)
            return

        try:
            database_method(self._query)
        except:
            messagebox.showerror(title="Database Error", message="Unable to update database")
    
    def valid_params(self):
        """
        Checks to make sure all parameters are valid, and logs all invalid parameters
        """
        self._validity_log.reset()
        
        normalised_params = valid.normalise_params({"name": self._query._name, "restock_quantity": self._query._restock_quantity})
        name = normalised_params["name"]
        restock_quantity = normalised_params["restock_quantity"]

        self._query._name = name
        self._query._restock_quantity = restock_quantity

        # Check that all values are formatted correctly
        if not valid.is_valid_name(name):
            self._validity_log.error(f"Stock name {name} is invalid")

        if not valid.is_valid_num(restock_quantity):
            self._validity_log.error(f"Restock quantity {restock_quantity} is invalid")
