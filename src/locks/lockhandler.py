"""
Locks

A lock defines access to a particular subsystem or property of
Evennia. For example, the "owner" property can be impmemented as a
lock. Or the disability to lift an object or to ban users.

A lock consists of two three parts: 

 - access_type - this defines what kind of access this lock regulates. This
   just a string. 
 - function call - this is one or many calls to functions that will determine
   if the lock is passed or not.
 - lock function(s). These are regular python functions with a special 
   set of allowed arguments. They should always return a boolean depending
   on if they allow access or not. 

# Lock function

A lock function is defined by existing in one of the modules
listed by settings.LOCK_FUNC_MODULES. It should also always
take four arguments looking like this:

   funcname(accessing_obj, accessed_obj, *args, **kwargs):
        [...]

The accessing object is the object wanting to gain access.
The accessed object is the object this lock resides on
args and kwargs will hold optional arguments and/or keyword arguments 
to the function as a list and a dictionary respectively.

Example:
   
   perm(accessing_obj, accessed_obj, *args, **kwargs):
       "Checking if the object has a particular, desired permission"
       if args:
           desired_perm = args[0] 
           return desired_perm in accessing_obj.permissions
       return False 

Lock functions should most often be pretty general and ideally possible to
re-use and combine in various ways to build clever locks. 


# Lock definition

A lock definition is a string with a special syntax. It is added to 
each object's lockhandler, making that lock available from then on. 

The lock definition looks like this:

 'access_type:[NOT] func1(args)[ AND|OR][NOT] func2() ...'

That is, the access_type, a colon followed by calls to lock functions
combined with AND or OR. NOT negates the result of the following call.

Example: 
  
 We want to limit who may edit a particular object (let's call this access_type 
for 'edit', it depends on what the command is looking for). We want this to
only work for those with the Permission 'Builder'. So we use our lock
function above and call it like this:

  'edit:perm(Builder)'
 
Here, the lock-function perm() will be called (accessing_obj and accessed_obj are added
automatically, you only need to add the args/kwargs, if any). 

If we wanted to make sure the accessing object was BOTH a Builder and a GoodGuy, we
could use AND:

  'edit:perm(Builder) AND perm(GoodGuy)'

To allow EITHER Builders and GoodGuys, we replace AND with OR. perm() is just one example,
the lock function can do anything and compare any properties of the calling object to 
decide if the lock is passed or not.

  'lift:attrib(very_strong) AND NOT attrib(bad_back)'

To make these work, add the string to the lockhandler of the object you want
to apply the lock to: 

  obj.lockhandler.add('edit:perm(Builder)')

From then on, a command that wants to check for 'edit' access on this 
object would do something like this:

  if not target_obj.lockhandler.has_perm(caller, 'edit'):
      caller.msg("Sorry you cannot edit that.")


# Permissions 

Permissions are just text strings stored in a comma-separated list on
typeclassed objects. The default perm() lock function uses them,
taking into account settings.PERMISSION_HIERARCHY. Also, the
restricted @perm command sets them, but otherwise they are identical
to any other identifier you can use.

"""

import re, inspect
from django.conf import settings
from src.utils import logger, utils 

#
# Cached lock functions
#

LOCKFUNCS = {}
def cache_lockfuncs():
    "Updates the cache."
    global LOCKFUNCS
    LOCKFUNCS = {}
    for modulepath in settings.LOCK_FUNC_MODULES:
        modulepath = utils.pypath_to_realpath(modulepath)
        mod = utils.mod_import(modulepath)
        if mod:                  
            for tup in (tup for tup in inspect.getmembers(mod) if callable(tup[1])):
                LOCKFUNCS[tup[0]] = tup[1]
        else:
            logger.log_errmsg("Couldn't load %s from PERMISSION_FUNC_MODULES." % modulepath)

#
# pre-compiled regular expressions
#

RE_FUNCS = re.compile(r"\w+\([^)]*\)")
RE_SEPS = re.compile(r"(?<=[ )])AND(?=\s)|(?<=[ )])OR(?=\s)|(?<=[ )])NOT(?=\s)")
RE_OK = re.compile(r"%s|and|or|not")


#
#
# Lock handler 
#
#

