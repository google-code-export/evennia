"""
CmdSethandler

The Cmdhandler tracks an object's 'Current CmdSet', which is the
current merged sum of all CmdSets added to it.

A CmdSet constitues a set of commands. The CmdSet works as a special
intelligent container that, when added to other CmdSet make sure that
same-name commands are treated correctly (usually so there are no
doublets).  This temporary but up-to-date merger of CmdSet is jointly
called the Current Cmset. It is this Current CmdSet that the
commandhandler looks through whenever a player enters a command (it
also adds CmdSets from objects in the room in real-time). All player
objects have a 'default cmdset' containing all the normal in-game mud
commands (look etc).

So what is all this cmdset complexity good for?

In its simplest form, a CmdSet has no commands, only a key name. In
this case the cmdset's use is up to each individual game - it can be
used by an AI module for example (mobs in cmdset 'roam' move from room
to room, in cmdset 'attack' they enter combat with players).

Defining commands in cmdsets offer some further powerful game-design
consequences however. Here are some examples:

As mentioned above, all players always have at least the Default
CmdSet.  This contains the set of all normal-use commands in-game,
stuff like look and @desc etc. Now assume our players end up in a dark
room. You don't want the player to be able to do much in that dark
room unless they light a candle. You could handle this by changing all
your normal commands to check if the player is in a dark room. This
rapidly goes unwieldly and error prone. Instead you just define a
cmdset with only those commands you want to be available in the 'dark'
cmdset - maybe a modified look command and a 'light candle' command -
and have this completely replace the default cmdset.

Another example: Say you want your players to be able to go
fishing. You could implement this as a 'fish' command that fails
whenever the player has no fishing rod. Easy enough.  But what if you
want to make fishing more complex - maybe you want four-five different
commands for throwing your line, reeling in, etc? Most players won't
(we assume) have fishing gear, and having all those detailed commands
is cluttering up the command list. And what if you want to use the
'throw' command also for throwing rocks etc instead of 'using it up'
for a minor thing like fishing?

So instead you put all those detailed fishing commands into their own
CommandSet called 'Fishing'. Whenever the player gives the command
'fish' (presumably the code checks there is also water nearby), only
THEN this CommandSet is added to the Cmdhandler of the player. The
'throw' command (which normally throws rocks) is replaced by the
custom 'fishing variant' of throw. What has happened is that the
Fishing CommandSet was merged on top of the Default ones, and due to
how we defined it, its command overrules the default ones.

When we are tired of fishing, we give the 'go home' command (or
whatever) and the Cmdhandler simply removes the fishing CommandSet
so that we are back at defaults (and can throw rocks again).

Since any number of CommandSets can be piled on top of each other, you
can then implement separate sets for different situations. For
example, you can have a 'On a boat' set, onto which you then tack on
the 'Fishing' set. Fishing from a boat? No problem!
"""
import traceback 
from src.utils import logger, utils
from src.commands.cmdset import CmdSet
from src.server.models import ServerConfig

CACHED_CMDSETS = {}

