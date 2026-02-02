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
        self.header = ""
        self.data = data

    def error(self, msg: str):
        self.success = False
        if self.msg == "":
            self.msg = msg
        else:
            self.msg += f"; {msg}"

    def reset(self):
        self.success = True
        self.msg = ""

class MsgBoxGenerator:
    """
    Returned when database functions error for the purpose of displaying a messagebox
    """
    def __init__(self, title, message):
        self.title = title
        self.message = message

def is_valid_name(name: str)->bool:
    """
    Checks to see if the name is valid
    Names shouldn't include non-alphanumeric characters including whitespace
    """
    return all(c.isalnum() or c.isspace() for c in name)

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
def normalise_stringvar_params(params: dict[str, tk.StringVar]):
    """
    Normalises tk.StringVar search params by making them upper case and removing superfluous whitespace
    """
    for key in params:
        params[key].set(params[key].get().strip().upper())

def normalise_params(params: dict[str, str]):
    """
    Normalises str search params by making them upper case and removing superfluous whitespace
    """
    for key in params:
        params[key] = params[key].strip().upper()
    
    return params