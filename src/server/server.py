"""
This module implements the main Evennia server process, the core of
the game engine. 

This module should be started with the 'twistd' executable since it
sets up all the networking features.  (this is done automatically
by game/evennia.py).

"""
import time
import sys
import os
import signal
if os.name == 'nt':
    # For Windows batchfile we need an extra path insertion here.
    sys.path.insert(0, os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.web import server, static
from django.db import connection
from django.conf import settings

from src.scripts.models import ScriptDB

from src.server.models import ServerConfig
from src.server import initial_setup

from src.utils.utils import get_evennia_version
from src.comms import channelhandler
from src.server.sessionhandler import SESSIONS

SERVER_RESTART = os.path.join(settings.GAME_DIR, 'server.restart')

#------------------------------------------------------------
# Evennia Server settings 
#------------------------------------------------------------

SERVERNAME = settings.SERVERNAME
VERSION = get_evennia_version()

AMP_ENABLED = True 
AMP_HOST = settings.AMP_HOST
AMP_PORT = settings.AMP_PORT


#------------------------------------------------------------
# Evennia Main Server object 
#------------------------------------------------------------
class Evennia(object):

    """
    The main Evennia server handler. This object sets up the database and
    tracks and interlinks all the twisted network services that make up
    evennia.
    """    
    
    def __init__(self, application):
        """
        Setup the server. 

        application - an instantiated Twisted application

        """        
        sys.path.append('.')

        # create a store of services
        self.services = service.IServiceCollection(application)
        self.amp_protocol = None # set by amp factory
        self.sessions = SESSIONS
        self.sessions.server = self
        
        print '\n' + '-'*50

        # Database-specific startup optimizations.
        self.sqlite3_prep()
                    
        # Run the initial setup if needed 
        self.run_initial_setup()

        self.start_time = time.time()

        # initialize channelhandler
        channelhandler.CHANNELHANDLER.update()
        
        # init all global scripts

        ScriptDB.objects.validate(init_mode=True)

        # Make info output to the terminal.         
        self.terminal_output()

        print '-'*50        

        # set a callback if the server is killed abruptly, 
        # by Ctrl-C, reboot etc.
        #reactor.addSystemEventTrigger('before', 'shutdown', self.shutdown, _abrupt=True)

        self.game_running = True
                
    # Server startup methods

    def sqlite3_prep(self):
        """
        Optimize some SQLite stuff at startup since we
        can't save it to the database.
        """
        if (settings.DATABASE_ENGINE == "sqlite3"
            or hasattr(settings, 'DATABASE')   
            and settings.DATABASE.get('ENGINE', None) 
                == 'django.db.backends.sqlite3'):            
            cursor = connection.cursor()
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA synchronous=OFF")
            cursor.execute("PRAGMA count_changes=OFF")
            cursor.execute("PRAGMA temp_store=2")

    def run_initial_setup(self):
        """
        This attempts to run the initial_setup script of the server.
        It returns if this is not the first time the server starts.
        """
        last_initial_setup_step = ServerConfig.objects.conf('last_initial_setup_step')
        if not last_initial_setup_step:
            # None is only returned if the config does not exist,
            # i.e. this is an empty DB that needs populating.
            print ' Server started for the first time. Setting defaults.'
            initial_setup.handle_setup(0)
            print '-'*50
        elif int(last_initial_setup_step) >= 0:
            # a positive value means the setup crashed on one of its
            # modules and setup will resume from this step, retrying
            # the last failed module. When all are finished, the step
            # is set to -1 to show it does not need to be run again.
            print ' Resuming initial setup from step %s.' % \
                last_initial_setup_step  
            initial_setup.handle_setup(int(last_initial_setup_step))
            print '-'*50


    def terminal_output(self):
        """
        Outputs server startup info to the terminal.
        """
        print ' %s Server (%s) started.' % (SERVERNAME, VERSION)       
        print '  amp (Portal): %s' % AMP_PORT

    def set_restart_mode(self, mode=None):
        """
        This manages the flag file that tells the runner if the server should
        be restarted or is shutting down. Valid modes are True/False and None. 
        If mode is None, no change will be done to the flag file.
        """
        if mode == None:
            return 
        f = open(SERVER_RESTART, 'w')
        f.write(str(mode))
        f.close()

    def shutdown(self, restart=None):
        """
        Shuts down the server from inside it. 

        restart - True/False sets the flags so the server will be
                  restarted or not. If None, the current flag setting
                  (set at initialization or previous runs) is used.
        """
        self.set_restart_mode(restart)
        reactor.callLater(0, reactor.stop)


#------------------------------------------------------------
#
# Start the Evennia game server and add all active services
#
#------------------------------------------------------------

# Tell the system the server is starting up; some things are not available yet
ServerConfig.objects.conf("server_starting_mode", True) 

# twistd requires us to define the variable 'application' so it knows
# what to execute from.
application = service.Application('Evennia')

# The main evennia server program. This sets up the database 
# and is where we store all the other services.
EVENNIA = Evennia(application)

# The AMP protocol handles the communication between
# the portal and the mud server. Only reason to ever deactivate
# it would be during testing and debugging. 

if AMP_ENABLED: 

    from src.server import amp

    factory = amp.AmpServerFactory(EVENNIA)
    amp_service = internet.TCPServer(AMP_PORT, factory)
    amp_service.setName("EvenniaPortal")
    EVENNIA.services.addService(amp_service)

# clear server startup mode
ServerConfig.objects.conf("server_starting_mode", delete=True)

if os.name == 'nt':
    # Windows only: Set PID file manually
    f = open(os.path.join(settings.GAME_DIR, 'server.pid'), 'w')
    f.write(str(os.getpid()))
    f.close()
