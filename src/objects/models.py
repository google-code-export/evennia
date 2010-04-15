"""
This is where all of the crucial, core object models reside. 
"""
import re
import traceback
import time

from django.db import models
from django.conf import settings
from src.objects.util import object as util_object
from src.objects.managers.object import ObjectManager
from src.config.models import ConfigValue
from src.ansi import ANSITable, parse_ansi
from src import scripthandler
from src import defines_global
from src import session_mgr
from src import logger
from src import session_mgr

from src.idmapper.models import SharedMemoryModel as DEFAULT_MODEL
from src.idmapper.base import SharedMemoryModelBase as DEFAULT_MODEL_BASE

from src.scripthandler import scriptlink

# Import as the absolute path to avoid local variable clashes.
from src.util import functions_general
from django.db.models import signals

# temp debug function
def dbg(*args):
    logger.log_errmsg(", ".join(map(str, args)))

from src.objects.PickledObjectField import PickledObjectField

class PrimitiveModelBase(DEFAULT_MODEL_BASE):
    def __call__(cls, *args, **kwargs):
        # new_instance is custom, everything else is cut and paste
        def new_instance():
            x = super(DEFAULT_MODEL_BASE, cls).__call__(*args, **kwargs)
            dbg("___________________________")
            dbg("NEW INSTANCE", id(x), x._get_pk_val())
            # go ahead and cache it even before we init it so we don't
            # end up in a recursive loop with primitives initing other prims
            # repeatedly
            cls.cache_instance(x)
            x.at_object_creation()
            x.already_created = True
            return x
        dbg("CALLING ", cls, args, kwargs)
        instance_key = cls._get_cache_key(args, kwargs)
        if instance_key is None:
            return new_instance()
        cached_instance = cls.get_cached_instance(instance_key)
        if cached_instance is None:
            assert(not hasattr(cached_instance, "already_created"))
            cached_instance = new_instance()
            cls.cache_instance(cached_instance)
        return cached_instance

class PolymorphicPrimitiveForeignKey(models.Field):
    __metaclass__ = models.SubfieldBase
    def get_internal_type(self):
        return "IntegerField"
    def to_python(self, value):
        if value is not None:
            if type(value) is int:
                return Primitive.objects.get(id=value).preferred_object
            else:
                return value
    def get_db_prep_value(self, value):
        if value is not None:
            if hasattr(value, "primitive_ptr"):
                return value.primitive_ptr.id
            else:
                return value.id

class PreferredModel(models.CharField):
    """ TODO: should probably return the actual model object"""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        super(models.CharField, self).__init__(*args, **kwargs)

