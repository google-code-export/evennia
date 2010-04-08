"""
Session manager, handles connected players.
"""
import time
from django.contrib.auth.models import User
from src.config.models import ConfigValue
from src import logger

# Our list of connected sessions.
session_list = []

def find_sessions_from_username(username):
    """
    Given a username, return any matching sessions.
    """
    try:
        uobj = User.objects.get(username=username)
        uid = uobj.id
        return [session for session in session_list if session.uid == uid]
    except User.DoesNotExist:
        return None

def add_session(session):
    """
    Adds a session to the session list.
    """
    session_list.insert(0, session)
    logger.log_infomsg('Sessions active: %d' % (len(get_session_list(return_unlogged=True),)))
    
def get_session_list(return_unlogged=False):
    """
    Lists the connected session objects.
    """
    if return_unlogged:
        return session_list
    else:
        return [sess for sess in session_list if sess.is_loggedin()]
    
def get_session_id_list(return_unlogged=False):
    """
    Lists the connected session object ids.
    """
    if return_unlogged:
        return session_list
    else:
        return [sess.uid for sess in session_list if sess.is_loggedin()]

def disconnect_all_sessions():
    """
    Cleanly disconnect all of the connected sessions.
    """
    for sess in get_session_list():
        sess.handle_close()

def disconnect_duplicate_session(session):
    """
    Disconnects any existing session under the same object. This is used in
    connection recovery to help with record-keeping.
    """
    session_list = get_session_list()
    for other_session in session_list:
        if session.puppet == other_session.puppet and other_session != session:
            other_session.msg("Your account has been logged in from elsewhere, disconnecting.")
            other_session.disconnectClient()
            return True
    return False

def check_all_sessions():
    """
    Check all currently connected sessions and see if any are dead.
    """
    idle_timeout = int(ConfigValue.objects.get_configvalue('idle_timeout'))

    if len(session_list) <= 0:
        return

    if idle_timeout <= 0:
        return
    
    for sess in get_session_list(return_unlogged=True):
        if (time.time() - sess.cmd_last) > idle_timeout:
            sess.msg("Idle timeout exceeded, disconnecting.")
            sess.handle_close()

def remove_session(session):
    """
    Removes a session from the session list.
    """
    try:
        session_list.remove(session)
        logger.log_infomsg('Sessions active: %d' % (len(get_session_list()),))
    except ValueError:
        #logger.log_errmsg("Unable to remove session: %s" % (session,))
        pass
        
    
def sessions_from_object(targ_object):
    """
    Returns a list of matching session objects, or None if there are no matches.
    
    targobject: (Object) The object to match.
    """
    return [prospect for prospect in session_list if prospect.puppet == targ_object]
        
def announce_all(message, with_ann_prefix=True):
    """
    Announces something to all connected players.
    """
    if with_ann_prefix:
        prefix = 'Announcement:'
    else:
        prefix = ''

    for session in get_session_list():
        session.msg('%s %s' % (prefix, message))
