"""
This module contains the base Script class that all
scripts are inheriting from.

It also defines a few common scripts. 
"""

from time import time 
from twisted.internet.defer import maybeDeferred
from twisted.internet.task import LoopingCall
from twisted.internet import task 
from src.server.sessionhandler import SESSIONS
from src.typeclasses.typeclass import TypeClass
from src.scripts.models import ScriptDB
from src.comms import channelhandler 
from src.utils import logger

#
# Base script, inherit from Script below instead. 
#
class ScriptClass(TypeClass):
    """
    Base class for scripts
    """

    # private methods 

    def __eq__(self, other):
        """
        This has to be located at this level, having it in the
        parent doesn't work.
        """
        try:
            return other.id == self.id
        except Exception:
            return False 

    def _start_task(self):
        "start task runner"
        #print "_start_task: self.interval:", self.key, self.interval, self.dbobj.db_interval
        self.ndb.twisted_task = LoopingCall(self._step_task)
        self.ndb.twisted_task.start(self.interval, now=not self.start_delay)
        self.ndb.time_last_called = int(time())
    def _stop_task(self):
        "stop task runner"
        try:
            #print "stopping twisted task:", id(self.ndb.twisted_task), self.obj
            self.ndb.twisted_task.stop()            
        except Exception:
            logger.log_trace()
    def _step_err_callback(self, e):
        "callback for runner errors"
        cname = self.__class__.__name__
        estring = "Script %s(#%i) of type '%s': at_repeat() error '%s'." % (self.key, self.id, cname, e.getErrorMessage())
        try:
            self.dbobj.db_obj.msg(estring)
        except Exception:
            pass
        logger.log_errmsg(estring)
    def _step_succ_callback(self):
        "step task runner. No try..except needed due to defer wrap."
        if not self.is_valid():
            self.stop()
            return 
        self.at_repeat()
        repeats = self.dbobj.db_repeats
        if repeats <= 0:
            pass # infinite repeat
        elif repeats == 1:
            self.stop()
            return 
        else:
            self.dbobj.db_repeats -= 1
        self.ndb.time_last_called = int(time())
        self.save()
    def _step_task(self):
        "step task"
        try:            
            d = maybeDeferred(self._step_succ_callback)
            d.addErrback(self._step_err_callback)            
            return d
        except Exception:
            logger.log_trace()        


    def time_until_next_repeat(self):
        """
        Returns the time in seconds until the script will be
        run again. If this is not a stepping script, returns None. 
        This is not used in any way by the script's stepping
        system; it's only here for the user to be able to
        check in on their scripts and when they will next be run. 
        """
        try:
            return max(0, (self.ndb.time_last_called + self.dbobj.db_interval) - int(time()))
        except Exception:
            return None 

    def start(self, force_restart=False):
        """
        Called every time the script is started (for
        persistent scripts, this is usually once every server start)

        force_restart - if True, will always restart the script, regardless
                        of if it has started before. 
                        
        returns 0 or 1 to indicated the script has been started or not. Used in counting.                         
        """
        #print "Script %s (%s) start (active:%s, force:%s) ..." % (self.key, id(self.dbobj), 
        #                                                          self.is_active, force_restart)        

        if self.dbobj.is_active and not force_restart:
            # script already runs and should not be restarted.
            return 0 

        obj = self.obj
        if obj:            
            # check so the scripted object is valid and initalized 
            try:
                dummy = object.__getattribute__(obj, 'cmdset')                
            except AttributeError:
                # this means the object is not initialized.
                self.dbobj.is_active = False
                return 0 
        # try to start the script 
        try:            
            self.dbobj.is_active = True
            self.at_start()
            if self.dbobj.db_interval > 0:
                self._start_task()
            return 1
        except Exception:
            logger.log_trace()
            self.dbobj.is_active = False 
            return 0

    def stop(self, kill=False):
        """
        Called to stop the script from running.
        This also deletes the script. 

        kill - don't call finishing hooks. 
        """
        #print "stopping script %s" % self.key
        #import pdb
        #pdb.set_trace()
        if not kill:
            try:
                self.at_stop()
            except Exception:
                logger.log_trace()
        if self.dbobj.db_interval > 0:
            try:
                self._stop_task()
            except Exception, e:
                logger.log_trace("Stopping script %s(%s)" % (self.key, self.id))
                pass
        try:
            self.dbobj.delete()
        except AssertionError:
            logger.log_trace()
            return 0
        return 1

    # hooks
    def at_script_creation(self):
        "placeholder"
        pass
    def is_valid(self):
        "placeholder"
        pass
    def at_start(self):
        "placeholder."
        pass        
    def at_stop(self):
        "placeholder"
        pass
    def at_repeat(self):
        "placeholder"
        pass