class Primitive(DEFAULT_MODEL):
    __metaclass__ = PrimitiveModelBase
    preferred_model = PreferredModel()
    _location = PolymorphicPrimitiveForeignKey(blank=True,null=True,db_index=True)
    def _set_location(self, location):
        pself = self.preferred_object
        if pself.location:
            pself.location.at_leave(self) # 
            pself.location.contents.remove(self)
        pself._location = location
        pself.location.contents.append(self)
        pself.location.at_obj_receive(self)
    location = property(fget=lambda self:self._location,fset=_set_location)
    def save(self, *args, **kwargs):
        if not self.pk and not self.preferred_model:
            self.preferred_model = self.__module__ + "." + self.__class__.__name__
        super(Primitive, self).save(*args, **kwargs)
    def at_object_creation(self):
        if hasattr(self, "already_created"):
            return
        try:
           nm = self.name
        except:
           nm = "#%s" % self.id
        # set up the preferred model from the get-go
        if not self.pk and not self.preferred_model:
            self.preferred_model = self.__module__ + "." + self.__class__.__name__
        # dont add an item to inventory contents if its not the preferred model
        if self is not self.preferred_object:
            return
        self.already_created = True
        dbg("CREATING OBJ", nm, self, id(self))
        self.contents = []
        possible_contents = Primitive.objects.filter(_location=self)
        # possible_contents = self._default_manager.filter(_location=self)
        # cause the other objects it contains to come into being
        for prim in possible_contents:
            prim.preferred_object
        if self.location:
            # FIXME: check shouldn't be needed but avoids multiple 
            # instances of objects showing up in room
            if self not in self.location.contents:
                self.location.contents.append(self.preferred_object)
    def _get_preferred_object(self):
        if not self.preferred_model:
            return self
	# Split the script name up by periods to give us the directory we need
	# to change to. I really wish we didn't have to do this, but there's some
	# strange issue with __import__ and more than two directories worth of
	# nesting.
        scriptname = self.preferred_model
	#full_script = "%s.%s" % (settings.SCRIPT_IMPORT_PATH, self.preferred_model)
        
	#script_module = ".".join(self.preferred_model.split('.')[0:-1])
	#script_name = self.preferred_model.split('.')[-1]
	# Change the working directory to the location of the script and import.
        
	#module = __import__(script_module, fromlist=[script_name])
        #mdl = getattr(module, script_name)
        mdl = scriptlink(scriptname)

        if hasattr(mdl, "primitive_ptr") and self.id and self.preferred_model:
            try:
                return mdl.objects.get(primitive_ptr=self.id)
            except:
                dbg("IMPORTING? DEFAULTING FOR #%s, %s, %s" % (self.id, mdl, dir(self)))
                return self
        else:
            #print "DEFAULTING FOR #%s, %s, %s" % (self.id, mdl, dir(self))
            dbg("DEFAULTING FOR #%s, %s, %s" % (self.id, self, mdl))
            return self
    preferred_object = property(fget=_get_preferred_object)
    def matches(self, txt):
        if txt.lower() == self.name.lower():
            return True

class Attribute(DEFAULT_MODEL):
    primitive = models.ForeignKey(Primitive, related_name="_attributes")
    name = models.CharField(max_length=255)
    value = PickledObjectField()

class AttributeField(object):
    def __init__(self, default=None):
        self.name = None
        self.default = default
    def post_save_listener(self, **kwargs):
        instance = kwargs['instance']
        if hasattr(instance, "primitive_ptr"):
            primitive = instance.primitive_ptr
        else:
            primitive = instance
        val = self.__get__(instance)
        attr, created = Attribute.objects.get_or_create(primitive=primitive,name=self.name)
        if attr.value != val:
           attr.value = val
           attr.save()
    def contribute_to_class(self, cls, name):
        print "CONTRIBUTING AttributeField %s" % name
        self.name = name
        setattr(cls, name, self)
        signals.post_save.connect(self.post_save_listener, sender=cls, weak=False, dispatch_uid="post_save_listener")
    def __get__(self, instance, owner=None):
        if instance is None:
            return None
        elif hasattr(instance, '_%s_cache' % self.name):
               return getattr(instance, '_%s_cache' % self.name, None)
        elif instance.id:
            tval, created = Attribute.objects.get_or_create(primitive=instance,name=self.name)
            # probaly should be changed to just add a default to PickledObjectField
            if created:
                val = self.default
            else:
                val = tval.value
            self.__set__(instance, val)
            return val
        else:
            return None
    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(_('%s can only be set on instances.') % self.name)
        else:
            setattr(instance, '_%s_cache' % self.name, value)



