#!/usr/bin/env python
"""
EVENNIA SERVER STARTUP SCRIPT

Sets the appropriate environmental variables and launches the server
and portal through the runner. Run without arguments to get a
menu. Run the script with the -h flag to see usage information.

"""
import os
import sys, signal
from optparse import OptionParser
from subprocess import Popen, call

HELPENTRY = \
"""
                                                 (version %s) 

This program launches Evennia with various options. You can access all
this functionality directly from the command line; for example option
five (restart server) would be "evennia.py restart server".  Use
"evennia.py -h" for command line options.

Evennia consists of two separate programs that both must be running
for the game to work as it should:

Portal - the connection to the outside world (via telnet, web, ssh
         etc). This is normally running as a daemon and don't need to
         be reloaded unless you are debugging a new connection
         protocol. As long as this is running, players won't loose
         their connection to your game. Only one instance of Portal
         will be started, more will be ignored.
Server - the game server itself. This will often need to be reloaded
         as you develop your game. The Portal will auto-connect to the
         Server whenever the Server activates. We will also make sure
         to automatically restart this whenever it is shut down (from
         here or from inside the game or via task manager etc). Only
         one instance of Server will be started, more will be ignored.

In a production environment you will want to run with the default
option (1), which runs as much as possible as a background
process. When developing your game it is however convenient to
directly see tracebacks on standard output, so starting with options
2-4 may be a good bet. As you make changes to your code, reload the
server (option 5) to make it available to users.
"""

MENU = \
"""
+---------------------------------------------------------------------------+
|                                                                           |
|                    Welcome to the Evennia launcher!                       |
|                                                                           |
|                Pick an option below. Use 'h' to get help.                 |
|                                                                           |
+--- Starting (will not restart already running processes) -----------------+
|                                                                           |
|  1) (default):      Start Server and Portal. Portal starts in daemon mode.|
|                     All output is to logfiles.                            |
|  2) (game debug):   Start Server and Portal. Portal starts in daemon mode.|
|                     Server outputs to stdout instead of logfile.          |
|  3) (portal debug): Start Server and Portal. Portal starts in non-daemon  |
|                     mode (can be reloaded) and logs to stdout.            |
|  4) (full debug):   Start Server and Portal. Portal starts in non-daemon  |
|                     mode (can be reloaded). Both log to stdout.           |
|                                                                           |
+--- Restarting (must first be started) ------------------------------------+
|                                                                           |
|  5) Restart/reload the Server                                             |
|  6) Restart/reload the Portal (only works in non-daemon mode. If running  |
|       in daemon mode, Portal needs to be restarted manually (option 1-4)) |
|                                                                           |
+--- Stopping (must first be started) --------------------------------------+
|                                                                           |
|  7) Stopping both Portal and Server. Server will not restart.             |
|  8) Stopping only Server. Server will not restart.                        |
|  9) Stopping only Portal.                                                 |
|                                                                           |
+---------------------------------------------------------------------------+
|  h) Help                                                                  |
|  q) Quit                                                                  |
+---------------------------------------------------------------------------+
"""


#
# System Configuration and setup
#


SERVER_PIDFILE = "server.pid"
PORTAL_PIDFILE = "portal.pid"

# Set the Python path up so we can get to settings.py from here.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'game.settings'

if not os.path.exists('settings.py'):
    # make sure we have a settings.py file.
    print "    No settings.py file found. Launching manage.py ..."

    import game.manage

    print """
    Now configure Evennia by editing your new settings.py file.
    If you haven't already, you should also create/configure the
    database with 'python manage.py syncdb' before continuing.

    When you are ready, run this program again to start the server."""
    sys.exit()

# Get the settings
from django.conf import settings

