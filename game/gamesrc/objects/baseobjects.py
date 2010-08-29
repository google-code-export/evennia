"""
These are the base object typeclasses, a convenient shortcut to the
objects in src/objects/objects.py. You can start building your game
from these bases if you want.

To change these defaults to point to some other object, 
change some or all of these variables in settings.py: 
BASE_OBJECT_TYPECLASS 
BASE_CHARACTER_TYPECLASS 
BASE_ROOM_TYPECLASS 
BASE_EXIT_TYPECLASS
BASE_PLAYER_TYPECLASS

Some of the main uses for these settings are not hard-coded in
Evennia, rather they are convenient defaults for in-game commands
(which you may change) Example would be build commands like '@dig'
knowing to create a particular room-type object).

New instances of Objects (inheriting from these typeclasses)
are created with src.utils.create.create_object(typeclass, ...)
where typeclass is the python path to the class you want to use. 
"""
from src.objects.objects import Object as BaseObject
from src.objects.objects import Character as BaseCharacter
from src.objects.objects import Room as BaseRoom
from src.objects.objects import Exit as BaseExit
from src.players.player import Player as BasePlayer

class Object(BaseObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.
    
    Hooks (these are class methods, so their arguments should also start with self): 
     at_object_creation() - only called once, when object is first created.
                            Almost all object customizations go here. 
     at_first_login() - only called once, the very first time user logs in.
     at_pre_login() - called every time the user connects, after they have 
                      identified, just before the system actually logs them in.
     at_post_login() - called at the end of login, just before setting the
                       player loose in the world. 
     at_disconnect() - called just before the use is disconnected (this is also
                       called if the system determines the player lost their link)
     at_object_delete() - called just before the database object is permanently
                          deleted from the database with obj.delete(). Note that cleaning out contents
                          and deleting connected exits is not needed, this is handled
                          automatically when doing obj.delete(). If this method returns
                          False, deletion is aborted. 

     at_before_move(destination) - called by obj.move_to() just before moving object to the destination.
                                   If this method returns False, move is cancelled. 
     announce_move_from(destination) - called while still standing in the old location, 
                                       if obj.move_to() has argument quiet=False. 
     announce_move_to(source_location) - called after move, while standing in the new location
                                       if obj.move_to() has argument quiet=False.
     at_after_move(source_location) - always called after a move has been performed.

     at_object_leave(obj, target_location) - called when this object loose an object (e.g. 
                                             someone leaving the room, an object is given away etc)
     at_object_receive(obj, source_location) - called when this object receives another object
                                             (e.g. a room being entered, an object moved into inventory)

     return_appearance(looker) - by default, this is used by the 'look' command to
                                        request this object to describe itself. Looker
                                        is the object requesting to get the information. 
     at_desc(looker=None) - by default called whenever the appearance is requested.      
     """
    pass

class Character(BaseCharacter):
    """
    This is the default object created for a new user connecting - the
    in-game player character representation. Note that it's important
    that at_object_creation sets up an script that adds the Default
    command set whenever the player logs in - otherwise they won't be
    able to use any commands! 
    """
    def at_object_creation(self):
        # This adds the default cmdset to the player every time they log
        # in. Don't change this unless you really know what you are doing.
        #self.scripts.add(scripts.AddDefaultCmdSet)
        super(Character, self).at_object_creation()

        # expand with whatever customizations you want below...
        # ...
    
class Room(BaseRoom):
    """
    Rooms are like any object, except their location is None
    (which is default). Usually this object should be 
    assigned to room-building commands by use of the 
    settings.BASE_ROOM_TYPECLASS variable.
    """
    pass

class Exit(BaseExit):
    """
    Exits are connectors between rooms. They are identified by the 
    engine by having an attribute "_destination" defined on themselves,
    pointing to a valid room object. That is usually defined when
    the exit is created (in, say, @dig or @link-type commands), not 
    hard-coded in their typeclass. Exits do have to make sure they
    clean up a bit after themselves though, easiest accomplished
    by letting by_object_delete() call the object's parent. 
    """
    def at_object_delete(self):
        """
        The game needs to do some cache cleanups when deleting an exit,
        so we make sure to call super() here. If this method returns
        False, the deletion is aborted.
        """
        # handle some cleanups
        return super(Exit, self).at_object_delete()
        # custom modifications below.
        # ... 


class Player(BasePlayer):
    """
    This class describes the actual OOC player (i.e. the user connecting 
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object. 
    
    It can be useful e.g. for storing configuration options for your game, but 
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_PLAYER_TYPECLASS.

    The following hooks are called by the engine. Note that all of the following 
    are called on the character object too, and mostly at the same time. 

    at_player_creation() - This is called once, the very first time
                  the player is created (i.e. first time they
                  register with the game). It's a good place
                  to store attributes all players should have,
                  like configuration values etc. 
     at_pre_login() - called every time the user connects, after they have 
                      identified, just before the system actually logs them in.
     at_post_login() - called at the end of login, just before setting the
                       player loose in the world. 
     at_disconnect() - called just before the use is disconnected (this is also
                       called if the system determines the player lost their link)

    """
    pass
