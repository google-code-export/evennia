"""
This module contains classes related to Sessions. sessionhandler has the things
needed to manage them.
"""
import time
from datetime import datetime
from twisted.conch.telnet import StatefulTelnetProtocol
from django.conf import settings
from src.server import sessionhandler
from src.objects.models import ObjectDB 
from src.comms.models import Channel
from src.config.models import ConnectScreen
from src.commands import cmdhandler
from src.utils import ansi
from src.utils import reloads 
from src.utils import logger
from src.utils import utils

from src.teltola.tokens import HTML_TOKEN, JAVASCRIPT_TOKEN, UNENCODED_TOKEN, NO_AUTOCHUNK_TOKEN, AUTOCHUNK_TOKEN, TELNET_ONLY_TOKEN, ENCODING_TOKENS
from src.teltola.formatting import strip_for_teltola_client as strip_for_client, manual

from django.template.loader import get_template
from django.template import Context

from cgi import escape
from nevow.livepage import js, eol

class AnsiState:
    def __init__(self):
        self.buffer = ""
        self.open_span = False
        self.reset()
    def reset(self):
        self.background = None
        self.foreground = None
        self.bold = False
        self.italic = False
        self.underline = False
        self.inverse = False
        self.strikethrough = False
    def process_buffer(self):
        retval = ""
        if self.buffer == "[0":
            self.reset()
        elif self.buffer == "[1":
            self.bold = True
        elif self.buffer == "[3":
            self.italic = True
        elif self.buffer == "[4":
            self.underline = True
        elif self.buffer == "[7":
            self.inverse = True
        elif self.buffer == "[9":
            self.strikethrough = True
        elif self.buffer == "[22":
            self.bold = False
        elif self.buffer == "[23":
            self.italic = False
        elif self.buffer == "[24":
            self.underilne = False
        elif self.buffer == "[27":
            self.inverse = False
        elif self.buffer == "[29":
            self.strikethrough = False
        elif self.buffer == "[30":
            self.foreground = "black"
        elif self.buffer == "[31":
            self.foreground = "red"
        elif self.buffer == "[32":
            self.foreground = "green"
        elif self.buffer == "[33":
            self.foreground = "yellow"
        elif self.buffer == "[34":
            self.foreground = "blue"
        elif self.buffer == "[35":
            self.foreground = "magenta"
        elif self.buffer == "[36":
            self.foreground = "cyan"
        elif self.buffer == "[37":
            self.foreground = "white"
        # 38
        elif self.buffer == "[39":
            self.foreground = False 
        elif self.buffer == "[40":
            self.background = "black"
        elif self.buffer == "[41":
            self.background = "red"
        elif self.buffer == "[42":
            self.background = "green"
        elif self.buffer == "[43":
            self.background = "yellow"
        elif self.buffer == "[44":
            self.background = "blue"
        elif self.buffer == "[45":
            self.background = "magenta"
        elif self.buffer == "[46":
            self.background = "cyan"
        elif self.buffer == "[47":
            self.background = "white"
        # 48
        elif self.buffer == "[49":
            self.background = False 
        else:
            retval += "<h1>%s</h1>" % self.buffer
        self.buffer = ""
        if self.open_span:
            retval += "</span>"
        self.open_span = False
        attrs = []
        if self.bold:
           attrs.append('font-weight:bold')
        if self.background:
           attrs.append('background-color:%s' % self.background)
        if self.foreground:
           attrs.append('color:%s' % self.foreground)
        if len(attrs):
            retval += "<span style='%s'>" % (u";".join(attrs))
            self.open_span = True
        return retval
        
       

