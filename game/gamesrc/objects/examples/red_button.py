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
import random 
from game.gamesrc.objects.baseobjects import Object
from game.gamesrc.scripts.examples import red_button_scripts as scriptexamples
from game.gamesrc.commands.examples import cmdset_red_button as cmdsetexamples

#
# Definition of the object itself
#
    
class RedButton(Object):
    """
    This class describes an evil red button.
    It will use the script definition in
    game/gamesrc/events/example.py to blink
    at regular intervals until the lightbulb
    breaks. It also use the EventCloselid script to
    close the lid and do nasty stuff when pressed. 
    """
    def at_object_creation(self):
        """
        This function is called when object is created. Use this
        instead of e.g. __init__.
        """        
        # store desc
        desc = "This is a large red button, inviting yet evil-looking. "
        desc += "A closed glass lid protects it." 
        self.db.desc = desc 

        # We have to define all the variables the scripts 
        # are checking/using *before* adding the scripts or 
        # they might be deactivated before even starting! 
        self.db.lid_open = False 
        self.db.lamp_works = True 
        self.db.lid_locked = False

        # set the default cmdset to the object, permanent=True means a 
        # script will automatically be created to always add this. 
        self.cmdset.add_default(cmdsetexamples.DefaultCmdSet, permanent=True)        

        # since the other cmdsets relevant to the button are added 'on the fly',
        # we need to setup custom scripts to do this for us (also, these scripts
        # check so they are valid (i.e. the lid is actually still closed)). 
        # The AddClosedCmdSet script makes sure to add the Closed-cmdset. 
        self.scripts.add(scriptexamples.ClosedLidState)
        # the script EventBlinkButton makes the button blink regularly.
        self.scripts.add(scriptexamples.BlinkButtonEvent)

    # state-changing methods 

    def open_lid(self, feedback=True):
        """
        Open the glass lid and start the timer so it will soon close
        again.
        """

        if self.db.lid_open:
            return 

        desc = "This is a large red button, inviting yet evil-looking. "
        desc += "Its glass cover is open and the button exposed."
        self.db.desc = desc 
        self.db.lid_open = True
        
        if feedback and self.location:
            string =  "The lid slides clear of the button with a click."
            string += "\nA ticking sound is heard, suggesting the lid might have"
            string += " some sort of timed locking mechanism."
            self.location.msg_contents(string)
 
        # with the lid open, we validate scripts; this will clean out
        # scripts that depend on the lid to be closed.
        self.scripts.validate()
        # now add new scripts that define the open-lid state
        self.scripts.add(scriptexamples.OpenLidState)
        # we also add a scripted event that will close the lid after a while.
        # (this one cleans itself after being called once)
        self.scripts.add(scriptexamples.CloseLidEvent)

    def close_lid(self, feedback=True):
        """
        Close the glass lid. This validates all scripts on the button,
        which means that scripts only being valid when the lid is open
        will go away automatically.
        """

        if not self.db.lid_open:
            return         

        desc = "This is a large red button, inviting yet evil-looking. "
        desc += "Its glass cover is closed, protecting it." 
        self.db.desc = desc 
        self.db.lid_open = False        

        if feedback and self.location:
            string = "With a click the lid slides back, securing the button once again."
            self.location.msg_contents(string)

        # clean out scripts depending on lid to be open
        self.scripts.validate()
        # add scripts related to the closed state
        self.scripts.add(scriptexamples.ClosedLidState)

    def break_lamp(self, feedback=True):
        """
        Breaks the lamp in the button, stopping it from blinking.
        
        """
        self.db.lamp_works = False 
        self.db.desc = "The big red button has stopped blinking for the time being."

        if feedback and self.location:
            string = "The lamp flickers, the button going dark."
            self.location.msg_contents(string)        
        self.scripts.validate()

    def press_button(self, pobject):
        """
        Someone was foolish enough to press the button!
        pobject - the person pressing the button
        """
        # deactivate the button so it won't flash/close lid etc.
        self.scripts.add(scriptexamples.DeactivateButtonEvent)
        # blind the person pressing the button. Note that this 
        # script is set on the *character* pressing the button!
        pobject.scripts.add(scriptexamples.BlindedState)

    # script-related methods

    def blink(self):
        """
        The script system will regularly call this
        function to make the button blink. Now and then
        it won't blink at all though, to add some randomness
        to how often the message is echoed. 
        """
        loc = self.location        
        if loc: 
            rand = random.random()
            if rand < 0.2: 
                string = "The red button flashes briefly."
            elif rand < 0.4:
                string = "The red button blinks invitingly."
            elif rand < 0.6:
                string = "The red button flashes. You know you wanna push it!"                
            else:
                # no blink
                return 
            loc.msg_contents(string)

