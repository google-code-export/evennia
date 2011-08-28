#!/usr/bin/env python
"""

This runner is controlled by evennia.py and should normally not be launched directly.
 It manages the two main Evennia processes (Server and Portal) and most importanly runs a 
passive, threaded loop that makes sure to restart Server whenever it shuts down. 


"""
import os  
import sys
from optparse import OptionParser
from subprocess import Popen, call
import Queue, thread, subprocess

#
# System Configuration
# 


SERVER_PIDFILE = "server.pid"
PORTAL_PIDFILE = "portal.pid"

# Set the Python path up so we can get to settings.py from here.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'game.settings'

if not os.path.exists('settings.py'):

    print "No settings.py file found. Run evennia.py to create it."
    sys.exit()
                     
# Get the settings
from django.conf import settings

# Setup access of the evennia server itself
SERVER_PY_FILE = os.path.join(settings.SRC_DIR, 'server/server.py')
PORTAL_PY_FILE = os.path.join(settings.SRC_DIR, 'server/portal.py')

# Get logfile names
SERVER_LOGFILE = settings.SERVER_LOG_FILE
PORTAL_LOGFILE = settings.PORTAL_LOG_FILE

# Add this to the environmental variable for the 'twistd' command.
currpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] += (":%s" % currpath)
else:
    os.environ['PYTHONPATH'] = currpath

TWISTED_BINARY = 'twistd' 
if os.name == 'nt':
    TWISTED_BINARY = 'twistd.bat'
    err = False 
    try:
        import win32api  # Test for for win32api
    except ImportError:
        err = True 
    if not os.path.exists(TWISTED_BINARY):
        err = True 
    if err:
        print "Twisted binary for Windows is not ready to use. Please run evennia.py."
        sys.exit()


# Functions 

def get_pid(pidfile):
    """
    Get the PID (Process ID) by trying to access
    an PID file. 
    """
    pid = None 
    if os.path.exists(pidfile):
        f = open(pidfile, 'r')
        pid = f.read()
    return pid 


def cycle_logfile(logfile):
    """
    Move the old log files to <filename>.old

    """    
    logfile_old = logfile + '.old'
    if os.path.exists(logfile):
        # Cycle the old logfiles to *.old
        if os.path.exists(logfile_old):
            # E.g. Windows don't support rename-replace
            os.remove(logfile_old)
        os.rename(logfile, logfile_old)

    logfile = settings.HTTP_LOG_FILE.strip()
    logfile_old = logfile + '.old'
    if os.path.exists(logfile):
        # Cycle the old logfiles to *.old
        if os.path.exists(logfile_old):
            # E.g. Windows don't support rename-replace
            os.remove(logfile_old)
        os.rename(logfile, logfile_old)    


# Start program management 

SERVER = None
PORTAL = None 

PORTAL_INTERACTIVE = False

def start_services(server_argv, portal_argv):
    """
    This calls a threaded loop that launces the Portal and Server
    and then restarts them when they finish. 
    """
    global SERVER, PORTAL 

    processes = Queue.Queue()

    def server_waiter(queue):                
        try: 
            rc = Popen(server_argv).wait()
        except Exception, e:
            print "Server process error: %s" % e
        queue.put(("server_stopped", rc)) # this signals the controller that the program finished

    def portal_waiter(queue):                
        try: 
            rc = Popen(portal_argv).wait()
        except Exception, e:
            print "Portal process error: %s " % e
        queue.put(("portal_stopped", rc)) # this signals the controller that the program finished
                    
    if server_argv:
        # start server as a reloadable thread 
        SERVER = thread.start_new_thread(server_waiter, (processes, ))

    if portal_argv: 
        if PORTAL_INTERACTIVE:
            # start portal as interactive, reloadable thread 
            PORTAL = thread.start_new_thread(portal_waiter, (processes, ))
        else:
            # normal operation: start portal as a daemon; we don't care to monitor it for restart
            PORTAL = Popen(portal_argv)
            if not SERVER:
                # if portal is daemon and no server is running, we have no reason to continue to the loop.
                return 

    # Reload loop 
    while True:
        
        # this blocks until something is actually returned.
        message, rc = processes.get()                    
        
        # restart only if process stopped cleanly
        if message == "server_stopped" and int(rc) == 0:
            print "Evennia Server stopped. Restarting ..."
            SERVER = thread.start_new_thread(server_waiter, (processes, ))
            continue 

        # normally the portal is not reloaded since it's run as a daemon.
        if PORTAL_INTERACTIVE and message == "portal_stopped" and int(rc) == 0:
            print "Evennia Portal stopped in interactive mode. Restarting ..."
            PORTAL = thread.start_new_thread(portal_waiter, (processes, ))                            
            continue 
        break 

# Setup signal handling

def main():
    """
    This handles 
    """
    
    parser = OptionParser(usage="%prog [options] start",
                          description="This runner should normally *not* be called directly - it is called automatically from the evennia.py main program. It manages the Evennia game server and portal processes an hosts a threaded loop to restart the Server whenever it is stopped (this constitues Evennia's reload mechanism).")
    parser.add_option('-s', '--noserver', action='store_true', 
                      dest='noserver', default=False,
                      help='Do not start Server process')
    parser.add_option('-p', '--noportal', action='store_true', 
                      dest='noportal', default=False,
                      help='Do not start Portal process')
    parser.add_option('-i', '--iserver', action='store_true', 
                      dest='iserver', default=False,
                      help='output server log to stdout instead of logfile')
    parser.add_option('-d', '--iportal', action='store_true', 
                      dest='iportal', default=False,
                      help='output portal log to stdout. Does not make portal a daemon.')
    options, args = parser.parse_args()

    if not args or args[0] != 'start':
        # this is so as to not be accidentally launched.
        parser.print_help()
        sys.exit()

    # set up default project calls 
    server_argv = [TWISTED_BINARY, 
                   '-n',
                   '--logfile=%s' % SERVER_LOGFILE,
                   '--pidfile=%s' % SERVER_PIDFILE, 
                   '--python=%s' % SERVER_PY_FILE]
    portal_argv = [TWISTED_BINARY,
                   '--logfile=%s' % PORTAL_LOGFILE,
                   '--pidfile=%s' % PORTAL_PIDFILE, 
                   '--python=%s' % PORTAL_PY_FILE]    
    # Server 
    
    pid = get_pid(SERVER_PIDFILE)
    if pid and not options.noserver:
            print "Evennia Server is already running as process %s. Not restarted." % pid
            options.noserver = True
    if options.noserver:
        server_argv = None 
    else:
        if options.iserver:
            # don't log to server logfile
            del server_argv[2]
            print "Starting Evennia Server (output to stdout)."
        else:
            print "Starting Evennia Server (output to server logfile)."
        cycle_logfile(SERVER_LOGFILE)

    # Portal 

    pid = get_pid(PORTAL_PIDFILE)
    if pid and not options.noportal:
        print "Evennia Portal is already running as process %s. Not restarted." % pid    
        options.noportal = True             
    if options.noportal:
        portal_argv = None 
    else:
        if options.iportal:
            # make portal interactive
            portal_argv[1] = '-n'
            PORTAL_INTERACTIVE = True                     
            print "Starting Evennia Portal in non-Daemon mode (output to stdout)."
        else:
            print "Starting Evennia Portal in Daemon mode (output to portal logfile)."            
        cycle_logfile(PORTAL_LOGFILE)

    # Start processes
    start_services(server_argv, portal_argv)
          
if __name__ == '__main__':
    from src.utils.utils import check_evennia_dependencies
    if check_evennia_dependencies():
        main()
