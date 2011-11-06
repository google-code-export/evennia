"""
This module defines handlers for storing sessions when handles 
sessions of users connecting to the server. 

There are two similar but separate stores of sessions:
  ServerSessionHandler - this stores generic game sessions 
         for the game. These sessions has no knowledge about
         how they are connected to the world. 
  PortalSessionHandler - this stores sessions created by
         twisted protocols. These are dumb connectors that
         handle network communication but holds no game info.
      

"""

import time
from django.conf import settings
from django.contrib.auth.models import User
from src.server.models import ServerConfig
from src.utils import utils 

from src.commands.cmdhandler import CMD_LOGINSTART

# i18n
from django.utils.translation import ugettext as _

ALLOW_MULTISESSION = settings.ALLOW_MULTISESSION
IDLE_TIMEOUT = settings.IDLE_TIMEOUT


class SessionHandler(object):
    """
    This handler holds a stack of sessions.
    """
    def __init__(self):
        """
        Init the handler.        
        """
        self.sessions = {}

    def get_sessions(self, include_unloggedin=False):
        """
        Returns the connected session objects.
        """
        if include_unloggedin:
            return self.sessions.values()
        else:
            return [session for session in self.sessions.values() if session.logged_in]

    def get_session(self, sessid):
        """
        Get session by sessid
        """
        return self.sessions.get(sessid, None)

    def get_all_sync_data(self):
        """
        Create a dictionary of sessdata dicts representing all 
        sessions in store. 
        """
        sessdict = {}
        for sess in self.sessions.values():
            # copy all relevant data from all sessions
            sessdict[sess.sessid] = sess.get_sync_data()            
        return sessdict

#------------------------------------------------------------
# Server-SessionHandler class
#------------------------------------------------------------

class ServerSessionHandler(SessionHandler):
    """
    This object holds the stack of sessions active in the game at
    any time. 

    A session register with the handler in two steps, first by
    registering itself with the connect() method. This indicates an
    non-authenticated session. Whenever the session is authenticated
    the session together with the related player is sent to the login()
    method. 

    """

    # AMP communication methods

    def __init__(self):
        """
        Init the handler.        
        """
        self.sessions = {}
        self.server = None 

    def portal_connect(self, sessid, session):
        """
        Called by Portal when a new session has connected. 
        Creates a new, unlogged-in game session.
        """
        self.sessions[sessid] = session
        session.execute_cmd(CMD_LOGINSTART)

    def portal_disconnect(self, sessid):
        """
        Called by Portal when portal reports a closing of a session
        from the portal side.
        """
        session = self.sessions.get(sessid, None)
        if session:
            del self.sessions[session.sessid]
            self.session_count(-1)

    def portal_session_sync(self, sesslist):
        """
        Syncing all session ids of the portal with the ones of the server. This is instantiated
        by the portal when reconnecting.
        
        sesslist is a complete list of (sessid, session) pairs, matching the list on the portal.
                 if session was logged in, the amp handler will have logged them in before this point.
        """        
        for sess in self.sessions.values():
            # we delete the old session to make sure to catch eventual lingering references.
            del sess
        for sess in sesslist:
            self.sessions[sess.sessid] = sess
            sess.at_sync()

    def portal_shutdown(self):
        """
        Called by server when shutting down the portal.
        """        
        self.server.amp_protocol.call_remote_PortalAdmin(0,
                                                         operation='SSHUTD',
                                                         data="")        
    # server-side access methods 

    def disconnect(self, session, reason=""):
        """
        Called from server side to remove session and inform portal 
        of this fact.
        """
        session = self.sessions.get(session.sessid, None)
        if session:
            sessid = session.sessid
            del self.sessions[sessid]
            # inform portal that session should be closed.
            self.server.amp_protocol.call_remote_PortalAdmin(sessid,
                                                             operation='SDISCONN',
                                                             data=reason)
        self.session_count(-1)

        
    def login(self, session):
        """
        Log in the previously unloggedin session and the player we by
        now should know is connected to it. After this point we
        assume the session to be logged in one way or another.
        """
        # prep the session with player/user info
        
        if not ALLOW_MULTISESSION:
            # disconnect previous sessions.
            self.disconnect_duplicate_sessions(session)
        session.logged_in = True 
        self.session_count(1)
        # sync the portal to this session
        sessdata = session.get_sync_data()
        self.server.amp_protocol.call_remote_PortalAdmin(session.sessid,
                                                         operation='SLOGIN',
                                                         data=sessdata)
    
    def session_sync(self):
        """
        This is called by the server when it reboots. It syncs all session data
        to the portal. 
        """
        sessdata = self.get_all_sync_data()
        self.server.amp_protocol.call_remote_PortalAdmin(0,
                                                         'SSYNC',
                                                         data=sessdata)


    def disconnect_all_sessions(self, reason="You have been disconnected."):
        """
        Cleanly disconnect all of the connected sessions.
        """
        
        for session in self.sessions:
            del session
        self.session_count(0)
        # tell portal to disconnect all sessions
        self.server.amp_protocol.call_remote_PortalAdmin(0,
                                                         operation='SDISCONNALL',
                                                         data=reason)

    def disconnect_duplicate_sessions(self, curr_session):
        """
        Disconnects any existing sessions with the same game object. 
        """
        curr_char = curr_session.get_character()
        doublet_sessions = [sess for sess in self.sessions
                            if sess.logged_in 
                            and sess.get_character() == curr_char
                            and sess != curr_session]
        reason = _("Logged in from elsewhere. Disconnecting.") 
        for sessid in doublet_sessions:
            self.disconnect(session, reason)            
            self.session_count(-1)


    def validate_sessions(self):
        """
        Check all currently connected sessions (logged in and not) 
        and see if any are dead.
        """
        tcurr = time.time()
        invalid_sessions = [session for session in self.sessions.values() 
                            if session.logged_in and IDLE_TIMEOUT > 0 
                            and (tcurr - session.cmd_last) > IDLE_TIMEOUT]            
        for session in invalid_sessions:
            self.disconnect(session, reason=_("Idle timeout exceeded, disconnecting."))
            self.session_count(-1)
                
    def session_count(self, num=None):
        """
        Count up/down the number of connected, authenticated users. 
        If num is None, the current number of sessions is returned.

        num can be a positive or negative value to be added to the current count. 
        If 0, the counter will be reset to 0. 
        """
        if num == None:
            # show the current value. This also syncs it.                         
            return int(ServerConfig.objects.conf('nr_sessions', default=0))            
        elif num == 0:
            # reset value to 0
            ServerConfig.objects.conf('nr_sessions', 0)
        else:
            # add/remove session count from value
            add = int(ServerConfig.objects.conf('nr_sessions', default=0))
            num = max(0, num + add)
            ServerConfig.objects.conf('nr_sessions', str(num))

    def player_count(self):
        """
        Get the number of connected players (not sessions since a player
        may have more than one session connected if ALLOW_MULTISESSION is True)
        Only logged-in players are counted here.
        """
        return len(set(session.uid for session in self.sessions.values() if session.logged_in))
        
    def sessions_from_player(self, player):
        """
        Given a player, return any matching sessions.
        """
        username = player.user.username
        try:
            uobj = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        uid = uobj.id
        return [session for session in self.sessions.values() if session.logged_in and session.uid == uid]

    def sessions_from_character(self, character):
        """
        Given a game character, return any matching sessions.
        """
        player = character.player
        if player:
            return self.sessions_from_player(player)
        return None 


    def announce_all(self, message):
        """
        Send message to all connected sessions
        """
        for sess in self.sessions.values():
            self.data_out(sess, message)

    def data_out(self, session, string="", data=""):
        """
        Sending data Server -> Portal
        """
        self.server.amp_protocol.call_remote_MsgServer2Portal(sessid=session.sessid,
                                                              msg=string,
                                                              data=data)
    def data_in(self, sessid, string="", data=""):
        """
        Data Portal -> Server
        """        
        session = self.sessions.get(sessid, None)                
        if session:            
            session.execute_cmd(string)

        # ignore 'data' argument for now; this is otherwise the place
        # to put custom effects on the server due to data input, e.g.
        # from a custom client. 
    

