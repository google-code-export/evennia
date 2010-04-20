import time
import sys
from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.python import rebuild
from django.db import connection
from django.conf import settings
from src.config.models import ConfigValue
from src.session import SessionProtocol
from src import events
from src import logger
from src import comsys
from src import session_mgr
from src import alias_mgr
from src import cmdtable
from src import initial_setup
from src.util import functions_general
from src import scheduler
from src import gametime

class EvenniaService(service.Service):
    def __init__(self):
        # Holds the TCP services.
        self.service_collection = None
        self.game_running = True
        sys.path.append('.')

        # Database-specific startup optimizations.
        if settings.DATABASE_ENGINE == "sqlite3":
            self.sqlite3_prep()

        # Begin startup debug output.
        print '-'*50

        firstrun = False 
        try:
            # If this fails, this is an empty DB that needs populating.
            ConfigValue.objects.get_configvalue('game_firstrun')
        except ConfigValue.DoesNotExist:            
            print ' Game started for the first time, setting defaults.'
            firstrun = True
            initial_setup.handle_setup()
            
        self.start_time = time.time()

        print ' %s started on port(s):' % (ConfigValue.objects.get_configvalue('site_name'),)
        for port in settings.GAMEPORTS:
            print '  * %s' % (port)
        
        # Populate the command table.
        self.load_command_table()
        # Cache the aliases from the database for quick access.
        alias_mgr.load_cmd_aliases()
        
        # disabled temporarily until cache is replaced
        if False and not firstrun:
            # Find out how much offset the timer is (due to being
            # offline).
            downtime_sync = gametime.time_last_sync()
            
            # Sync the in-game timer.
            gametime.time_save()
                        
            # Fire up the event scheduler.        
            event_cache = cache.get_pcache("_persistent_event_cache")                
            if event_cache and type(event_cache) == type(list()):            
                for event in event_cache:
                    # We adjust the last executed time to account for offline time.
                    # If we don't, the events will be confused since their last
                    # executed time is further away than their firing interval. 
                    event.time_last_executed = event.time_last_executed + downtime_sync
                    scheduler.add_event(event)

        print '-'*50
 
        #print "In game timer started."
        #from game.gamesrc.MudTime import incrementTick
        #from twisted.internet.task import LoopingCall
        #repeater = LoopingCall(incrementTick)
        #repeater.start(.05)
        #logger.log_infomsg("Rob's temp in game timer started")



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
            except ImportError, e:
                logger.log_errmsg("ERROR: Unable to load command module: %s (%s)" % (cmd_mod, e))
                continue

    """
    BEGIN GENERAL METHODS
    """
    def shutdown(self, message='The server has been shutdown. Please check back soon.'):
        """
        Gracefully disconnect everyone and kill the reactor.
        """
        gametime.time_save()
        logger.log_infomsg("Persistent cache and time saved prior to shutdown.")
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
        s = []
        for mod_str in cmd_modules:
            if not sys.modules.has_key(mod_str):
                comsys.cemit_mudinfo("... %s not reloadable." % mod_str)
                logger.log_errmsg("Module %s not reloadable." % mod_str)
            else:
                mod = sys.modules[mod_str]
                s.append(mod_str)
                try:
                    rebuild.rebuild(mod)
                except:
                    comsys.cemit_mudinfo("... Error reloading %s!" % mod_str)
                    raise                        
            
        logger.log_infomsg("%s reloaded %i modules: %s" % (source_object, len(s), s))
        
    def reload_aliases(self, source_object=None):
        """
        Reload the aliases from the Alias model into the local table.
        """
        alias_mgr.load_cmd_aliases()

    def getEvenniaServiceFactory(self):
        f = protocol.ServerFactory()
        f.protocol = SessionProtocol
        f.server = self
        return f

    def start_services(self, application):
        """
        Starts all of the TCP services.
        """
        self.service_collection = service.IServiceCollection(application)
        for port in settings.GAMEPORTS:
            evennia_server = internet.TCPServer(port, self.getEvenniaServiceFactory())
            evennia_server.setName('Evennia%s' %port)
            evennia_server.setServiceParent(self.service_collection)
        
        if settings.IMC2_ENABLED:
            from src.imc2.connection import IMC2ClientFactory
            from src.imc2 import events as imc2_events
            imc2_factory = IMC2ClientFactory()
            svc = internet.TCPClient(settings.IMC2_SERVER_ADDRESS, 
                                     settings.IMC2_SERVER_PORT, 
                                     imc2_factory)
            svc.setName('IMC2')
            svc.setServiceParent(self.service_collection)
            imc2_events.add_events()

        if settings.IRC_ENABLED:
            from src.irc.connection import IRC_BotFactory
            irc = internet.TCPClient(settings.IRC_NETWORK, 
                                     settings.IRC_PORT, 
                                     IRC_BotFactory(settings.IRC_CHANNEL,
                                                    settings.IRC_NETWORK,
                                                    settings.IRC_NICKNAME))            
            irc.setName("%s:%s" % ("IRC",settings.IRC_CHANNEL))
            irc.setServiceParent(self.service_collection)

        if settings.RTCLIENT_ENABLED:
           from twisted.application import strports
           from nevow import appserver
           from game.gamesrc.teltola import teltola

           teltolaResource = teltola.createResource()
           site = appserver.NevowSite(teltolaResource)
           #application = service.Application("teltola")
           #strports.service("2300", site).setServiceParent(application)
           strports.service("2300", site).setServiceParent(self.service_collection)
           #teltolaResource.setServiceParent(self.service_collection)
           teltolaResource.serviceParent = self.service_collection

application = service.Application('Evennia')
mud_service = EvenniaService()
mud_service.start_services(application)