# class ScriptClass(TypeClass):
#     """
#     Base class for all Scripts. 
#     """
    
#     # private methods for handling timers. 

#     def __eq__(self, other):
#         """
#         This has to be located at this level, having it in the
#         parent doesn't work.
#         """
#         if other:
#             return other.id == self.id
#         return False 

#     def _start_task(self):
#         "start the task runner."
#         print "self_interval:", self.interval
#         if self.interval > 0:
#             #print "Starting task runner"
#             start_now = not self.start_delay
#             self.ndb.twisted_task = task.LoopingCall(self._step_task)
#             self.ndb.twisted_task.start(self.interval, now=start_now)          
#             self.ndb.time_last_called = int(time())
#             #self.save()
#     def _stop_task(self):
#         "stop the task runner"
#         if hasattr(self.ndb, "twisted_task"):
#             self.ndb.twisted_task.stop()
#     def _step_task(self):
#         "perform one repeat step of the script"        
#         #print "Stepping task runner (obj %s)" % id(self)
#         #print "Has dbobj: %s" % hasattr(self, 'dbobj') 
#         if not self.is_valid():
#             #the script is not valid anymore. Abort.
#             self.stop()
#             return 
#         try:            
#             self.at_repeat()
#             if self.repeats:
#                 if self.repeats <= 1:
#                     self.stop()
#                     return 
#                 else:
#                     self.repeats -= 1
#             self.ndb.time_last_called = int(time())
#             self.save()                
#         except Exception:
#             logger.log_trace()
#             self._stop_task()

#     def time_until_next_repeat(self):
#         """
#         Returns the time in seconds until the script will be
#         run again. If this is not a stepping script, returns None. 
#         This is not used in any way by the script's stepping
#         system; it's only here for the user to be able to
#         check in on their scripts and when they will next be run. 
#         """
#         if self.interval and hasattr(self.ndb, 'time_last_called'):
#             return max(0, (self.ndb.time_last_called + self.interval) - int(time()))
#         else:
#             return None 

#     def start(self, force_restart=False):
#         """
#         Called every time the script is started (for
#         persistent scripts, this is usually once every server start)

#         force_restart - if True, will always restart the script, regardless
#                         of if it has started before. 
#         """
#         #print "Script %s (%s) start (active:%s, force:%s) ..." % (self.key, id(self.dbobj), 
#         #                                                          self.is_active, force_restart)        
#         if force_restart:
#             self.is_active = False 
            
#         should_start = True 
#         if self.obj:
#             try:
#                 #print "checking  cmdset ... for obj", self.obj
#                 dummy = object.__getattribute__(self.obj, 'cmdset')                
#                 #print "... checked cmdset"
#             except AttributeError:
#                 #print "self.obj.cmdset not found. Setting is_active=False."
#                 self.is_active = False
#                 should_start = False
#         if self.is_active and not force_restart:
#             should_start = False

#         if should_start:
#             #print "... starting."        
#             try:            
#                 self.is_active = True
#                 self.at_start()
#                 self._start_task()
#                 return 1
#             except Exception:
#                 #print ".. error when starting"
#                 logger.log_trace()
#                 self.is_active = False 
#                 return 0
#         else:
#             # avoid starting over. 
#             #print "... Start cancelled (invalid start or already running)."
#             return 0 # this is used by validate() for counting started scripts        
            
#     def stop(self, kill=False):
#         """
#         Called to stop the script from running.
#         This also deletes the script. 

#         kill - don't call finishing hooks. 
#         """
#         #print "stopping script %s" % self.key
#         if not kill:
#             try:
#                 self.at_stop()
#             except Exception:
#                 logger.log_trace()
#         if self.interval:
#             try:
#                 self._stop_task()
#             except Exception:
#                 pass
#         self.is_running = False
#         try:
#             self.delete()
#         except AssertionError:
#             return 0
#         return 1