class Object(Primitive):
    """
    The Object class is very generic representation of a THING, PLAYER, EXIT,
    ROOM, or other entities within the database. Pretty much anything in the
    game is an object. Objects may be one of several different types, and
    may be parented to allow for differing behaviors.
    """
    
    class Meta(PrimitiveModelBase):
        """
        Define permission types on the object class and
        how it is ordered in the database.
        """
        ordering = ['-date_created', 'id']
        permissions = settings.PERM_OBJECTS

    name = models.CharField(max_length=255)
    owner = models.ForeignKey('self',
                              related_name="obj_owner",
                              blank=True, null=True)
    home = models.ForeignKey('self',
                             related_name="obj_home",
                             blank=True, null=True)
    date_created = models.DateField(editable=False,
                                    auto_now_add=True)

    # state system can set a particular command
    # table to be used (not persistent).
    state = None

    # the following is_ functions should be properties
    def is_superuser(self):
        if hasattr(self, "user"):
           return self.user.is_superuser
    def is_player(self):
        if hasattr(self, "user"):
           return True
    
    def __str__(self):
        return self.name
        
    def __cmp__(self, other):
        """
        Used to figure out if one object is the same as another.
        """
        return self.id == other.id

    def dbref(self):
        """Returns the object's dbref id on the form #NN, directly
        usable by Object.objects.dbref_search()
        """
        return "#%s" % str(self.id)
        
    #
    # BEGIN COMMON METHODS
    # 
    def search_for_object(self, ostring,
                          emit_to_obj=None,
                          search_contents=True, 
                          search_location=True,
                          dbref_only=False, 
                          limit_types=False,
                          search_aliases=False,
                          attribute_name=None):
        """
        Perform a standard object search, handling multiple
        results and lack thereof gracefully.

        ostring: (str) The string to match object names against.
                       Obs - To find a player, append * to the start of ostring. 
        emit_to_obj: (obj) An object (instead of caller) to receive search feedback
        search_contents: (bool) Search the caller's inventory
        search_location: (bool) Search the caller's location
        dbref_only: (bool) Requires ostring to be a #dbref
        limit_types: (list) Object identifiers from defines_global.OTYPE:s
        search_aliases: (bool) Search player aliases first
        attribute_name: (string) Which attribute to match (if None, uses default 'name')
        """

        # This is the object that gets the duplicate/no match emits.
        if not emit_to_obj:
            emit_to_obj = self
        search_sets = [self.location.contents]
        if search_contents:
            search_sets.append(self.contents)    
        if search_aliases:
           #TODO implement player aliases again
           pass 
        results = []
        for search_set in search_sets:
            results += filter(lambda x: x.matches(ostring), search_set)

        if len(results) > 1:
            string = "More than one match for '%s' (please narrow target):" % ostring            
            for num, result in enumerate(results):
                invtext = ""
                if result.location == self:
                    invtext = " (carried)"                    
                string += "\n %i-%s%s" % (num+1,
                                     result.name,
                                     invtext)
            emit_to_obj.emit_to(string)            
            return False
        elif len(results) == 0:
            emit_to_obj.emit_to("I don't see that here.")
            return False
        else:
            return results[0]
        
    def get_sessions(self):
        """
        Returns a list of sessions matching this object.
        """
        return session_mgr.sessions_from_object(self)
            
    def emit_to(self, message):
        """
        Emits something to any sessions attached to the object.
        
        message: (str) The message to send
        """
            
        sessions = self.get_sessions()
        for session in sessions:
            session.msg(parse_ansi(message))
            
    def execute_cmd(self, command_str, session=None, ignore_state=False):
        """
        Do something as this object.

        bypass_state - ignore the fact that a player is in a state
                       (means the normal command table will be used
                       no matter what)
        """      
        # The Command object has all of the methods for parsing and preparing
        # for searching and execution. Send it to the handler once populated.        
        cmdhandler.handle(cmdhandler.Command(self, command_str,
                                             session=session),
                          ignore_state=ignore_state)
            
    def emit_to_contents(self, message, exclude=None):
        """
        Emits something to all objects inside an object.
        """
        for x in self.contents:
            if x != exclude:
                x.emit_to(message)
            
    def get_user_account(self):
        return None
    
    def sees_dbrefs(self):
        """
        Returns True if the object sees dbrefs in messages. This is here
        instead of session.py due to potential future expansion in the
        direction of MUX-style puppets.
        """
        looker_user = self.get_user_account()
        if looker_user:
            # Builders see dbrefs
            return looker_user.has_perm('objects.see_dbref')
        else:
            return False

    def has_perm(self, perm):
        """
        Checks to see whether a user has the specified permission or is a super
        user.

        perm: (string) A string representing the desired permission. This
                       is on the form app.perm , e.g. 'objects.see_dbref' as
                       defined in the settings file.         
        """
        if not self.is_player():
            return False

        if self.is_superuser():
            return True

        if self.get_user_account().has_perm(perm):
            return True
        else:
            return False

    def has_perm_list(self, perm_list):
        # TODO
        return True
        """
        Checks to see whether a user has the specified permission or is a super
        user. This form accepts an iterable of strings representing permissions,
        if the user has any of them return true.

        perm_list: (iterable) An iterable of strings of permissions.
        """
        if not self.is_player():
            return False

        if self.is_superuser():
            return True

        for perm in perm_list:
            # Stop searching perms on the first match.
            if self.get_user_account().has_perm(perm):
                return True
            
        # Fall through to failure
        return False

    def has_group(self, group):
        # TODO
        return True
        """
        Checks if a user is member of a particular user group.
        """
        if not self.is_player():
            return False

        if self.is_superuser():
            return True

        if group in [g.name for g in self.get_user_account().groups.all()]:
            return True
        else:
            return False
        

    def owns_other(self, other_obj):
        """
        See if the envoked object owns another object.
        other_obj: (Object) Reference for object to check ownership of.
        """
        return self.id == other_obj.get_owner().id

    def controls_other(self, other_obj, builder_override=False):
        """
        See if the envoked object controls another object.
        other_obj: (Object) Reference for object to check dominance of.
        builder_override: (bool) True if builder perm allows controllership.
        """
        if self == other_obj:
            return True
            
        if self.is_superuser():
            # Don't allow superusers to dominate other superusers.
            if not other_obj.superuser():
                return True
            else:
                return False
        
        if self.owns_other(other_obj):
            # If said object owns the target, then give it the green.
            return True
        
        # When builder_override is enabled, a builder permission means
        # the object controls the other.
        if builder_override and not other_obj.is_player() \
               and self.has_group('Builders'):
            return True

        # They've failed to meet any of the above conditions.
        return False

    def set_home(self, new_home):
        """
        Sets an object's home.
        """
        self.home = new_home
        self.save()
        
    def set_owner(self, new_owner):
        """
        Sets an object's owner.
        """
        self.owner = new_owner
        self.save()

    def destroy(self, destroy_players=False,
                destroy_contents=False):    
        """
        Destroy an object after first safely removing objects inside
        it as well cleaning up exits. 
        """
        
        if self.is_player() and not destroy_players:
            # Protect against destroying players unless we have
            # specifically set the keyword for it. 
            logger.log_errmsg("Not allowed to destroy a Player.")
            return
        
        # Clear out any objects located within the object

        # TODO: Temporarily disabled until it's clear how the contents
        # are stored.        
        #self.clear_objects()            

        # Destroy any exits to and from this room, do this first
        # TODO: temporarily disabled.
        #self.clear_exits()

        # Destroy this object permanently
        self.delete()
              
    def delete(self):
        """
        Deletes an object permanently. Observe that this will not  
        """
        # check if this is a player. Kick their session.
        sessions = self.get_sessions()
        for session in sessions:
            session.msg("You have been deleted. Goodbye.")
            session.handle_close()            
        # delete the object 
        super(Object, self).delete()

    def clear_exits(self):
        """
        Destroys all of the exits and any exits pointing to this
        object as a destination.
        """
        exits = self.exits
        exits += self.obj_home.all().exits

        for exit in exits:
            exit.destroy()

    def clear_objects(self):
        """
        Moves all objects (players/things) currently in a
        GOING -> GARBAGE location to their home or default
        home (if it can be found).
        """
        # Gather up everything, other than exits and going/garbage,
        # that is under the belief this is its location.
        objs = self.obj_location.filter(type__in=[1, 2, 3])
        default_home_id = ConfigValue.objects.get_configvalue('default_home')
        try:
            default_home = Object.objects.get(id=default_home_id)
        except:
            functions_general.log_errmsg("Could not find default home '(#%d)'." % (default_home_id))

        for obj in objs:
            home = obj.get_home()
            text = "object"
            
            if obj.is_player():
                text = "player"

            # Obviously, we can't send it back to here.
            if home and home.id == self.id:
                obj.home = default_home
                obj.save()
                home = default_home

            # If for some reason it's still None...
            if not home:
                string = "Missing default home, %s '%s(#%d)' now has a null location."
                functions_general.log_errmsg(string %
                                             (text, obj.name, obj.id))
                    
            if obj.is_player():
                if obj.is_connected_plr():
                    if home:                        
                        obj.emit_to("Your current location has ceased to exist, moving you to your home %s(#%d)." %
                                    (home.name, home.id))
                    else:
                        # Famous last words: The player should never see this.
                        obj.emit_to("You seem to have found a place that does not exist ...")
                    
            # If home is still None, it goes to a null location.            
            obj.move_to(home)

    def is_connected_plr(self):
        """
        Is this object a connected player?
        """
        if self.is_player():
            if self.get_sessions():
                return True

        # No matches or not a player
        return False
        
    def get_owner(self):
        """
        Returns an object's owner.
        """
        # Players always own themselves.
        if self.is_player():
            return self
        else:
            return self.owner
    
    def get_home(self):
        """
        Returns an object's home.
        """
        try:
            return self.home
        except:
            return None
    
    def get_location(self):
        """
        Returns an object's location.
        """
        try:
            return self.location
        except:
            string = "Object '%s(#%d)' has invalid location: #%s"
            functions_general.log_errmsg(string % \
                                         (self.name,self.id,self.location_id))
            return False