from src.utils.utils import get_evennia_version
EVENNIA_VERSION = get_evennia_version()

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
    # Windows needs more work to get the correct binary
    try:
        # Test for for win32api
        import win32api
    except ImportError:
        print """
    ERROR: Unable to import win32api, which Twisted requires to run.
    You may download it from:

    http://sourceforge.net/projects/pywin32
      or
    http://starship.python.net/crew/mhammond/win32/Downloads.html"""
        sys.exit()

    if not os.path.exists('twistd.bat'):
        # Test for executable twisted batch file. This calls the twistd.py
        # executable that is usually not found on the path in Windows.
        # It's not enough to locate scripts.twistd, what we want is the
        # executable script C:\PythonXX/Scripts/twistd.py. Alas we cannot
        # hardcode this location since we don't know if user has Python
        # in a non-standard location, so we try to figure it out.
        from twisted.scripts import twistd
        twistd_path = os.path.abspath(
            os.path.join(os.path.dirname(twistd.__file__),
                         os.pardir, os.pardir, os.pardir, os.pardir,
                         'scripts', 'twistd.py'))
        bat_file = open('twistd.bat','w')
        bat_file.write("@\"%s\" \"%s\" %%*" % (sys.executable, twistd_path))
        bat_file.close()
        print """
    INFO: Since you are running Windows, a file 'twistd.bat' was
    created for you. This is a simple batch file that tries to call
    the twisted executable. Evennia determined this to be:

       %s

    If you run into errors at startup you might need to edit
    twistd.bat to point to the actual location of the Twisted
    executable (usually called twistd.py) on your machine.

    This procedure is only done once. Run evennia.py again when you
    are ready to start the server.
    """ % twistd_path
        sys.exit()

    TWISTED_BINARY = 'twistd.bat'


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

def del_pid(pidfile):
    """
    The pidfile should normally be removed after a process has finished, but
    when sending certain signals they remain, so we need to clean them manually.
    """
    if os.path.exists(pidfile):
        os.remove(pidfile)

def kill(pidfile, signal=signal.SIGINT, succmsg="", errmsg="", clean=False):
    """
    Send a kill signal to a process based on PID. A customized success/error
    message will be returned. If clean=True, the system will attempt to manually
    remove the pid file.
    """
    pid = get_pid(pidfile)
    if pid:
        if os.name == 'nt' and sys.version < "2.7":
            print "Sorry, Windows requires Python 2.7 or higher for this operation."
            return
        try:
            os.kill(int(pid), signal)
        except OSError:
            print "Process %s could not be signalled. The PID file '%s' seems stale. Try removing it." % (pid, pidfile)
            return
        print succmsg
        if clean:
            del_pid(pidfile)
        return
    print errmsg

def run_menu():
    """
    This launches an interactive menu.
    """

    cmdstr = ["python", "runner.py"]

    while True:
        # menu loop

        print MENU
        inp = raw_input(" option > ")

        # quitting and help
        if inp.lower() == 'q':
            sys.exit()
        elif inp.lower() == 'h':
            print HELPENTRY % EVENNIA_VERSION
            raw_input("press <return> to continue ...")
            continue

        # options
        try:
            inp = int(inp)
        except ValueError:
            print "Not a valid option."
            continue
        errmsg = "The %s does not seem to be running."
        if inp < 5:
            if inp == 1:
                pass # default operation
            elif inp == 2:
                cmdstr.extend(['--iserver'])
            elif inp == 3:
                cmdstr.extend(['--iportal'])
            elif inp == 4:
                cmdstr.extend(['--iserver', '--iportal'])
            return cmdstr
        elif inp < 10:
            if inp == 5:
                kill(SERVER_PIDFILE, signal.SIGINT, "Server restarted.", errmsg % "Server")
            elif inp == 6:
                kill(PORTAL_PIDFILE, signal.SIGINT, "Portal restarted (or stopped if in daemon mode).", errmsg % "Portal")
            elif inp == 7:
                kill(PORTAL_PIDFILE, signal.SIGQUIT, "Stopped Server.", errmsg % "Server", clean=True)
                kill(SERVER_PIDFILE, signal.SIGQUIT, "Stopped Portal.", errmsg % "Portal", clean=True)
            elif inp == 8:
                kill(PORTAL_PIDFILE, signal.SIGQUIT, "Stopped Server.", errmsg % "Server", clean=True)
            elif inp == 9:
                kill(SERVER_PIDFILE, signal.SIGQUIT, "Stopped Portal.", errmsg % "Portal", clean=True)
            return 
        else:
            print "Not a valid option."
    return None


