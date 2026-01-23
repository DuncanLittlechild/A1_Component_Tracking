# A1-Component-Tracking
Component tracking system to record the quantity and location of stock instances, as well as flag stock that needs restocking. It uses tkinter to display pages where databases of locations, stock instances, and stock types can have the full range of CRUD operations performed on them. It is verified for python 3.12 onwards, and can run on either windows or linux.

The project stores stock data in instances, which have a stock type, a location, and a quantity. The type and location must already exist in their own databases before an instance can be added - these can be added by selecting the appropriate option on the initial screen. Individual instances can be deleted, but locations and types cannot be deleted if there are any instances that still reference them.


## How to install
1. Download the zip and extract to a location of your choice
2. Open a command line prompt in that folder by typing cmd and enter into the address bar while viewing it in file explorer (windows) or simply by navigating to it from a regular command line propt (linux or windows)
3. Set up a virtual environment using python3 -m venv venv
4. Activate it with "venv\Scripts\activate" (windows) or "source venv/bin/activate" (linux)
5. Install the contents of requirements.txt using the command "pip install -r requirements.txt"
6. Start the program using the command "python3 main.py"