## #    def get_cache(self):
## #        """
## #        Returns an object's volatile cache (in-memory storage)
## #        """
## #        return cache.get_cache(self.dbref())

## #    def del_cache(self):
## #        """
## #        Cleans the object cache for this object
## #        """
## #        cache.flush_cache(self.dbref())        
## #    cache = property(fget=get_cache, fdel=del_cache)

    ## def get_pcache(self):
    ##     """
    ##     Returns an object's persistent cache (in-memory storage)
    ##     """
    ##     return cache.get_pcache(self.dbref())

    ## def del_pcache(self):
    ##     """
    ##     Cleans the object persistent cache for this object
    ##     """
    ##     cache.flush_pcache(self.dbref())
        
    ## pcache = property(fget=get_pcache, fdel=del_pcache)
    
    ## def get_script_parent(self):
    ##     """
    ##     Returns a string representing the object's script parent.
    ##     """
    ##     if not self.script_parent or self.script_parent.strip() == '':
    ##         # No parent value, assume the defaults based on type.
    ##         if self.is_player():
    ##             return settings.SCRIPT_DEFAULT_PLAYER
    ##         else:
    ##             return settings.SCRIPT_DEFAULT_OBJECT
    ##     else:
    ##         # A parent has been set, load it from the field's value.
    ##         return self.script_parent
    
    def get_zone(self):
        """
        Returns the object that is marked as this object's zone.
        """
        try:
            return self.zone
        except:
            return None

    def set_zone(self, new_zone):
        """
        Sets an object's zone.
        """
        self.zone = new_zone
        self.save()
    
    def move_to(self, target, quiet=False, force_look=True):
        """
        Moves the object to a new location.
        
        target: (Object) Reference to the object to move to.
        quiet:  (bool)    If true, don't emit left/arrived messages.
        force_look: (bool) If true and self is a player, make them 'look'.
        """
        # First, check if we can enter that location at all.
        if not target.enter_lock(self):
            if self.enter_lock_msg:
                self.emit_to(self.enter_lock_msg)
            else:
                self.emit_to("That destination is blocked from you.")
            return
        
        source_location = self.location
        owner = self.get_owner()
        errtxt = "There was a bug in a move_to(). Contact an admin.\n"

        # Before the move, call eventual pre-commands.
        try:
            if self.at_before_move(target) != None:                
                return
        except:            
            owner.emit_to("%s%s" % (errtxt, traceback.print_exc()))
            return 
        
        if not quiet:
            #tell the old room we are leaving
            try:
                self.announce_move_from(target)            
            except:
                owner.emit_to("%s%s" % (errtxt, traceback.print_exc()))

            
        # Perform move
        self.location = target
        self.save()        
                
        if not quiet:
            # Tell the new room we are there. 
            try:
                self.announce_move_to(source_location)
            except:
                owner.emit_to("%s%s" % (errtxt, traceback.print_exc()))
            
        # Execute eventual extra commands on this object after moving it
        try:
            self.at_after_move(source_location)
        except:
            owner.emit_to("%s%s" % (errtxt, traceback.print_exc()))
        # Perform eventual extra commands on the receiving location
        try:
            target.at_obj_receive(self, source_location)
        except:
            owner.emit_to("%s%s" % (errtxt, traceback.print_exc()))

        if force_look and self.is_player():            
            self.execute_cmd('look')

    def dbref_match(self, oname):
        """
        Check if the input (oname) can be used to identify this particular object
        by means of a dbref match.
        
        oname: (str) Name to match against.
        """
        if not util_object.is_dbref(oname):
            return False
            
        try:
            is_match = int(oname[1:]) == self.id
        except ValueError:
            return False
            
        return is_match
        
    def name_match(self, oname, match_type="fuzzy"):
        """    
        See if the input (oname) can be used to identify this particular object.
        Check the # sign for dbref (exact) reference, and anything else is a
        name comparison.
        
        NOTE: A 'name' can be a dbref or the actual name of the object. See
        dbref_match for an exclusively name-based match.
        """
        
        if util_object.is_dbref(oname):
            # First character is a pound sign, looks to be a dbref.
            return self.dbref_match(oname)

        oname = oname.lower()
        if match_type == "exact":
            #exact matching
            name_chunks = self.name.lower().split(';')
            #False=0 and True=1 in python, so if sum>0, we
            #have at least one exact match.
            return sum(map(lambda o: oname == o, name_chunks)) > 0
        else:
            #fuzzy matching
            return oname in self.name.lower()
            
    def filter_contents_from_str(self, oname):
        """
        Search an object's contents for name and dbref matches. Don't put any
        logic in here, we'll do that from the end of the command or function.
        
        oname: (str) The string to filter from.
        """
        return [prospect for prospect in self.contents if prospect.name_match(oname)]

    # Type comparison methods.
    def is_player(self):
        return session_mgr.sessions_from_object(self) != []
    def is_room(self):    
        return self.type == defines_global.OTYPE_ROOM
    def is_thing(self):
        return self.type == defines_global.OTYPE_THING
    def is_exit(self):
        return self.type == defines_global.OTYPE_EXIT
