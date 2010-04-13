"""
An example script parent for a nice red button object. It has
custom commands defined on itself that are only useful in relation to this
particular object. See example.py in gamesrc/commands for more info
on the pluggable command system. 

Assuming this script remains in gamesrc/parents/examples, create an object
of this type using @create button:examples.red_button

This file also shows the use of the Event system to make the button
send a message to the players at regular intervals. To show the use of
Events, we are tying two types of events to the red button, one which cause ALL
red buttons in the game to blink in sync (gamesrc/events/example.py) and one
event which cause the protective glass lid over the button to close
again some time after it was opened. 

Note that if you create a test button you must drop it before you can
see its messages!
"""
import traceback
from game.models import Object
from src.events import IntervalEvent
from src import scheduler
from src import logger

from django.db import models
from django.contrib.auth.models import User

from src.objects.models import AttributeField

#
# Events
#

# Importing this will start the blink event ticking, only one
# blink event is used for all red buttons.
#import game.gamesrc.events.example 

# We also create an object-specific event.

class EventCloselid(IntervalEvent):
    """
    This event closes the glass lid over the button
    some time after it was opened. 
    """
    def __init__(self, obj):
        """
        Note how we take an object as an argument,
        this will allow instances of this event to
        operate on this object only.
        """
        # we must call super to make sure things work!
        super(EventCloselid, self).__init__()
        # store the object reference
        self.obj_dbref = obj.dbref()
        # This is used in e.g. @ps to show what the event does
        self.description = "Close lid on %s" % obj 
        # We make sure that this event survives a reboot
        self.persistent = True
        # How many seconds from event creation to closing
        # the lid
        self.interval = 20
        # We only run the event one time before it deletes itself.
        self.repeats = 1

    def event_function(self):
        """
        This function is called every self.interval seconds.
        Note that we must make sure to handle all errors from
        this call to avoid trouble. 
        """
        try:
            # if the lid is open, close it. We have to find the object
            # again since it might have changed. 
            obj = Object.objects.get_object_from_dbref(self.obj_dbref)
            if obj.has_flag("LID_OPEN"):
                obj.close_lid()
                retval = "The glass cover over the button silently closes by itself."
                obj.get_location().emit_to_contents(retval)
        except:
            # send the traceback to the log instead of letting it by.
            # It is important that we handle exceptions gracefully here!
            logger.log_errmsg(traceback.print_exc())


#
# Object commands 
#
# Commands for using the button object. These are added to 
# the object in the class_factory function at the
# bottom of this module.
# 

def cmd_open_lid(command):
    """
    Open the glass lid cover over the button.
    """
    # In the case of object commands, you can use this to
    # get the object the command is defined on. 
    obj = command.scripted_obj

    if obj.has_flag("LID_OPEN"):
        retval = "The lid is already open."
    else:
        retval = "You lift the lid, exposing the tempting button."
        obj.open_lid()
    command.source_object.emit_to(retval)

def cmd_close_lid(command):
    """
    Close the lid again.
    """
    obj = command.scripted_obj
    if not obj.has_flag("LID_OPEN"):
        retval = "The lid is already open."
    else:
        retval = "You secure the glass cover over the button."
        obj.close_lid()
    command.source_object.emit_to(retval)

def cmd_push_button(command):
    """

    This is a simple command that handles a user pressing the
    button by returning a message. The button can only be 
    """    
    obj = command.scripted_obj
    
    if obj.has_flag("LID_OPEN"):
        retval = "You press the button ..."
        retval += "\n ..."    
        retval += "\n BOOOOOM!"
        obj.close_lid()
    else:
        retval = "There is a glass lid covering "
        retval += "the button as a safety measure. If you "
        retval += "want to press the button you need to open "
        retval += "the lid first."
    command.source_object.emit_to(retval)
                        

#
# Definition of the object itself
#
    
class RedButton(Object):
    """
    This class describes an evil red button.
    It will use the event definition in
    game/gamesrc/events/example.py to blink
    at regular intervals until the lightbulb
    breaks. It also use the EventCloselid event defined
    above to close the lid 
    """
    class Meta:
        abstract = True
        # gotta figure out a way to set all Objects to this app_label
        app_label = "game"
    desc = AttributeField(default="This is a big red button. It has a glass cover.")
    breakpoint = AttributeField(default=5)
    count = AttributeField(default=0)
    lid_open = AttributeField(default=0)
    
    #pushed = models.BooleanField()
    def at_object_creation(self):
        """
        This function is called when object is created. Use this
        preferably over __init__.
        """        
        # add the object-based commands to the button
        #self.add_command("open lid", cmd_open_lid)
        #self.add_command("lift lid", cmd_open_lid)
        #self.add_command("close lid", cmd_close_lid)        
        #self.add_command("push button", cmd_push_button)
        #self.add_command("push the button", cmd_push_button)
        pass
        
    def open_lid(self):
        """
        Open the glass lid and start the timer so it will
        soon close again. 
        """
        self.lid_open = True
        scheduler.add_event(EventCloselid(self))
    
    def close_lid(self):
        """
        Close the glass lid
        """
        self.lid_open = False

    def blink(self):
        """
        If the event system is active, it will regularly call this
        function to make the button blink. Note the use of attributes
        to store the variable count and breakpoint in a persistent
        way.
        """
        if self.count <= self.breakpoint:
            if self.breakpoint:            
                self.emit("The button flashes, then goes dark.")
            else: 
                self.emit("The red button flashes, demanding your attention.")
            self.count += 1            