def import_cmdset(python_path, cmdsetobj, emit_to_obj=None, no_logging=False):
    """
    This helper function is used by the cmdsethandler to load a cmdset
    instance from a python module, given a python_path. It's usually accessed
    through the cmdsethandler's add() and add_default() methods. 
    python_path - This is the full path to the cmdset object. 
    cmdsetobj - the database object/typeclass on which this cmdset is to be assigned 
               (this can be also channels and exits, as well as players but there will 
               always be such an object)
    emit_to_obj - if given, error is emitted to this object (in addition to logging)
    no_logging - don't log/send error messages. This can be useful if import_cmdset is just
                  used to check if this is a valid python path or not. 
    function returns None if an error was encountered or path not found.
    """        

    try:
        try:                        
            #print "importing %s: CACHED_CMDSETS=%s" % (python_path, CACHED_CMDSETS)
            wanted_cache_key = python_path            
            cmdsetclass = CACHED_CMDSETS.get(wanted_cache_key, None)
            errstring = ""
            if not cmdsetclass:
                #print "cmdset '%s' not in cache. Reloading %s on %s." % (wanted_cache_key, python_path, cmdsetobj)
                # Not in cache. Reload from disk.
                modulepath, classname = python_path.rsplit('.', 1)
                module = __import__(modulepath, fromlist=[True])
                cmdsetclass = module.__dict__[classname]                
                CACHED_CMDSETS[wanted_cache_key] = cmdsetclass            
            #instantiate the cmdset (and catch its errors)
            if callable(cmdsetclass):
                cmdsetclass = cmdsetclass(cmdsetobj) 
            return cmdsetclass

        except ImportError:
            errstring = "Error loading cmdset: Couldn't import module '%s'."
            errstring = errstring % modulepath
            raise
        except KeyError:
            errstring = "Error in loading cmdset: No cmdset class '%s' in %s."
            errstring = errstring % (classname, modulepath)
            raise
        except Exception:            
            errstring = "\n%s\nCompile/Run error when loading cmdset '%s'."
            errstring = errstring % (traceback.format_exc(), python_path)
            raise
    except Exception:            
        if errstring and not no_logging:
            print errstring 
            logger.log_trace()    
            if emit_to_obj and not ServerConfig.objects.conf("server_starting_mode"):
                object.__getattribute__(emit_to_obj, "msg")(errstring)            
        #raise # have to raise, or we will not see any errors in some situations!

# classes 