#     def is_valid(self):
#         "placeholder"
#         pass
#     def at_start(self):
#         "placeholder."
#         pass        
#     def at_stop(self):
#         "placeholder"
#         pass
#     def at_repeat(self):
#         "placeholder"
#         pass


#
# Base Script - inherit from this
#

class Script(ScriptClass):
    """
    This is the class you should inherit from, it implements
    the hooks called by the script machinery.
    """

    def at_script_creation(self):
        """
        Only called once, by the create function.
        """
        self.key = "<unnamed>"           
        self.desc = ""
        self.interval = 0 # infinite
        self.start_delay = False
        self.repeats = 0  # infinite
        self.persistent = False             
    
    def is_valid(self):
        """
        Is called to check if the script is valid to run at this time. 
        Should return a boolean. The method is assumed to collect all needed
        information from its related self.obj.
        """
        return True

    def at_start(self):
        """
        Called whenever the script is started, which for persistent
        scripts is at least once every server start. 
        """
        pass

    def at_repeat(self):
        """
        Called repeatedly if this Script is set to repeat
        regularly. 
        """
        pass
    
    def at_stop(self):
        """
        Called whenever when it's time for this script to stop
        (either because is_valid returned False or )
        """
        pass

    def at_server_restart(self):
        """
        This hook is called whenever the server is shutting down for restart/reboot. 
        If you want to, for example, save non-persistent properties across a restart,
        this is the place to do it. 
        """
        pass

    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully (i.e. not for 
        a restart). 
        """
        pass



# Some useful default Script types used by Evennia. 

class DoNothing(Script):
    "An script that does nothing. Used as default fallback."    
    def at_script_creation(self):    
         "Setup the script"
         self.key = "sys_do_nothing"
         self.desc = "This is a placeholder script."         
    
class CheckSessions(Script):
    "Check sessions regularly."
    def at_script_creation(self):
        "Setup the script"
        self.key = "sys_session_check"
        self.desc = "Checks sessions so they are live."        
        self.interval = 60  # repeat every 60 seconds        
        self.persistent = True            

    def at_repeat(self):
        "called every 60 seconds"
        #print "session check!"
        #print "ValidateSessions run"
        SESSIONS.validate_sessions()

class ValidateScripts(Script):
    "Check script validation regularly"    
    def at_script_creation(self):
        "Setup the script"
        self.key = "sys_scripts_validate"
        self.desc = "Validates all scripts regularly."
        self.interval = 3600 # validate every hour.
        self.persistent = True

    def at_repeat(self):
        "called every hour"        
        #print "ValidateScripts run."
        ScriptDB.objects.validate()

class ValidateChannelHandler(Script):
    "Update the channelhandler to make sure it's in sync." 

    def at_script_creation(self):
        "Setup the script"
        self.key = "sys_channels_validate"
        self.desc = "Updates the channel handler"    
        self.interval = 3700 # validate a little later than ValidateScripts
        self.persistent = True
    
    def at_repeat(self):
        "called every hour+"
        #print "ValidateChannelHandler run."
        channelhandler.CHANNELHANDLER.update()
                
class AddCmdSet(Script):
    """
    This script permanently assigns a command set
    to an object whenever it is started. This is not
    used by the core system anymore, it's here mostly
    as an example. 
    """
    def at_script_creation(self):
        "Setup the script"
        if not self.key:
            self.key = "add_cmdset"
        if not self.desc:
            self.desc = "Adds a cmdset to an object."
        self.persistent = True 

        # this needs to be assigned to upon creation.
        # It should be a string pointing to the right
        # cmdset module and cmdset class name, e.g.  
        # 'examples.cmdset_redbutton.RedButtonCmdSet'        
        # self.db.cmdset = <cmdset_path>
        # self.db.add_default = <bool>

    def at_start(self):
        "Get cmdset and assign it."
        cmdset = self.db.cmdset
        if cmdset:
            if self.db.add_default:
                self.obj.cmdset.add_default(cmdset)
            else:
                self.obj.cmdset.add(cmdset)
        
    def at_stop(self):
        """
        This removes the cmdset when the script stops
        """
        cmdset = self.db.cmdset        
        if cmdset:
            if self.db.add_default:
                self.obj.cmdset.delete_default()
            else:
                self.obj.cmdset.delete(cmdset)
