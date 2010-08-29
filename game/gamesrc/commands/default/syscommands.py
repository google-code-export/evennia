"""
System commands

These are the default commands called by the system commandhandler
when various exceptions occur. If one of these commands are not
implemented and part of the current cmdset, the engine falls back
to a default solution instead. 

Some system commands are shown in this module
as a REFERENCE only (they are not all added to Evennia's 
default cmdset since they don't currently do anything differently from the 
default backup systems hard-wired in the engine).

Overloading these commands in a cmdset can be used to create
interesting effects. An example is using the NoMatch system command
to implement a line-editor where you don't have to start each
line with a command (if there is no match to a known command,
the line is just added to the editor buffer). 
"""
from game.gamesrc.commands.default.muxcommand import MuxCommand
from src.comms.models import Channel
from src.utils import create
from src.permissions.permissions import has_perm

# The command keys the engine is calling
# (the actual names all start with __)
from src.commands.cmdhandler import CMD_NOINPUT
from src.commands.cmdhandler import CMD_NOMATCH
from src.commands.cmdhandler import CMD_MULTIMATCH
from src.commands.cmdhandler import CMD_NOPERM
from src.commands.cmdhandler import CMD_CHANNEL
from src.commands.cmdhandler import CMD_EXIT
 

# Command called when there is no input at line
# (i.e. an lone return key)

class SystemNoInput(MuxCommand):
    """
    This is called when there is no input given
    """
    key = CMD_NOINPUT

    def func(self):
        "Do nothing."
        pass

#
# Command called when there was no match to the
# command name
#

class SystemNoMatch(MuxCommand):
    """
    No command was found matching the given input.
    """
    key = CMD_NOMATCH
    
    def func(self):
        """
        This is given the failed raw string as input.
        """        
        self.caller.msg("Huh?")

#
# Command called when there were mulitple matches to the command.
#
class SystemMultimatch(MuxCommand):
    """
    Multiple command matches
    """
    key = CMD_MULTIMATCH
    
    def func(self):
        """
        argument to cmd is a comma-separated string of
        all the clashing matches.
        """
        self.caller.msg("Multiple matches found:\n %s" % self.args)

class SystemNoPerm(MuxCommand):
    """
    This is called when the user does not have the
    correct permissions to use a particular command.
    """
    key = CMD_NOPERM
    
    def func(self):
        """
        This receives the original raw 
        input string (the one whose command failed to validate)
        as argument. 
        """
        self.caller.msg("You are not allowed to do that.")    


# Command called when the comman given at the command line
# was identified as a channel name, like there existing a
# channel named 'ooc' and the user wrote 
#  > ooc Hello! 

class SystemSendToChannel(MuxCommand):
    """
    This is a special command that the cmdhandler calls
    when it detects that the command given matches
    an existing Channel object key (or alias). 
    """

    key = CMD_CHANNEL
    permissions = "cmd:use_channels"

    def parse(self):
        channelname, msg = self.args.split(':', 1)        
        self.args = channelname.strip(), msg.strip()

    def func(self):
        """
        Create a new message and send it to channel, using
        the already formatted input.
        """        
        caller = self.caller        
        channelkey, msg = self.args
        if not msg:
            caller.msg("Say what?")
            return 
        channel = Channel.objects.get_channel(channelkey)
        if not channel:
            caller.msg("Channel '%s' not found." % channelkey)
            return 
        if not channel.has_connection(caller):
            string = "You are not connected to channel '%s'."
            caller.msg(string % channelkey)
            return
        if not has_perm(caller, channel, 'chan_send'):
            string = "You are not permitted to send to channel '%s'."
            caller.msg(string % channelkey)
            return
        msg = "[%s] %s: %s" % (channel.key, caller.name, msg)        
        msgobj = create.create_message(caller, msg, channels=[channel])
        channel.msg(msgobj)

#
# Command called when the system recognizes the command given
# as matching an exit from the room. E.g. if there is an exit called 'door'
# and the user gives the command
#  > door 
# the exit 'door' should be traversed to its destination.

class SystemUseExit(MuxCommand):
    """
    Handles what happens when user gives a valid exit
    as a command. It receives the raw string as input.
    """
    key = CMD_EXIT

    def func(self):        
        """
        Handle traversing an exit
        """
        caller = self.caller
        if not self.args:
            return
        exit_name = self.args
        exi = caller.search(exit_name)
        if not exi:
            return 
        destination = exi.attr('_destination')
        if not destination:
            return             
        if has_perm(caller, exit, 'traverse'):
            caller.move_to(destination)
        else:
            caller.msg("You cannot enter")