#------------------------------------------------------------
# Portal-SessionHandler class
#------------------------------------------------------------

class PortalSessionHandler(SessionHandler):
    """
    This object holds the sessions connected to the portal at any time.
    It is synced with the server's equivalent SessionHandler over the AMP
    connection. 

    Sessions register with the handler using the connect() method. This 
    will assign a new unique sessionid to the session and send that sessid
    to the server using the AMP connection. 

    """

    def __init__(self):
        """
        Init the handler
        """
        self.portal = None 
        self.sessions = {}
        self.latest_sessid = 0

    def connect(self, session):
        """
        Called by protocol at first connect. This adds a not-yet authenticated session
        using an ever-increasing counter for sessid. 
        """        
        self.latest_sessid += 1
        sessid = self.latest_sessid
        session.sessid = sessid
        sessdata = session.get_sync_data()
        self.sessions[sessid] = session
        # sync with server-side 
        self.portal.amp_protocol.call_remote_ServerAdmin(sessid,
                                                         operation="PCONN",
                                                         data=sessdata)
    def disconnect(self, session):
        """
        Called from portal side when the connection is closed from the portal side.
        """
        sessid = session.sessid
        self.portal.amp_protocol.call_remote_ServerAdmin(sessid,
                                                         operation="PDISCONN")
        
    def server_disconnect(self, sessid, reason=""):
        """
        Called by server to force a disconnect by sessid
        """
        session = self.sessions.get(sessid, None)
        if session:
            session.disconnect(reason)        
            del session 

    def server_disconnect_all(self, reason=""):
        """
        Called by server when forcing a clean disconnect for everyone.
        """
        for session in self.sessions.values():            
            session.disconnect(reason)
            del session        

    def session_from_suid(self, suid):
        """
        Given a session id, retrieve the session (this is primarily
        intended to be called by web clients)
        """
        return [sess for sess in self.get_sessions(include_unloggedin=True) 
                if hasattr(sess, 'suid') and sess.suid == suid]

    def data_in(self, session, string="", data=""):
        """
        Called by portal sessions for relaying data coming 
        in from the protocol to the server. data is 
        serialized before passed on. 
        """    
        self.portal.amp_protocol.call_remote_MsgPortal2Server(session.sessid,
                                                              msg=string,
                                                              data=data)
    def announce_all(self, message):
        """
        Send message to all connection sessions
        """
        for session in self.sessions.values():
            session.data_out(message)

    def data_out(self, sessid, string="", data=""):
        """
        Called by server for having the portal relay messages and data 
        to the correct session protocol. 
        """
        session = self.sessions.get(sessid, None)
        if session:
            session.data_out(string, data=data)                                        

SESSIONS = ServerSessionHandler()
PORTAL_SESSIONS = PortalSessionHandler()