class CmdSetHandler(object):
    """
    The CmdSetHandler is always stored on an object, this object is supplied as an argument.

    The 'current' cmdset is the merged set currently active for this object.
    This is the set the game engine will retrieve when determining which
    commands are available to the object. The cmdset_stack holds a history of all CmdSets
    to allow the handler to remove/add cmdsets at will. Doing so will re-calculate
    the 'current' cmdset. 
    """

    def __init__(self, obj):
        """
        This method is called whenever an object is recreated. 

        obj - this is a reference to the game object this handler
              belongs to.
        """
        self.obj = obj                

        # the id of the "merged" current cmdset for easy access. 
        self.key = None
        # this holds the "merged" current command set 
        self.current = None
        # this holds a history of CommandSets
        self.cmdset_stack = [CmdSet(cmdsetobj=self.obj, key="Empty")]
        # this tracks which mergetypes are actually in play in the stack
        self.mergetype_stack = ["Union"] 

        # the subset of the cmdset_paths that are to be stored in the database
        self.permanent_paths = [""]
        
        #self.update(init_mode=True) is then called from the object __init__.

    def __str__(self):
        "Display current commands"                
            
        string = ""
        mergelist = []
        if len(self.cmdset_stack) > 1:
            # We have more than one cmdset in stack; list them all
            num = 0
            #print self.cmdset_stack, self.mergetype_stack
            for snum, cmdset in enumerate(self.cmdset_stack):
                num = snum
                mergetype = self.mergetype_stack[snum]
                permstring = "non-perm"
                if cmdset.permanent:
                    permstring = "perm"
                if mergetype != cmdset.mergetype:
                    mergetype = "%s^" % (mergetype)            
                string += "\n %i: <%s (%s, prio %i, %s)>: %s" % \
                    (snum, cmdset.key, mergetype,
                     cmdset.priority, permstring, cmdset)                                
                mergelist.append(str(snum))
            string += "\n"
 
        # Display the currently active cmdset, limited by self.obj's permissions
        mergetype = self.mergetype_stack[-1]  
        if mergetype != self.current.mergetype:
            merged_on = self.cmdset_stack[-2].key
            mergetype = "custom %s on cmdset '%s'" % (mergetype, merged_on)        
        if mergelist:
            string += " <Merged %s (%s, prio %i)>: %s" % ("+".join(mergelist), mergetype, self.current.priority, self.current)
        else:
            permstring = "non-perm"
            if self.current.permanent:
                permstring = "perm"
            string += " <%s (%s, prio %i, %s)>: %s" % (self.current.key, mergetype, self.current.priority, permstring,
                                                   ", ".join(cmd.key for cmd in sorted(self.current, key=lambda o:o.key)))
        return string.strip() 

    def update(self, init_mode=False):        
        """
        Re-adds all sets in the handler to have an updated
        current set. 
        
        init_mode is used right after this handler was 
        created; it imports all permanent cmdsets from db. 
        """
        if init_mode:
            # reimport all permanent cmdsets
            storage = self.obj.cmdset_storage
            #print "cmdset_storage:", self.obj.cmdset_storage            
            if storage:
                self.cmdset_stack = []           
                for pos, path in enumerate(storage):
                    if pos == 0 and not path:
                        self.cmdset_stack = [CmdSet(cmdsetobj=self.obj, key="Empty")]
                    elif path:
                        cmdset = self.import_cmdset(path)                    
                        if cmdset:
                            cmdset.permanent = True
                            self.cmdset_stack.append(cmdset)
                            
        # merge the stack into a new merged cmdset
        new_current = None 
        self.mergetype_stack = []
        for cmdset in self.cmdset_stack:                
            try:
                # for cmdset's '+' operator, order matters.                 
                new_current = cmdset + new_current 
            except TypeError:
                continue
            self.mergetype_stack.append(new_current.actual_mergetype)
        self.current = new_current
        
    def import_cmdset(self, cmdset_path, emit_to_obj=None):
        """
        Method wrapper for import_cmdset. 
        load a cmdset from a module.
        cmdset_path - the python path to an cmdset object. 
        emit_to_obj - object to send error messages to
        """
        if not emit_to_obj:
            emit_to_obj = self.obj
        return import_cmdset(cmdset_path, self.obj, emit_to_obj)
                    
    def add(self, cmdset, emit_to_obj=None, permanent=False):
        """
        Add a cmdset to the handler, on top of the old ones.
        Default is to not make this permanent (i.e. no script
        will be added to add the cmdset every server start/login).

        cmdset - can be a cmdset object or the python path to
                 such an object.
        emit_to_obj - an object to receive error messages. 
        permanent - this cmdset will remain across a server reboot

        Note: An interesting feature of this method is if you were to
        send it an *already instantiated cmdset* (i.e. not a class),
        the current cmdsethandler's obj attribute will then *not* be
        transferred over to this already instantiated set (this is
        because it might be used elsewhere and can cause strange effects). 
        This means you could in principle have the handler
        launch command sets tied to a *different* object than the
        handler. Not sure when this would be useful, but it's a 'quirk'
        that has to be documented. 
        """
        if callable(cmdset):
            if not utils.inherits_from(cmdset, CmdSet):
                raise Exception("Only CmdSets can be added to the cmdsethandler!")
            cmdset = cmdset(self.obj)
        elif isinstance(cmdset, basestring):
            # this is (maybe) a python path. Try to import from cache.
            cmdset = self.import_cmdset(cmdset)
        if cmdset:
            if permanent:
                # store the path permanently
                cmdset.permanent = True
                storage = self.obj.cmdset_storage
                if not storage:
                    storage = ["", cmdset.path] 
                else:
                    storage.append(cmdset.path)
                self.obj.cmdset_storage = storage
            else:
                cmdset.permanent = False 
            self.cmdset_stack.append(cmdset)                
            self.update()

    def add_default(self, cmdset, emit_to_obj=None, permanent=True):
        """
        Add a new default cmdset. If an old default existed,
        it is replaced. If permanent is set, the set will survive a reboot.
        cmdset - can be a cmdset object or the python path to
                 an instance of such an object. 
        emit_to_obj - an object to receive error messages. 
        permanent - save cmdset across reboots
        See also the notes for self.add(), which applies here too.
        """       
        if callable(cmdset):
            if not utils.inherits_from(cmdset, CmdSet):
                raise Exception("Only CmdSets can be added to the cmdsethandler!")
            cmdset = cmdset(self.obj)
        elif isinstance(cmdset, basestring):
            # this is (maybe) a python path. Try to import from cache.
            cmdset = self.import_cmdset(cmdset)
        if cmdset:
            if self.cmdset_stack:
                self.cmdset_stack[0] = cmdset
                self.mergetype_stack[0] = cmdset.mergetype
            else:
                self.cmdset_stack = [cmdset]
                self.mergetype_stack = [cmdset.mergetype]
            
            if permanent:
                cmdset.permanent = True 
                storage = self.obj.cmdset_storage
                if storage:
                    storage[0] = cmdset.path
                else:
                    storage = [cmdset.path]
                self.obj.cmdset_storage = storage
            else:
                cmdset.permanent = False 
            self.update()        
        
    def delete(self, cmdset=None):
        """
        Remove a cmdset from the  handler. 

        cmdset can be supplied either as a cmdset-key,
        an instance of the CmdSet or a python path
        to the cmdset. If no key is given,
        the last cmdset in the stack is removed. Whenever
        the cmdset_stack changes, the cmdset is updated.
        The default cmdset (first entry in stack) is never
        removed - remove it explicitly with delete_default.

        """
        if len(self.cmdset_stack) < 2:
            # don't allow deleting default cmdsets here. 
            return

        if not cmdset:
            # remove the last one in the stack 
            cmdset = self.cmdset_stack.pop()
            if cmdset.permanent:
                storage = self.obj.cmdset_storage
                storage.pop()
                self.obj.cmdset_storage = storage
        else:            
            # try it as a callable
            if callable(cmdset) and hasattr(cmdset, 'path'):
                delcmdsets = [cset for cset in self.cmdset_stack[1:] if cset.path == cmdset.path]
            else:
                # try it as a path or key
                delcmdsets = [cset for cset in self.cmdset_stack[1:] if cset.path == cmdset or cset.key == cmdset]
            storage = []

            if any(cset.permanent for cset in delcmdsets):
                # only hit database if there's need to 
                storage = self.obj.cmdset_storage                                
                for cset in delcmdsets:                
                    if cset.permanent:
                        try:
                            storage.remove(cset.path) 
                        except ValueError:
                            pass
            for cset in delcmdsets:
                # clean the in-memory stack 
                try:
                    self.cmdset_stack.remove(cset)
                except ValueError:
                    pass                
        # re-sync the cmdsethandler. 
        self.update()

    def delete_default(self):
        "This explicitly deletes the default cmdset. It's the only command that can."
        if self.cmdset_stack:
            cmdset = self.cmdet_stack[0]
            if cmdset.permanent:
                storage = self.obj.cmdset_storage
                if storage:
                    storage[0] = ""
                else:
                    storage = [""]
                self.cmdset_storage = storage                
            self.cmdset_stack[0] = CmdSet(cmdsetobj=self.obj, key="Empty")
        else:            
            self.cmdset_stack = [CmdSet(cmdsetobj=self.obj, key="Empty")]
        self.update()

    def all(self):
        """
        Returns the list of cmdsets. Mostly useful to check if stack if empty or not.
        """
        return self.cmdset_stack

    def clear(self):
        """
        Removes all extra Command sets from the handler, leaving only the
        default one.
        """
        self.cmdset_stack = [self.cmdset_stack[0]]
        self.mergetype_stack = [self.cmdset_stack[0].mergetype]
        storage = self.obj.cmdset_storage
        if storage: 
            storage = storage[0]
            self.obj.cmdset_storage = storage 
        self.update()

    def has_cmdset(self, cmdset_key, must_be_default=False):
        """
        checks so the cmdsethandler contains a cmdset with the given key.
        must_be_default - only match against the default cmdset. 
        """
        if must_be_default:
            return self.cmdset_stack and self.cmdset_stack[0].key == cmdset_key
        else:
            return any([cmdset.key == cmdset_key for cmdset in self.cmdset_stack])
        

    def all(self):
        """
        Returns all cmdsets.
        """
        return self.cmdset_stack

    def reset(self):
        """
        Force reload of all cmdsets in handler. This should be called 
        after CACHED_CMDSETS have been cleared (normally by @reload). 
        """
        new_cmdset_stack = []
        new_mergetype_stack = [] 
        for cmdset in self.cmdset_stack:
            if cmdset.key == "Empty":
                new_cmdset_stack.append(cmdset)
                new_mergetype_stack.append("Union")
            else:                
                new_cmdset_stack.append(self.import_cmdset(cmdset.path))
                new_mergetype_stack.append(cmdset.mergetype)
        self.cmdset_stack = new_cmdset_stack
        self.mergetype_stack = new_mergetype_stack
        self.update()