class LockHandler(object):
    """
    This handler should be attached to all objects implementing 
    permission checks, under the property 'lockhandler'. 
    """

    def __init__(self, obj):
        """
        Loads and pre-caches all relevant locks and their
        functions.
        """
        if not LOCKFUNCS:
            cache_lockfuncs()
        self.obj = obj
        self.locks = {}        
        self.log_obj = None 
        self.no_errors = True
        self.reset_flag = False 

        self._cache_locks(self.obj.lock_storage)



    def __str__(self):
        return ";".join(self.locks[key][2] for key in sorted(self.locks))

    def _log_error(self, message):
        "Try to log errors back to object"
        if self.log_obj and hasattr(self.log_obj, 'msg'):
            self.log_obj.msg(message)   
        elif hasattr(self.obj, 'msg'):
            self.obj.msg(message)
        else:
            logger.log_trace("%s: %s" % (self.obj, message))

    def _parse_lockstring(self, storage_lockstring):
        """
        Helper function. 
        locks are stored as a string 'atype:[NOT] lock()[[ AND|OR [NOT] lock() [...]];atype...
        """
        locks = {}
        if not storage_lockstring:
            return locks 
        nlocks = storage_lockstring.count(';') + 1
        duplicates = 0
        elist = []
        for raw_lockstring in storage_lockstring.split(';'):            
            lock_funcs = []
            access_type, rhs = (part.strip() for part in raw_lockstring.split(':', 1))

            # parse the lock functions and separators
            funclist = RE_FUNCS.findall(rhs)                                           
            evalstring = rhs.replace('AND','and').replace('OR','or').replace('NOT','not')
            nfuncs = len(funclist)
            for funcstring in funclist: 
                funcname, rest = [part.strip().strip(')') for part in funcstring.split('(', 1)]
                func = LOCKFUNCS.get(funcname, None)
                if not callable(func):
                    elist.append("Lock: function '%s' is not available." % funcstring)
                    continue 
                args = [arg.strip() for arg in rest.split(',') if not '=' in arg]
                kwargs = dict([arg.split('=', 1) for arg in rest.split(',') if '=' in arg])                
                lock_funcs.append((func, args, kwargs))            
                evalstring = evalstring.replace(funcstring, '%s')        
            if len(lock_funcs) < nfuncs:                                
                continue
            try:
                # purge the eval string of any superfluos items, then test it
                evalstring = " ".join(RE_OK.findall(evalstring))
                eval(evalstring % tuple(True for func in funclist))
            except Exception:
                elist.append("Lock: definition '%s' has syntax errors." % raw_lockstring)
                continue
            if access_type in locks:                
                duplicates += 1
                elist.append("Lock: access type '%s' changed from '%s' to '%s' " % \
                    (access_type, locks[access_type][2], raw_lockstring))
            locks[access_type] = (evalstring, tuple(lock_funcs), raw_lockstring)            
        if elist:
            self._log_error("\n".join(elist))
            self.no_errors = False
        
        return locks 

    def _cache_locks(self, storage_lockstring):
        """Store data"""
        self.locks = self._parse_lockstring(storage_lockstring)

    def _save_locks(self):
        "Store locks to obj"
        self.obj.lock_storage = ";".join([tup[2] for tup in self.locks.values()])

    def add(self, lockstring, log_obj=None):
        """
        Add a new, single lockstring on the form '<access_type>:<functions>'

        If log_obj is given, it will be fed error information.
        """
        if log_obj:
            self.log_obj = log_obj
        self.no_errors = True 
        # sanity checks        
        for lockdef in lockstring.split(';'):                        
            if not ':' in lockstring:
                self._log_error("Lock: '%s' contains no colon (:)." % lockdef)
                return False 
            access_type, rhs = [part.strip() for part in lockdef.split(':', 1)]
            if not access_type:
                self._log_error("Lock: '%s' has no access_type (left-side of colon is empty)." % lockdef)
                return False 
            if rhs.count('(') != rhs.count(')'):
                self._log_error("Lock: '%s' has mismatched parentheses." % lockdef)
                return False 
            if not RE_FUNCS.findall(rhs):
                self._log_error("Lock: '%s' has no valid lock functions." % lockdef)
                return False 
        # get the lock string
        storage_lockstring = self.obj.lock_storage
        if storage_lockstring:
            storage_lockstring = storage_lockstring + ";" + lockstring
        else:
            storage_lockstring = lockstring
        # cache the locks will get rid of eventual doublets
        self._cache_locks(storage_lockstring)
        self._save_locks()
        self.log_obj = None 
        return self.no_errors 

    def get(self, access_type):
        "get the lockstring of a particular type"
        return self.locks.get(access_type, None)

    def delete(self, access_type):
        "Remove a lock from the handler"
        if access_type in self.locks:
            del self.locks[access_type]
            self._save_locks()
            return True 
        return False 

    def clear(self):
        "Remove all locks"
        self.locks = {}
        self.lock_storage = ""
    def reset(self):
        """
        Set the reset flag, so the the lock will be re-cached at next checking.
        This is usually set by @reload. 
        """
        self.reset_flag = True
        
    def check(self, accessing_obj, access_type, default=False):
        """
        Checks a lock of the correct type by passing execution
        off to the lock function(s).

        accessing_obj - the object seeking access
        access_type - the type of access wanted
        default - if no suitable lock type is found, use this
        """
        if self.reset_flag:
            # rebuild cache 
            self._cache_locks(self.obj.lock_storage)
            self.reset_flag = False 

        if (hasattr(accessing_obj, 'player') and hasattr(accessing_obj.player, 'is_superuser') and accessing_obj.player.is_superuser) \
                or (hasattr(accessing_obj, 'get_player') and (accessing_obj.get_player()==None or accessing_obj.get_player().is_superuser)):
            # we grant access to superusers and also to protocol instances that not yet has any player assigned to them (the
            # latter is a safety feature since superuser cannot be authenticated at some point during the connection).
            return True
        if access_type in self.locks:
            # we have a lock, test it.            
            evalstring, func_tup, raw_string = self.locks[access_type]            
            # we have previously stored the function object and all the args/kwargs as list/dict,
            # now we just execute them all in sequence. The result will be a list of True/False 
            # statements. Note that there is no eval here, these are normal command calls!
            true_false = (tup[0](accessing_obj, self.obj, *tup[1], **tup[2]) for tup in func_tup)
            # we now input these True/False list into the evalstring, which combines them with 
            # AND/OR/NOT in order to get the final result
            return eval(evalstring % tuple(true_false))
        else:
            return default

    def check_lockstring(self, accessing_obj, accessed_obj, lockstring):
        """
        Do a direct check against a lockstring ('atype:func()..'), without any
        intermediary storage on the accessed object (this can be left
        to None if the lock functions called don't access it). atype can also be 
        put to a dummy value since no lock selection is made.
        """
        if (hasattr(accessing_obj, 'player') and hasattr(accessing_obj.player, 'user') 
            and hasattr(accessing_obj.player.user, 'is_superuser') 
            and accessing_obj.player.user.is_superuser):
            return True  # always grant access to the superuser.        
        locks = self. _parse_lockstring(lockstring)
        for access_type in locks:
            evalstring, func_tup, raw_string = locks[access_type]            
            true_false = (tup[0](accessing_obj, self.obj, *tup[1], **tup[2]) for tup in func_tup)
            return eval(evalstring % tuple(true_false))
            

        
def test():
    # testing 

    class TestObj(object):
        pass

    import pdb
    obj1 = TestObj()
    obj2 = TestObj()
    
    #obj1.lock_storage = "owner:dbref(#4);edit:dbref(#5) or perm(Wizards);examine:perm(Builders);delete:perm(Wizards);get:all()"
    #obj1.lock_storage = "cmd:all();admin:id(1);listen:all();send:all()"   
    obj1.lock_storage = "listen:perm(Immortals)"

    pdb.set_trace()
    obj1.locks = LockHandler(obj1)
    obj2.permissions = ["Immortals"]
    obj2.id = 4

    #obj1.locks.add("edit:attr(test)")

    print "comparing obj2.permissions (%s) vs obj1.locks (%s)" % (obj2.permissions, obj1.locks)
    print obj1.locks.check(obj2, 'owner')
    print obj1.locks.check(obj2, 'edit')
    print obj1.locks.check(obj2, 'examine')
    print obj1.locks.check(obj2, 'delete')
    print obj1.locks.check(obj2, 'get')
    print obj1.locks.check(obj2, 'listen')
