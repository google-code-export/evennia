"""
This module contains classes related to Sessions. session_mgr has the things
needed to manage them.
"""
import time
import sys
from datetime import datetime
from twisted.conch.telnet import StatefulTelnetProtocol
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from util import functions_general
from src.objects.models import Object
from src.channels.models import CommChannel, CommChannelMembership
from src.config.models import ConnectScreen, ConfigValue
from src import comsys
import cmdhandler
import logger
import session_mgr
import ansi

class SessionProtocol(StatefulTelnetProtocol):
    """
    This class represents a player's session. From here we branch down into
    other various classes, please try to keep this one tidy!
    """

    def connectionMade(self):
        """
        What to do when we get a connection.
        """
        self.prep_session()
        logger.log_infomsg('New connection: %s' % self)
        self.cemit_info('New connection: %s' % self)
        session_mgr.add_session(self)
        self.game_connect_screen()

    def getClientAddress(self):
        """
        Returns the client's address and port in a tuple. For example
        ('127.0.0.1', 41917)
        """
        return self.transport.client

    def prep_session(self):
        self.server = self.factory.server
        self.address = self.getClientAddress()
        self.user = None
        self.puppet = None
        self.logged_in = False
        # The time the user last issued a command.
        self.cmd_last = time.time()
        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = time.time()
        # Total number of commands issued.
        self.cmd_total = 0
        # The time when the user connected.
        self.conn_time = time.time()
        self.channels_subscribed = {}

    def disconnectClient(self):
        """
        Manually disconnect the client.
        """
        self.transport.loseConnection()

    def connectionLost(self, reason):
        """
        Execute this when a client abruplty loses their connection.
        """
        logger.log_infomsg('Disconnected: %s' % self)
        self.cemit_info('Disconnected: %s.' % self)
        self.handle_close()
        
    def lineReceived(self, data):
        """
        Any line return indicates a command for the purpose of a MUD. So we take
        the user input and pass it to this session's pobject.
        """
        if self.is_loggedin():
            # Session is logged in, run through the normal object execution.
            # Get the most up to date copy of the Object.
            if self.puppet:
                self.puppet.execute_cmd(data, session=self)
        else:
            # Not logged in, manually execute the command.
            cmdhandler.handle(cmdhandler.Command(None, data, session=self))

    def execute_cmd(self, command_str):
        """
        Sends a command to this session's object for processing.
        """
        self.puppet.pobject.execute_cmd(command_str, session=self)
      
    def count_command(self, silently=False):
        """
        Hit this when the user enters a command in order to update idle timers
        and command counters. If silently is True, the public-facing idle time
        is not updated.
        """
        # Store the timestamp of the user's last command.
        self.cmd_last = time.time()
        if not silently:
            # Increment the user's command counter.
            self.cmd_total += 1
            # Player-visible idle time, not used in idle timeout calcs.
            self.cmd_last_visible = time.time()
            
    def handle_close(self):
        """
        Break the connection and do some accounting.
        """
        if self.puppet:

            #call hook function
            self.puppet.at_disconnect()

            self.puppet.set_flag("CONNECTED", False)
                        
            uaccount = self.puppet.get_user_account()
            uaccount.last_login = datetime.now()
            uaccount.save()
            
        self.disconnectClient()
        self.logged_in = False
        session_mgr.remove_session(self)
        
    def game_connect_screen(self):
        """
        Show the banner screen. Grab from the 'connect_screen' config directive.
        """
        screen = ConnectScreen.objects.get_random_connect_screen()
        buffer = ansi.parse_ansi(screen.text)
        self.msg(buffer)

    def is_loggedin(self):
        """
        Returns a boolean True if the session is logged in.
        """
        try:
            return self.logged_in
        except:
            return False
    
    def login(self, user, puppet):
        """
        After the user has authenticated, handle logging him in.
        """
        self.user = user
        self.puppet = puppet
        self.logged_in = True
        if self.conn_time:
            puppet.at_first_login()
        self.conn_time = time.time()
        
        #session_mgr.disconnect_duplicate_session(self)

        puppet.at_pre_login(self)
        
        logger.log_infomsg("Logged in: %s" % self)
        self.cemit_info('Logged in: %s' % self)
        
        # Update their account's last login time.
        user.last_login = datetime.now()        
        user.save()
        
        puppet.at_post_login(self)
        
    def msg(self, message):
        """
        Sends a message to the session.
        """
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        self.sendLine("%s" % (message,))
        
    def add_default_channels(self):
        """
        Adds the player to the default channels.
        """        
        # Add the default channels.
        for chan in CommChannel.objects.filter(is_joined_by_default=True):            
            chan_alias = chan.get_default_chan_alias()
            comsys.plr_add_channel(self.puppet, chan_alias, chan)            
            comsys.plr_set_channel_listening(self, chan_alias, True)

    def add_default_group(self):        
        default_group = settings.PERM_DEFAULT_PLAYER_GROUP.strip()
        if not default_group:
            logger.log_infomsg("settings.DEFAULT_PLAYER_GROUP is not set. Using no group.")
            return 
        try:
            group = Group.objects.get(name=default_group)            
        except Group.DoesNotExist:
            logger.log_errmsg("settings.DEFAULT_PLAYER_GROUP = %s is not a valid group. Using no group." % default_group)
            return
        self.user.groups.add(group)
        logger.log_infomsg("Added new player to default permission group '%s'." % default_group)
        user.save();

    def __str__(self):
        """
        String representation of the user session class. We use
        this a lot in the server logs and stuff.
        """
        if self.is_loggedin():
            symbol = '#'
        else:
            symbol = '?'
        return "<%s> %s@%s" % (symbol, self.user, self.address,)
    
    def cemit_info(self, message):
        """
        Channel emits info to the appropriate info channel. By default, this
        is MUDConnections.
        """
        comsys.send_cmessage(settings.COMMCHAN_MUD_CONNECTIONS, 
                             'Session: %s' % message)
