"""

Template for Objects

Copy this module up one level and name it as you like, then
use it as a template to create your own Objects.

To make the default commands default to creating objects of your new
type (and also change the "fallback" object used when typeclass
creation fails), change settings.BASE_OBJECT_TYPECLASS to point to
your new class, e.g.

settings.BASE_OBJECT_TYPECLASS = "game.gamesrc.objects.myobj.MyObj"

Note that objects already created in the database will not notice
this change, you have to convert them manually e.g. with the
@typeclass command.

"""
from ev import Object

class ExampleObject(Object):
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


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     dbobj (Object, read-only) - link to database model. dbobj.typeclass points back to this class
     typeclass (Object, read-only) - this links back to this class as an identified only. Use self.swap_typeclass() to switch.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     player (Player) - controlling player (will also return offline player)
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     sessions (list of Sessions, read-only) - returns all sessions connected to this object
     has_player (bool, read-only)- will only return *connected* players
     contents (list of Objects, read-only) - returns all objects inside this object (including exits)
     exits (list of Objects, read-only) - returns all exits from this object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, player=False)
     execute_cmd(raw_string)
     msg(message, from_obj=None, data=None)
     msg_contents(message, exclude=None, from_obj=None, data=None)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so their arguments should also start with self):

     basetype_setup()     - only called once, used for behind-the-scenes setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created. Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning False, deletion is aborted. Note that all objects
                          inside a deleted object are automatically moved to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory, at least once every server restart/reload
     at_cmdset_get()      - this is called just before the command handler requests a cmdset from this object
     at_first_login()     - (player-controlled objects only) called once, the very first time user logs in.
     at_pre_login()       - (player-controlled objects only) called every time the user connects, after they have identified, before other setup
     at_post_login()      - (player-controlled objects only) called at the end of login, just before setting the player loose in the world.
     at_disconnect()      - (player-controlled objects only) called just before the user disconnects (or goes linkless)
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_before_move(destination)             - called just before moving object to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives another object

     at_before_traverse(traversing_object)                 - (exit-objects only) called just before an object traverses this object
     at_after_traverse(traversing_object, source_location) - (exit-objects only) called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, data=None) - called when a message (via self.msg()) is sent to this obj.
                                                           If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, data=None) - called when this objects sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look" command by default
     at_desc(looker=None)      - called by 'look' whenever the appearance is requested.
     at_get(getter)            - called after object has been picked up. Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this object speaks

     """
    pass