def handle_args(options, mode, service):
    """
    Handle argument options given on the command line.

    options - parsed object for command line
    mode - str; start/stop etc
    service - str; server, portal or all
    """

    inter = options.interactive
    cmdstr = ["python", "runner.py"]
    errmsg = "The %s does not seem to be running."

    if mode == 'start':
        # starting one or many services
        if service == 'server':
            if inter:
                cmdstr.append('--iserver')
            cmdstr.append('--noportal')
        elif service == 'portal':
            if inter:
                cmdstr.append('--iportal')
            cmdstr.append('--noserver')
        else: # all
            if inter:
                cmdstr.extend(['--iserver', '--iportal'])
        return cmdstr

    elif mode == 'restart':
        # restarting services
        if service == 'server':
            kill(SERVER_PIDFILE, signal.SIGINT, "Server restarted.", errmsg % 'Server')
        elif service == 'portal':
            print "Note: Portal usually don't need to be restarted unless you are debugging in interactive mode."
            print "If Portal was running in default Daemon mode, it cannot be restarted. In that case you have "
            print "to restart it manually with 'evennia.py start portal'"
            kill(PORTAL_PIDFILE, signal.SIGINT, "Portal restarted (or stopped, if it was in daemon mode).", errmsg % 'Portal')
        else: # all
            # default mode, only restart server
            kill(SERVER_PIDFILE, signal.SIGINT, "Server restarted.", errmsg % 'Server')

    elif mode == 'stop':
        # stop processes, avoiding reload
        if service == 'server':
            kill(SERVER_PIDFILE, signal.SIGQUIT, "Server stopped.", errmsg % 'Server', clean=True)
        elif service == 'portal':
            kill(PORTAL_PIDFILE, signal.SIGQUIT, "Portal stopped.", errmsg % 'Portal', clean=True)
        else:
            kill(SERVER_PIDFILE, signal.SIGQUIT, "Server stopped.", errmsg % 'Server', clean=True)
            kill(PORTAL_PIDFILE, signal.SIGQUIT, "Portal stopped.", errmsg % 'Portal', clean=True)
    return None

def main():
    """
    This handles command line input.
    """

    parser = OptionParser(usage="%prog [-i] [menu|start|restart|stop [server|portal|all]]",
                          description="This is the main Evennia launcher. It manages the parts of Evennia that need to be running, notably the Evennia Server and Portal. Default is to operate on all services. Use --interactive together with start to launch services as 'interactive' (outputting to stdout rather than to their respective log files and avoid starting as daemons). No arguments displays a menu.")
    parser.add_option('-i', '--interactive', action='store_true', dest='interactive', default=False, help='Start given processes in interactive mode.')
    options, args = parser.parse_args()
    inter = options.interactive

    if not args:
        mode = "menu"
        service = 'all'
    if args:
        mode = args[0]
        service = "all"
    if len(args) > 1:
        service = args[1]

    if mode not in ['menu', 'start', 'restart', 'stop']:
        print "mode should be none or one of 'menu', 'start', 'restart' or 'stop'."
        sys.exit()
    if  service not in ['server', 'portal', 'all']:
        print "service should be none or 'server', 'portal' or 'all'."
        sys.exit()

    if mode == 'menu':
        # launch menu
        cmdstr = run_menu()
    else:
        # handle command-line arguments
        cmdstr = handle_args(options, mode, service)
    if cmdstr:
        # call the runner. 
        cmdstr.append('start')
        Popen(cmdstr)

if __name__ == '__main__':
    from src.utils.utils import check_evennia_dependencies
    if check_evennia_dependencies():
        main()
