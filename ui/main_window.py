import tkinter as tk
from tkinter import ttk
from database import Database
from ui.frames import ChooseFrame, InventoryFrame, LocationFrame, StockFrame, LogFrame


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

    def show_popup(self, frame_class: tk.Frame, title: str):
        new_window = PopupWindow(self, frame_class, title)

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


#######################
## class PopupWindow ##
#######################
# A popup window designed to be a blank container for frames

class PopupWindow(tk.Toplevel):
    """
    Toplevel window that functions exactly like the base window, but smaller.
    It's purpose is to allow frames designed for the base window to be easily displayed as new windows
    """
    def __init__(self, parent, frame_class: type, title):
        super().__init__(parent)
        self.title = title
        self.geometry("400x300")

        # Create container for active frames
        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

        # As popups never need to switch frame, showframe is effectively run here
        frame = frame_class(self._container, self)
        frame.pack(fill="both", expand=True)