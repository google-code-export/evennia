"""
The custom manager for Scripts.
"""

from src.typeclasses.managers import TypedObjectManager
from src.typeclasses.managers import returns_typeclass_list

VALIDATE_ITERATION = 0

class ScriptManager(TypedObjectManager):
    """
    ScriptManager get methods
    """
    @returns_typeclass_list
    def get_all_scripts_on_obj(self, obj, key=None):
        """
        Returns as result all the Scripts related to a particular object
        """
        if not obj:
            return []
        scripts = self.filter(db_obj=obj)
        if key:           
            return scripts.filter(db_key=key)
        return scripts 

    @returns_typeclass_list
    def get_all_scripts(self, key=None):
        """
        Return all scripts, alternative only
        scripts with a certain key/dbref or path. 
        """
        if key:
            dbref = self.dbref(key)
            if dbref:
                # try to see if this is infact a dbref
                script = self.dbref_search(dbref)
                if script:
                    return script
            # not a dbref. Normal key search
            scripts = self.filter(db_key=key)
        else:
            scripts = list(self.all())
        return scripts

    def delete_script(self, dbref):
        """
        This stops and deletes a specific script directly
        from the script database. This might be
        needed for global scripts not tied to
        a specific game object. 
        """
        scripts = self.get_id(dbref)
        for script in scripts:
            script.stop()

    def remove_non_persistent(self, obj=None):
        """
        This cleans up the script database of all non-persistent
        scripts, or only those on obj. It is called every time the server restarts
        and 
        """
        if obj:
            to_stop = self.filter(db_persistent=False, db_obj=obj)
        else:
            to_stop = self.filter(db_persistent=False)
        nr_deleted = to_stop.count()
        for script in to_stop.filter(db_is_active=True):
            script.stop()
        for script in to_stop.filter(db_is_active=False):
            script.delete() 
        return nr_deleted

    def validate(self, scripts=None, obj=None, key=None, dbref=None, 
                 init_mode=False):
        """
        This will step through the script database and make sure
        all objects run scripts that are still valid in the context
        they are in. This is called by the game engine at regular
        intervals but can also be initiated by player scripts. 
        If key and/or obj is given, only update the related
        script/object.

        Only one of the arguments are supposed to be supplied
        at a time, since they are exclusive to each other.
        
        scripts = a list of scripts objects obtained somewhere.
        obj = validate only scripts defined on a special object.
        key = validate only scripts with a particular key
        dbref = validate only the single script with this particular id. 

        init_mode - This is used during server upstart and can have
             three values: False (no init mode), "shutdown" or
             "restart".  The latter two depends on how the server was
             shut down.  In restart mode, "non-permanent" scripts will
             survive, in shutdown they will not.
                    
        This method also makes sure start any scripts it validates,
        this should be harmless, since already-active scripts
        have the property 'is_running' set and will be skipped. 
        """

        # we store a variable that tracks if we are calling a 
        # validation from within another validation (avoids 
        # loops). 

        global VALIDATE_ITERATION        
        if VALIDATE_ITERATION > 0:
            # we are in a nested validation. Exit.
            VALIDATE_ITERATION -= 1
            return None, None 
        VALIDATE_ITERATION += 1

        # not in a validation - loop. Validate as normal.
        
        nr_started = 0
        nr_stopped = 0        

        if init_mode == 'shutdown':
            # special mode when server starts or object logs in. 
            # This deletes all non-persistent scripts from database            
            nr_stopped += self.remove_non_persistent(obj=obj)
            # turn off the activity flag for all remaining scripts
            scripts = self.get_all_scripts()
            for script in scripts:
                script.dbobj.is_active = False 
       
        elif not scripts:
            # normal operation 
            if dbref and self.dbref(dbref):
                scripts = self.get_id(dbref)
            elif obj:
                scripts = self.get_all_scripts_on_obj(obj, key=key)            
            else:
                scripts = self.get_all_scripts(key=key) #self.model.get_all_cached_instances()

        if not scripts:
            # no scripts available to validate
            VALIDATE_ITERATION -= 1
            return None, None

        #print "scripts to validate: [%s]" % (", ".join(script.key for script in scripts))        
        for script in scripts:
            if script.is_valid():
                #print "validating %s (%i) (init_mode=%s)" % (script.key, id(script.dbobj), init_mode)                                
                nr_started += script.start(force_restart=init_mode) 
                #print "back from start. nr_started=", nr_started
            else:
                script.stop()
                nr_stopped += 1
        VALIDATE_ITERATION -= 1
        return nr_started, nr_stopped
            
    @returns_typeclass_list
    def script_search(self, ostring, obj=None, only_timed=False):
        """
        Search for a particular script.
        
        ostring - search criterion - a script ID or key
        obj - limit search to scripts defined on this object
        only_timed - limit search only to scripts that run
                     on a timer.         
        """

        ostring = ostring.strip()
        
        dbref = self.dbref(ostring)
        if dbref:
            # this is a dbref, try to find the script directly
            dbref_match = self.dbref_search(dbref)
            if dbref_match:
                ok = True 
                if obj and obj != dbref_match.obj:
                    ok = False
                if only_timed and dbref_match.interval:
                    ok = False 
                if ok:
                    return [dbref_match]
        # not a dbref; normal search
        scripts = self.filter(db_key__iexact=ostring)
        
        if obj:
            scripts = scripts.exclude(db_obj=None).filter(db_obj__db_key__iexact=ostring)
        if only_timed:
            scripts = scripts.exclude(interval=0)
        return scripts

    def copy_script(self, original_script, new_key=None, new_obj=None, new_locks=None):
        """
        Make an identical copy of the original_script
        """

        typeclass = original_script.typeclass_path
        if not new_key:
            new_key = original_script.key
        if not new_obj:
            new_obj = original_script.obj
        if not new_locks:
            new_locks = original_script.db_lock_storage

        from src.utils import create
        new_script = create.create_script(typeclass, key=new_key, obj=new_obj, locks=new_locks, autostart=True)
        return new_script
