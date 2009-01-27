import time
import sys
from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.python import rebuild
from django.db import connection
from django.conf import settings
from src.config.models import ConfigValue
from src.session import SessionProtocol
from src import scheduler
from src import logger
from src import session_mgr
from src import alias_mgr
from src import cmdtable
from src import initial_setup
from src.util import functions_general

class EvenniaService(service.Service):
    def __init__(self):
        self.game_running = True
        sys.path.append('.')

        # Database-specific startup optimizations.
        if settings.DATABASE_ENGINE == "sqlite3":
            self.sqlite3_prep()

        # Wipe our temporary flags on all of the objects.
        cursor = connection.cursor()
        cursor.execute("UPDATE objects_object SET nosave_flags=''")

        # Begin startup debug output.
        print '-'*50

        try:
            # If this fails, this is an empty DB that needs populating.
            ConfigValue.objects.get_configvalue('game_firstrun')
        except ConfigValue.DoesNotExist:
            print ' Game started for the first time, setting defaults.'
            initial_setup.handle_setup()

        self.start_time = time.time()

        print ' %s started on port(s):' % (ConfigValue.objects.get_configvalue('site_name'),)
        for port in settings.GAMEPORTS:
            print '  * %s' % (port)
        
        # Populate the command table.
        self.load_command_table()
        # Cache the aliases from the database for quick access.
        alias_mgr.load_cmd_aliases()
        
        print '-'*50
        scheduler.start_events()

    """
    BEGIN SERVER STARTUP METHODS
    """
    def sqlite3_prep(self):
        """
        Optimize some SQLite stuff at startup since we can't save it to the
        database.
        """
        cursor = connection.cursor()
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA synchronous=OFF")
        cursor.execute("PRAGMA count_changes=OFF")
        cursor.execute("PRAGMA temp_store=2")
        
    def get_command_modules(self):
        """
        Combines all of the command modules and returns a tuple. Order is
        preserved.
        """
        return settings.COMMAND_MODULES +\
               settings.CUSTOM_COMMAND_MODULES +\
               settings.UNLOGGED_COMMAND_MODULES +\
               settings.CUSTOM_UNLOGGED_COMMAND_MODULES
    
    def load_command_table(self):
        """
        Imports command modules and loads them into the command tables.
        """
        # Combine the tuples of command modules to load.
        cmd_modules = self.get_command_modules()

        # Import the command modules, which populates the command tables.
        for cmd_mod in cmd_modules:
            try:
                __import__(cmd_mod)
            except ImportError:
                logger.log_errmsg("ERROR: Unable to load command module: %s" % cmd_mod)
                continue

    """
    BEGIN GENERAL METHODS
    """
    def shutdown(self, message='The server has been shutdown. Please check back soon.'):
        """
        Gracefully disconnect everyone and kill the reactor.
        """
        session_mgr.announce_all(message)
        session_mgr.disconnect_all_sessions()
        reactor.callLater(0, reactor.stop)

    def reload(self, source_object=None):
        """
        Reload modules that don't have any variables that can be reset.
        For changes to the scheduler, server, or session_mgr modules, a cold
        restart is needed.
        """
        cmd_modules = self.get_command_modules()
        
        for mod_str, mod in sys.modules.items():
            if mod_str in cmd_modules:
                if source_object:
                    source_object.emit_to(" Reloading %s" % mod_str)
                rebuild.rebuild(mod)
        logger.log_infomsg("Modules reloaded by %s." % source_object)

    def getEvenniaServiceFactory(self):
        f = protocol.ServerFactory()
        f.protocol = SessionProtocol
        f.server = self
        return f

    """
    END Server CLASS
    """

application = service.Application('Evennia')
mud_service = EvenniaService()

# Sheet sheet, fire ze missiles!
serviceCollection = service.IServiceCollection(application)
for port in settings.GAMEPORTS:
    internet.TCPServer(port, mud_service.getEvenniaServiceFactory()).setServiceParent(serviceCollection)
