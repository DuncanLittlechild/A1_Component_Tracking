import tkinter as tk
#####################
## Validity checks ##
#####################
# Functions to check that parameters are valid
class ValidityCheck:
    """
    Holds the result of a validity check, and any relevant error messages
    """
    def __init__(self, data=[]):
        self.success = True
        self.msg = ""
        self.data = data

    def error(self, msg: str):
        self._success = False
        if self._msg == "":
            self._msg = msg
        else:
            self._msg += f"; {msg}"

def is_valid_name(name: tk.StringVar)->bool:
    """
    Checks to see if the name is valid
    Names shouldn't include non-alphanumeric characters except for whitespace
    TODO: this will switch to using regexes to ensure that the name follows a logical format
    """
    return all(c.isalnum() or c.isspace() for c in name.get())

def in_database(db: str, param: str, param_name: str, cur) -> bool:
    # Check to see if the name is already in the database
    cur.execute("SELECT * FROM ? WHERE ? = ?", (db, param, param_name))
    return len(cur.fetchall()) > 0

def is_valid_num(num: str) -> bool:
    """
    Checks to see if a number string is valid
    """
    return num.isdigit()

###################
## Normalisation ##
###################
# Functions to normalise input before they are added to the table
def normalise_params(params: dict[str, tk.StringVar]):
    """
    Normalises the search params by making them upper case and removing superfluous whitespace
    """
    for key in params:
        params[key].set(params[key].get().strip().upper())