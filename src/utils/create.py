"""
This module gathers all the essential database-creation
methods for the game engine's various object types.
Only objects created 'stand-alone' are in here,
e.g. object Attributes are always created directly through their
respective objects.

The respective object managers hold more methods for
manipulating and searching objects already existing in
the database. 

Models covered: 
 Objects
 Scripts
 Help
 Message
 Channel 
 Players
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from src.utils.idmapper.models import SharedMemoryModel
from src.utils import logger, utils, idmapper
from src.utils.utils import is_iter, has_parent, inherits_from

#
# Game Object creation 
#

def create_object(typeclass, key=None, location=None,
                  home=None, player=None, permissions=None, locks=None, 
                  aliases=None, destination=None):
    """
    Create a new in-game object. Any game object is a combination
    of a database object that stores data persistently to
    the database, and a typeclass, which on-the-fly 'decorates'
    the database object into whataver different type of object
    it is supposed to be in the game. 

    See src.objects.managers for methods to manipulate existing objects
    in the database. src.objects.objects holds the base typeclasses
    and src.objects.models hold the database model. 
    """
    # deferred import to avoid loops
    from src.objects.objects import Object
    from src.objects.models import ObjectDB

    if not typeclass:
        typeclass = settings.BASE_OBJECT_TYPECLASS
    elif isinstance(typeclass, ObjectDB):
        # this is already an objectdb instance, extract its typeclass
        typeclass = typeclass.typeclass.path
    elif isinstance(typeclass, Object) or utils.inherits_from(typeclass, Object):
        # this is already an object typeclass, extract its path
        typeclass = typeclass.path         

    # create new database object 
    new_db_object = ObjectDB()
    
    # assign the typeclass 
    typeclass = utils.to_unicode(typeclass)
    new_db_object.typeclass_path = typeclass

    # the name/key is often set later in the typeclass. This
    # is set here as a failsafe. 
    if key:
        new_db_object.key = key 
    else:
        new_db_object.key = "#%i" % new_db_object.id

    # this will either load the typeclass or the default one
    new_object = new_db_object.typeclass


    if not object.__getattribute__(new_db_object, "is_typeclass")(typeclass, exact=True):
        # this will fail if we gave a typeclass as input and it still gave us a default
        SharedMemoryModel.delete(new_db_object)
        return None 

    # from now on we can use the typeclass object 
    # as if it was the database object.

    if player:
        # link a player and the object together
        new_object.player = player
        player.obj = new_object

    new_object.destination = destination 

    # call the hook method. This is where all at_creation
    # customization happens as the typeclass stores custom
    # things on its database object. 
    new_object.basetype_setup() # setup the basics of Exits, Characters etc.
    new_object.at_object_creation()
    
    # custom-given perms/locks overwrite hooks
    if permissions:
        new_object.permissions = permissions
    if locks:
        new_object.locks.add(locks)
    if aliases:
        new_object.aliases = aliases

    # perform a move_to in order to display eventual messages.
    if home:
        new_object.home = home
    else:
        new_object.home = settings.CHARACTER_DEFAULT_HOME

                
    if location:
        new_object.move_to(location, quiet=True)
    else:
        # rooms would have location=None.
        new_object.location = None                             

    # post-hook setup (mainly used by Exits)
    new_object.basetype_posthook_setup()    

    new_object.save()
    return new_object

#
# Script creation 
#

def create_script(typeclass, key=None, obj=None, locks=None, autostart=True):
    """
    Create a new script. All scripts are a combination
    of a database object that communicates with the
    database, and an typeclass that 'decorates' the
    database object into being different types of scripts.
    It's behaviour is similar to the game objects except
    scripts has a time component and are more limited in
    scope. 

    Argument 'typeclass' can be either an actual
    typeclass object or a python path to such an object.
    Only set key here if you want a unique name for this
    particular script (set it in config to give
    same key to all scripts of the same type). Set obj
    to tie this script to a particular object. 

    See src.scripts.manager for methods to manipulate existing
    scripts in the database.
    """

    # deferred import to avoid loops.
    from src.scripts.scripts import Script
    #print "in create_script", typeclass    
    from src.scripts.models import ScriptDB    

    if not typeclass:
        typeclass = settings.BASE_SCRIPT_TYPECLASS
    elif isinstance(typeclass, ScriptDB):
        # this is already an scriptdb instance, extract its typeclass
        typeclass = new_db_object.typeclass.path
    elif isinstance(typeclass, Script) or utils.inherits_from(typeclass, Script):
        # this is already an object typeclass, extract its path
        typeclass = typeclass.path 

    # create new database script
    new_db_script = ScriptDB()    

    # assign the typeclass 
    typeclass = utils.to_unicode(typeclass)
    new_db_script.typeclass_path = typeclass
    
    # the name/key is often set later in the typeclass. This
    # is set here as a failsafe. 
    if key:
        new_db_script.key = key
    else:
        new_db_script.key = "#%i" % new_db_script.id

    # this will either load the typeclass or the default one
    new_script = new_db_script.typeclass

    if not object.__getattribute__(new_db_script, "is_typeclass")(typeclass, exact=True):
        # this will fail if we gave a typeclass as input and it still gave us a default
        print "failure:", new_db_script, typeclass
        SharedMemoryModel.delete(new_db_script)
        return None 

    if obj:
        try:
            new_script.obj = obj
        except ValueError:
            new_script.obj = obj.dbobj    

    # call the hook method. This is where all at_creation
    # customization happens as the typeclass stores custom
    # things on its database object.
    new_script.at_script_creation()

    # custom-given variables override the hook
    if key:
        new_script.key = key 

    if locks:
        new_script.locks.add(locks)

    # a new created script should usually be started.
    if autostart:
        new_script.start()
    
    new_db_script.save()
    return new_script 

#
# Help entry creation
#

def create_help_entry(key, entrytext, category="General", locks=None):
    """
    Create a static help entry in the help database. Note that Command
    help entries are dynamic and directly taken from the __doc__ entries
    of the command. The database-stored help entries are intended for more
    general help on the game, more extensive info, in-game setting information
    and so on. 
    """

    from src.help.models import HelpEntry
    try:
        new_help = HelpEntry()
        new_help.key = key
        new_help.entrytext = entrytext
        new_help.help_category = category
        if locks:
            new_help.locks.add(locks)
        new_help.save()
        return new_help 
    except IntegrityError:
        string = "Could not add help entry: key '%s' already exists." % key
        logger.log_errmsg(string)
        return None
    except Exception:
        logger.log_trace()
        return None 


#
# Comm system methods 
#

def create_message(senderobj, message, channels=None,
                   receivers=None, locks=None):
    """
    Create a new communication message. Msgs are used for all
    player-to-player communication, both between individual players
    and over channels.
    senderobj - the player sending the message. This must be the actual object.
    message - text with the message. Eventual headers, titles etc
              should all be included in this text string. Formatting
              will be retained. 
    channels - a channel or a list of channels to send to. The channels
             may be actual channel objects or their unique key strings.
    receivers - a player to send to, or a list of them. May be Player objects
               or playernames.
    locks - lock definition string

    The Comm system is created very open-ended, so it's fully possible
    to let a message both go to several channels and to several receivers
    at the same time, it's up to the command definitions to limit this as
    desired. 
    """
    from src.comms.models import Msg
    from src.comms.managers import to_object

    def to_player(obj):
        "Make sure the object is a player object"
        if hasattr(obj, 'user'):
            return obj
        elif hasattr(obj, 'player'):
            return obj.player
        else:
            return None 

    if not message:
        # we don't allow empty messages. 
        return

    new_message = Msg()
    new_message.sender = to_player(senderobj)
    new_message.message = message
    new_message.save()
    if channels:
        if not is_iter(channels):
            channels = [channels]
        new_message.channels = [channel for channel in
                                [to_object(channel, objtype='channel')
                                 for channel in channels] if channel] 
    if receivers:
        #print "Found receiver:", receivers
        if not is_iter(receivers):
            receivers = [receivers]
        #print "to_player: %s" % to_player(receivers[0])
        new_message.receivers = [to_player(receiver) for receiver in
                                 [to_object(receiver) for receiver in receivers]
                                 if receiver] 
    if locks:
        new_message.locks.add(locks)
    new_message.save()
    return new_message

def create_channel(key, aliases=None, desc=None,
                   locks=None, keep_log=True):
    """
    Create A communication Channel. A Channel serves as a central
    hub for distributing Msgs to groups of people without
    specifying the receivers explicitly. Instead players may
    'connect' to the channel and follow the flow of messages. By
    default the channel allows access to all old messages, but
    this can be turned off with the keep_log switch. 

    key - this must be unique. 
    aliases - list of alternative (likely shorter) keynames.
    locks - lock string definitions
    """

    from src.comms.models import Channel 
    from src.comms import channelhandler 
    try:
        new_channel = Channel()
        new_channel.key = key 
        if aliases:
            if not is_iter(aliases):
                aliases = [aliases]
            new_channel.aliases = ",".join([alias for alias in aliases])
        new_channel.desc = desc
        new_channel.keep_log = keep_log
    except IntegrityError:
        string = "Could not add channel: key '%s' already exists." % key
        logger.log_errmsg(string)
        return None
    if locks:
        new_channel.locks.add(locks)
    new_channel.save()
    channelhandler.CHANNELHANDLER.add_channel(new_channel)
    return new_channel 
    
#
# Player creation methods 
#

def create_player(name, email, password,
                  user=None,
                  typeclass=None,
                  is_superuser=False, 
                  locks=None, permissions=None,
                  create_character=True, character_typeclass=None,
                  character_location=None, character_home=None):                   

    
    """
    This creates a new player, handling the creation of the User
    object and its associated Player object. 
    
    If create_character is
    True, a game player object with the same name as the User/Player will
    also be created. Its typeclass and base properties can also be given.

    Returns the new game character, or the Player obj if no
    character is created.  For more info about the typeclass argument,
    see create_objects() above.
    
    Note: if user is supplied, it will NOT be modified (args name, email, 
    passw and is_superuser will be ignored). Change those properties 
    directly on the User instead. 

    If no permissions are given (None), the default permission group
    as defined in settings.PERMISSION_PLAYER_DEFAULT will be 
    assigned. If permissions are given, no automatic assignment will
    occur. 

    Concerning is_superuser:
     A superuser should have access to everything
     in the game and on the server/web interface. The very first user
     created in the database is always a superuser (that's using
     django's own creation, not this one).
     Usually only the server admin should need to be superuser, all
     other access levels can be handled with more fine-grained
     permissions or groups. 
     Since superuser overrules all permissions, we don't
     set any in this case.
    
    """
    # The system should already have checked so the name/email
    # isn't already registered, and that the password is ok before
    # getting here. 

    from src.players.models import PlayerDB
    from src.players.player import Player

    if not email:
        email = "dummy@dummy.com"
    if user:
        new_user = user
    else:
        if is_superuser:
            new_user = User.objects.create_superuser(name, email, password)
        else:
            new_user = User.objects.create_user(name, email, password) 

    try:
        if not typeclass:
            typeclass = settings.BASE_PLAYER_TYPECLASS
        elif isinstance(typeclass, PlayerDB):
            # this is already an objectdb instance, extract its typeclass
            typeclass = typeclass.typeclass.path
        elif isinstance(typeclass, Player) or utils.inherits_from(typeclass, Player):
            # this is already an object typeclass, extract its path
            typeclass = typeclass.path         

        # create new database object 
        new_db_player = PlayerDB(db_key=name, user=new_user)
        new_db_player.save()

        # assign the typeclass 
        typeclass = utils.to_unicode(typeclass)
        new_db_player.typeclass_path = typeclass

        # this will either load the typeclass or the default one
        new_player = new_db_player.typeclass

        if not object.__getattribute__(new_db_player, "is_typeclass")(typeclass, exact=True):
            # this will fail if we gave a typeclass as input and it still gave us a default
            SharedMemoryModel.delete(new_db_player)
            return None 

        new_player.basetype_setup() # setup the basic locks and cmdset
        # call hook method (may override default permissions)
        new_player.at_player_creation()

        # custom given arguments potentially overrides the hook 
        if permissions:
            new_player.permissions = permissions
        elif not new_player.permissions:
            new_player.permissions = settings.PERMISSION_PLAYER_DEFAULT

        if locks:
            new_player.locks.add(locks)

        # create *in-game* 'player' object 
        if create_character:
            if not character_typeclass:
                character_typeclass = settings.BASE_CHARACTER_TYPECLASS
            # creating the object automatically links the player
            # and object together by player.obj <-> obj.player
            new_character = create_object(character_typeclass, key=name,
                                          location=None, home=character_location, 
                                          permissions=permissions,
                                          player=new_player)        
            return new_character
        return new_player
    except Exception:
        # a failure in creating the character
        if not user:
            # in there was a failure we clean up everything we can
            logger.log_trace()
            try:
                new_user.delete()
            except Exception:
                pass
            try:
                new_player.delete()
            except Exception:
                pass 
            try:
                del new_character
            except Exception:
                pass 