#    def is_going(self):
#        return self.type == defines_global.OTYPE_GOING
#    def is_garbage(self):
#        return self.type == defines_global.OTYPE_GARBAGE
    
    # object custom commands

    def add_command(self, command_string, function,
                    priv_tuple=None, extra_vals=None,
                    help_category="", priv_help_tuple=None,
                    auto_help_override=False):
        """
        Add an object-based command to this object. The command
        definition is added to an attribute-stored command table
        (this table is created when adding the first command)

        command_string: (string) Command string (IE: WHO, QUIT, look).
        function: (reference) The command's function.
        priv_tuple: (tuple) String tuple of permissions required for command.
        extra_vals: (dict) Dictionary to add to the Command object.

        By default object commands are NOT added to the global help system
        with auto-help. You have to actively set auto_help_override to True
        if you explicitly want auto-help for your object command.
        
        help_category (str): An overall help category where auto-help will place 
                             the help entry. If not given, 'General' is assumed.
        priv_help_tuple (tuple) String tuple of permissions required to view this
                                help entry. If nothing is given, priv_tuple is used. 
        auto_help_override (bool): If True, use auto-help. If None, use setting
                                   in settings.AUTO_HELP_ENABLED. Default is False
                                   for object commands.
        """

        # we save using the attribute object to avoid
        # the protection on the __command_table__ keyword
        # in set_attribute_value()
        if not hasattr(self, "cmdtable"):
            # create new table if we didn't have one before
            from src.cmdtable import CommandTable 
            had_table = False 
            self.cmdtable = CommandTable()
        # add the command to the object's command table.
        self.cmdtable.add_command(command_string, function, priv_tuple, extra_vals,
                             help_category, priv_help_tuple,
                             auto_help_override)
            
    #state access functions

    def get_state(self):
        """
        Returns the player's current state.
        """
        return self.state
    
    def set_state(self, state_name=None):
        """
        Only allow setting a state on a player object, otherwise
        fail silently.

        This command safeguards the batch processor against dropping
        out of interactive mode; it also allows builders to
        sidestep room-based states when building (the genperm.admin_nostate
        permission is not set on anyone by default, set it temporarily
        when building a state-based room). 
        """
        if not self.is_player():
            return False
        
        if self.is_superuser():
            # we have to deal with superusers separately since
            # they would always appear to have the genperm.admin_nostate
            # permission. Instead we expect them to set the flag
            # ADMIN_NOSTATE on themselves if they don't want to
            # enter states. 
            nostate = self.admin_nostate
        else:
            # for other users we request the permission as normal. 
            nostate = self.has_perm("genperms.admin_nostate")

        # we never enter other states if we are already in
        # the interactive batch processor.
        nostate = nostate or \
                  self.get_state() == "_interactive batch processor"        

        if nostate:
            return False
        # switch the state 
        self.state = state_name      
        return True
            
    def clear_state(self):
        """
        Set to no state (return to normal operation)

        This safeguards the batch processor from exiting its
        interactive mode when entering a room cancelling states.
        (batch processor clears the state directly instead)
        """        
        if not self.state == "_interactive batch processor":
            self.state = None

    def purge_object(self):
        "Completely clears all aspects of the object."
        self.clear_all_attributes()
        self.clear_state()
        self.home = None 
        self.owner = None 
        self.location = None
        self.save()
