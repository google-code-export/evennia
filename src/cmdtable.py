"""
Command Table Module
---------------------
Each command entry consists of a key and a tuple containing a reference to the
command's function, and a tuple of the permissions to match against. The user
only need have one of the permissions in the permissions tuple to gain
access to the command. Obviously, super users don't have to worry about this
stuff. If the command is open to all (or you want to implement your own
privilege checking in the command function), use None in place of the
permissions tuple.

Commands are located under evennia/src/commands. server.py imports these
based on the value of settings.COMMAND_MODULES and 
settings.CUSTOM_COMMAND_MODULES. Each module imports cmdtable.py and runs
add_command on the command table each command belongs to.
"""

class CommandTable(object):
    """
    Stores command tables and performs lookups.
    """
    ctable = None
    
    def __init__(self):
        # This ensures there are no leftovers when the class is instantiated.
        self.ctable = {}
    
    def add_command(self, command_string, function, priv_tuple=None,
                    extra_vals=None):
        """
        Adds a command to the command table.
        
        command_string: (string) Command string (IE: WHO, QUIT, look).
        function: (reference) The command's function.
        priv_tuple: (tuple) String tuple of permissions required for command.
        extra_vals: (dict) Dictionary to add to the Command object.
        """
        self.ctable[command_string] = (function, priv_tuple, extra_vals)
        
    def get_command_tuple(self, func_name):
        """
        Returns a reference to the command's tuple. If there are no matches,
        returns false.
        """
        return self.ctable.get(func_name, False)

"""
Command tables
"""
# Global command table, for authenticated users.
GLOBAL_CMD_TABLE = CommandTable()
# Global unconnected command table, for unauthenticated users.
GLOBAL_UNCON_CMD_TABLE = CommandTable()