class RTFakeSessionProtocol:
    def __init__(self, client, host):
        self.client = client
        self.host = host
        self.ansi_state = AnsiState()
    def write(self, txt):
        self.client.send(txt)
    mode = 'WaitForUser'
    def dataReceived(self, chunk):
        if not hasattr(self, "currentEncoding"):
            self.currentEncoding = UNENCODED_TOKEN
            self.autochunk = True
            self.htmlBuffer = u""
            self.javascriptBuffer = u""
            self.trappingANSI = False
        while chunk != "":
            c = chunk[0]
            chunk = chunk[1:]
            if c in ENCODING_TOKENS:
                if c == AUTOCHUNK_TOKEN:
                    self.autochunk = True
                elif c == NO_AUTOCHUNK_TOKEN:
                    self.autochunk = False
                elif c != self.currentEncoding:
                    self.currentEncoding = c
            else:
                if self.currentEncoding == UNENCODED_TOKEN:
                    if c == chr(27):
                        self.trappingANSI = True
                    elif self.trappingANSI == True:
                        if c == "m":
                            self.trappingANSI = False
                            self.htmlBuffer += self.ansi_state.process_buffer()
                        else:
                            self.ansi_state.buffer += c
                    elif self.trappingANSI == False:
                        if c in [chr(10), chr(13), chr(255)]  and self.autochunk:
                            self.doSend()
                        self.htmlBuffer += escape(c, quote=True)
                elif self.currentEncoding == HTML_TOKEN:
                    self.htmlBuffer += c 
                elif self.currentEncoding == JAVASCRIPT_TOKEN:
                        self.javascriptBuffer += c
    def doSend(self):
        if self.ansi_state.open_span:
            self.ansi_state.reset()
            self.open_span = False
            self.htmlBuffer += "</span>"
        if self.htmlBuffer != "":
            self.client.send([js.addText(self.htmlBuffer), eol, js.scrollDown()])
            self.htmlBuffer = ""
        if self.javascriptBuffer != "":
            self.client.send([js.remoteEval(self.javascriptBuffer), eol, js.scrollDown()])
    def sendLine(self, txt):
        self.dataReceived(txt + u"\n")
    """
    This class represents a player's session. Each player
    gets a session assigned to them whenever
    they connect to the game server. All communication
    between game and player goes through here. 
    """
    
    def __str__(self):
        """
        String representation of the user session class. We use
        this a lot in the server logs and stuff.
        """
        if self.logged_in:
            symbol = '#'
        else:
            symbol = '?'
        return "<%s> %s@%s" % (symbol, self.name, self.address,)

    def connectionMade(self):
        """
        What to do when we get a connection.
        """
        # setup the parameters
        self.prep_session()
        # send info
        logger.log_infomsg('New connection: %s' % self)        
        # add this new session to handler
        sessionhandler.add_session(self)
        # show a connect screen 
        self.game_connect_screen()
        welcome_html = get_template('login.snip').render(Context())
        clear_screen_js = u""
        self.msg(HTML_TOKEN + welcome_html + UNENCODED_TOKEN)

    def getClientAddress(self):
        """
        Returns the client's address and port in a tuple. For example
        ('127.0.0.1', 41917)
        """
        return self.host

    def prep_session(self):
        """
        This sets up the main parameters of
        the session. The game will poll these
        properties to check the status of the
        connection and to be able to contact
        the connected player. 
        """
        # main server properties 
        # do we need this self.server?
        #self.server = self.factory.server
        self.address = self.getClientAddress()

        # player setup 
        self.name = None
        self.uid = None
        self.logged_in = False

        # The time the user last issued a command.
        self.cmd_last = time.time()
        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = time.time()
        # Total number of commands issued.
        self.cmd_total = 0
        # The time when the user connected.
        self.conn_time = time.time()
        #self.channels_subscribed = {}

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
        
    def lineReceived(self, raw_string):
        """
        Communication Player -> Evennia
        Any line return indicates a command for the purpose of the MUD.
        So we take the user input and pass it to the Player and their currently
        connected character.
        """
        try:
            raw_string = utils.to_unicode(raw_string)
        except Exception, e:
            self.sendLine(str(e))
            return 
        self.execute_cmd(raw_string)        

    def msg(self, message, markup=True):
        """
        Communication Evennia -> Player
        Sends a message to the session.

        markup - determines if formatting markup should be 
                 parsed or not. Currently this means ANSI
                 colors, but could also be html tags for 
                 web connections etc.        
        """
        try:
            message = utils.to_str(message)
        except Exception, e:
            self.sendLine(str(e))
            return 
        self.sendLine(strip_for_client(ansi.parse_ansi(message, strip_ansi=not markup)))

    def get_character(self):
        """
        Returns the in-game character associated with a session.
        This returns the typeclass of the object.
        """
        if self.logged_in: 
            character = ObjectDB.objects.get_object_with_user(self.uid)
            if not character:
                string  = "No character match for session uid: %s" % self.uid
                logger.log_errmsg(string)                
            else:
                return character
        return None 

    def execute_cmd(self, raw_string):
        """
        Sends a command to this session's
        character for processing.

        'idle' is a special command that is
        interrupted already here. It doesn't do
        anything except silently updates the
        last-active timer to avoid getting kicked
        off for idleness.
        """
        # handle the 'idle' command 
        if str(raw_string).strip() == 'idle':
            self.update_counters(idle=True)            
            return 

        # all other inputs, including empty inputs
        character = self.get_character()
        if character:
            # normal operation.            
            character.execute_cmd(raw_string)
        else:
            # we are not logged in yet
            cmdhandler.cmdhandler(self, raw_string, unloggedin=True)
        # update our command counters and idle times. 
        self.update_counters()
      
    def update_counters(self, idle=False):
        """
        Hit this when the user enters a command in order to update idle timers
        and command counters. If silently is True, the public-facing idle time
        is not updated.
        """
        # Store the timestamp of the user's last command.
        self.cmd_last = time.time()
        if not idle:
            # Increment the user's command counter.
            self.cmd_total += 1
            # Player-visible idle time, not used in idle timeout calcs.
            self.cmd_last_visible = time.time()
            
    def handle_close(self):
        """
        Break the connection and do some accounting.
        """
        character = self.get_character()
        if character:
            #call hook functions 
            character.at_disconnect()            
            character.player.at_disconnect()
            uaccount = character.player.user
            uaccount.last_login = datetime.now()
            uaccount.save()            
        self.disconnectClient()
        self.logged_in = False
        sessionhandler.remove_session(self)        
        
    def game_connect_screen(self):
        """
        Show the banner screen. Grab from the 'connect_screen'
        config directive. If more than one connect screen is
        defined in the ConnectScreen attribute, it will be
        random which screen is used. 
        """
        screen = ConnectScreen.objects.get_random_connect_screen()
        string = strip_for_client(ansi.parse_ansi(screen.text))
        self.msg(string)
    
    def login(self, player):
        """
        After the user has authenticated, this actually
        logs them in. At this point the session has
        a User account tied to it. User is an django
        object that handles stuff like permissions and
        access, it has no visible precense in the game.
        This User object is in turn tied to a game
        Object, which represents whatever existence
        the player has in the game world. This is the
        'character' referred to in this module. 
        """
        # set the session properties 

        user = player.user
        self.uid = user.id
        self.name = user.username
        self.logged_in = True
        self.conn_time = time.time()
        
        if not settings.ALLOW_MULTISESSION:
            # disconnect previous sessions.
            sessionhandler.disconnect_duplicate_session(self)

        # start (persistent) scripts on this object
        reloads.reload_scripts(obj=self.get_character(), init_mode=True)

        logger.log_infomsg("Logged in: %s" % self)
        self.cemit_info('Logged in: %s' % self)
        
        # Update their account's last login time.
        user.last_login = datetime.now()        
        user.save()
            
    def cemit_info(self, message):
        """
        Channel emits info to the appropriate info channel. By default, this
        is MUDConnections.
        """
        try:
            cchan = settings.CHANNEL_CONNECTINFO
            cchan = Channel.objects.get_channel(cchan[0])
            cchan.msg("[%s]: %s" % (cchan.key, message))
        except Exception:
            logger.log_infomsg(message)

            