### BEGIN IMPORT FROM OBJECT SCRIPT PARENT ###
    def at_object_creation(self):
        """
        This is triggered after a new object is created and ready to go. If
        you'd like to set attributes, or do anything when the object
        is created, do it here and not in __init__().
        """
        x = super(Object, self).at_object_creation()
    
    def at_object_destruction(self, pobject=None):
        """
        This is triggered when an object is about to be destroyed via
        @destroy ONLY. If an object is deleted via delete(), it is assumed
        that this method is to be skipped.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s looked at %s." % (pobject, self)
        pass
        
    def at_desc(self, pobject=None):
        """
        Perform this action when someone uses the LOOK command on the object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s looked at %s." % (pobject, self)
        pass

    def at_get(self, pobject):
        """
        Perform this action when someone uses the GET command on the object.
        
        values: 
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s got %s." % (pobject, self)
        pass

    def at_leave(self, obj):
        """
        Hook for the location from which an object is moved
        """
        pass
    
    def at_before_move(self, target_location):
        """
        This hook is called just before the object is moved.
        arg:
          target_location (obj): the place where this object is to be moved
        returns:
          if this function returns anything but None, the move is cancelled. 
        
        """
        pass

    def announce_move_from(self, target_location):
        """
        Called when announcing to leave a destination. 
        target_location - the place we are going to
        """
        loc = self.get_location()
        if loc:
            loc.emit_to_contents("%s has left." % self.name, exclude=self)
            if loc.is_player():
                loc.emit_to("%s has left your inventory." % (self.name))

    def announce_move_to(self, source_location):
        """
        Called when announcing one's arrival at a destination.
        source_location - the place we are coming from
        """
        loc = self.get_location()
        if loc: 
            loc.emit_to_contents("%s has arrived." % self.name, exclude=self)
            if loc.is_player():
                loc.emit_to("%s is now in your inventory." % self.name)

    def at_after_move(self, old_loc=None):
        """
        This hook is called just after the object was successfully moved.
        No return values.
        """
        pass
    
    def at_drop(self, pobject):
        """
        Perform this action when someone uses the DROP command on the object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s dropped %s." % (pobject, self)
        pass
    
    def at_obj_receive(self, object=None, old_loc=None):
        """
        Called whenever an object is added to the contents of this object.        
        """
        pass

    def return_appearance(self, pobject=None):
        """
        Returns a string representation of an object's appearance when LOOKed at.
        
        values: 
            * pobject: (Object) The object requesting the action.
        """
        # This is the object being looked at.
        target_obj = self        
        # See if the envoker sees dbref numbers.
        lock_msg = ""
        if pobject:        
            #check visibility lock
            if not target_obj.visible_lock(pobject):
                temp = target_obj.visible_lock_msg
                if temp:
                    return temp
                return "I don't see that here."
            
            show_dbrefs = pobject.sees_dbrefs()                                        

            #check for the defaultlock, this shows a lock message after the normal desc, if one is defined.
            #TODO - not sure why this should be restricted to rooms so disabled
            if False:
		if target_obj.is_room() and \
		       not target_obj.default_lock(pobject):
		    temp = target_obj.lock_msg
		    if temp:
			lock_msg = "\n%s" % temp
        else:
            show_dbrefs = False
                        
        if hasattr(target_obj, "desc"):
            retval = "%s%s\r\n%s%s%s" % ("%ch",
                target_obj.name,
                target_obj.desc, lock_msg,
                "%cn")
        else:
            retval = "%s%s%s" % ("%ch",
                                 target_obj.name,
                                 "%cn")
        if self.contents:
            retval += "\n\r%sYou see:%s" % (ANSITable.ansi["hilite"], 
                                            ANSITable.ansi["normal"])
            for obj in self.contents:
                retval +='\n\r%s' % (obj.name,)
            
        return retval

    def default_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for picking up
        objects or traversing exits.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.LOCKS
        if locks: 
            return locks.check("DefaultLock", pobject)
        else:
            return True

    def use_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for seeing whether
        a player can use an object or any of its commands.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.LOCKS
        if locks: 
            return locks.check("UseLock", pobject)
        else:
            return True

    def enter_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for seeing whether
        a player can enter another object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.LOCKS
        if locks: 
            return locks.check("EnterLock", pobject)
        else:
            return True

    def visible_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for picking up
        objects or traversing exits.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.LOCKS
        if locks: 
            return locks.check("VisibleLock", pobject)
        else:
            return True
    
    def lock_func(self, obj):
        """
        This is a custom function called by locks with the FuncKey key. Its
        return value should match that specified in the lock (so no true/false
        lock result is actually determined in here). Default desired return
        value is True. Also remember that the comparison in FuncKey is made
        using the string representation of the return value, since @lock can
        only define string lock criteria. 
        """
        return False

    def at_pre_login(self, session):
        """
        Everything done here takes place before the player is actually
        'logged in', in a sense that they're not ready to send logged in
        commands or receive communication.
        """
        
        # Load the player's channels from their JSON __CHANLIST attribute.
        comsys.load_object_channels(self)
        self.Last = "%s" % (time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()),)
        self.Lastsite = "%s" % (session.address[0],)
        self.CONNECTED = True

    def at_first_login(self):
        """
        This hook is called only *once*, when the player is created and logs
        in for first time. It is called after the user has logged in, but
        before at_post_login() is called.
        """
        self.emit_to("Welcome to %s, %s.\n\r" % (
            ConfigValue.objects.get_configvalue('site_name'), 
            self.name))
        
    def at_post_login(self, session):
        """
        The user is now logged in. This is what happens right after the moment
        they are 'connected'.
        """
        self.emit_to("You are now logged in as %s." % (self.name,))
        self.get_location().emit_to_contents("%s has connected." % 
            (self.name,), exclude=self)
        self.execute_cmd("look")

    def at_disconnect(self):
        """
        This is called just before the session disconnects, for whatever reason.
        """
        location = self.get_location()
        if location != None:
            location.emit_to_contents("%s has disconnected." % (self.name,), exclude=self)


#
# Base MUD object types 
#

class Exit(Object):
    destination = models.ForeignKey(Object, related_name="_destination")
    def matches(self, txt):
        alternatives = {}
        alternatives["n"] = "north"
        alternatives["s"] = "south"
        alternatives["e"] = "east"
        alternatives["w"] = "west"
        alternatives["nw"] = "northwest"
        alternatives["sw"] = "southwest"
        alternatives["ne"] = "northeast"
        alternatives["se"] = "southeast"
        alternatives["u"] = "up"
        alternatives["d"] = "down"
        if alternatives.has_key(txt.lower()):
            txt = alternatives[txt.lower()]
        if self.name.lower() == txt.lower():
            return True
        if txt.lower() in map(lambda word: word.lower(), word_list(self.keywords)):
            return True
class Thing(Object):
    pass

# Deferred imports are poopy. This will require some thought to fix.
from src import cmdhandler
from src import comsys
