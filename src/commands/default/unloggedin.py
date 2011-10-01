"""
Commands that are available from the connect screen.
"""
import traceback
from django.conf import settings 
from django.contrib.auth.models import User
from src.server import sessionhandler
from src.players.models import PlayerDB
from src.objects.models import ObjectDB
from src.server.models import ServerConfig
from src.comms.models import Channel

from src.utils import create, logger, utils, ansi
from src.commands.default.muxcommand import MuxCommand

CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE

class CmdConnect(MuxCommand):
    """
    Connect to the game.

    Usage (at login screen): 
      connect <email> <password>
      
    Use the create command to first create an account before logging in.
    """  
    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()" # not really needed

    def func(self):
        """
        Uses the Django admin api. Note that unlogged-in commands
        have a unique position in that their func() receives
        a session object instead of a source_object like all
        other types of logged-in commands (this is because
        there is no object yet before the player has logged in)
        """

        session = self.caller        
        arglist = self.arglist

        if not arglist or len(arglist) < 2:
            session.msg("\n\r Usage (without <>): connect <email> <password>")
            return
        email = arglist[0]
        password = arglist[1]
        
        # Match an email address to an account.
        player = PlayerDB.objects.get_player_from_email(email)
        # No playername match
        if not player:
            string = "The email '%s' does not match any accounts." % email
            string += "\n\r\n\rIf you are new you should first create a new account "
            string += "using the 'create' command."
            session.msg(string)
            return
        # We have at least one result, so we can check the password.
        if not player.user.check_password(password):
            session.msg("Incorrect password.")
            return 

        # actually do the login. This will call all hooks. 
        session.session_login(player)

        # we are logged in. Look around.
        character = player.character
        if character:
            character.execute_cmd("look")
        else:
            # we have no character yet; use player's look, if it exists
            player.execute_cmd("look")


class CmdCreate(MuxCommand):
    """
    Create a new account.

    Usage (at login screen):
      create \"playername\" <email> <password>

    This creates a new player account.

    """
    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
                   
    def parse(self):
        """
        The parser must handle the multiple-word player
        name enclosed in quotes:
        connect "Long name with many words" my@myserv.com mypassw
        """
        super(CmdCreate, self).parse()

        self.playerinfo = []
        if len(self.arglist) < 3:
            return 
        if len(self.arglist) > 3:
            # this means we have a multi_word playername. pop from the back.
            password = self.arglist.pop()
            email = self.arglist.pop()
            # what remains is the playername.
            playername = " ".join(self.arglist) 
        else:
            playername, email, password = self.arglist
        
        playername = playername.replace('"', '') # remove "
        playername = playername.replace("'", "")
        self.playerinfo = (playername, email, password)

    def func(self):
        "Do checks and create account"

        session = self.caller

        try: 
            playername, email, password = self.playerinfo
        except ValueError:            
            string = "\n\r Usage (without <>): create \"<playername>\" <email> <password>"
            session.msg(string)
            return
        if not playername: 
            # entered an empty string
            session.msg("\n\r You have to supply a longer playername, surrounded by quotes.")
            return
        if not email or not password:
            session.msg("\n\r You have to supply an e-mail address followed by a password." ) 
            return 

        if not utils.validate_email_address(email):
            # check so the email at least looks ok.
            session.msg("'%s' is not a valid e-mail address." % email)
            return             

        # Run sanity and security checks 
        
        if PlayerDB.objects.get_player_from_name(playername) or User.objects.filter(username=playername):
            # player already exists
            session.msg("Sorry, there is already a player with the name '%s'." % playername)
            return         
        if PlayerDB.objects.get_player_from_email(email):
            # email already set on a player
            session.msg("Sorry, there is already a player with that email address.")
            return 
        if len(password) < 3:
            # too short password
            string = "Your password must be at least 3 characters or longer."
            string += "\n\rFor best security, make it at least 8 characters long, "
            string += "avoid making it a real word and mix numbers into it."
            session.msg(string)
            return         

        # everything's ok. Create the new player account.
        try:
            default_home = ObjectDB.objects.get_id(settings.CHARACTER_DEFAULT_HOME)                

            typeclass = settings.BASE_CHARACTER_TYPECLASS
            permissions = settings.PERMISSION_PLAYER_DEFAULT

            new_character = create.create_player(playername, email, password,
                                                 permissions=permissions,
                                                 character_typeclass=typeclass,
                                                 character_location=default_home,
                                                 character_home=default_home)                            
            new_player = new_character.player
            
            # character safety features
            new_character.locks.delete("get")
            new_character.locks.add("get:perm(Wizards)")
            # allow the character itself and the player to puppet this character.
            new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" % 
                                    (new_character.id, new_player.id))

            # set a default description
            new_character.db.desc = "This is a Player."

            new_character.db.FIRST_LOGIN = True                
            new_player = new_character.player
            new_player.db.FIRST_LOGIN = True 

            # join the new player to the public channel                
            pchanneldef = settings.CHANNEL_PUBLIC
            if pchanneldef:
                pchannel = Channel.objects.get_channel(pchanneldef[0])
                if not pchannel.connect_to(new_player):
                    string = "New player '%s' could not connect to public channel!" % new_player.key
                    logger.log_errmsg(string)

            string = "A new account '%s' was created with the email address %s. Welcome!"
            string += "\n\nYou can now log with the command 'connect %s <your password>'."                
            session.msg(string % (playername, email, email))
        except Exception:
            # We are in the middle between logged in and -not, so we have to handle tracebacks 
            # ourselves at this point. If we don't, we won't see any errors at all.
            string = "%s\nThis is a bug. Please e-mail an admin if the problem persists."
            session.msg(string % (traceback.format_exc()))
            logger.log_errmsg(traceback.format_exc())            

class CmdQuit(MuxCommand):
    """
    We maintain a different version of the quit command
    here for unconnected players for the sake of simplicity. The logged in
    version is a bit more complicated.
    """
    key = "quit"
    aliases = ["q", "qu"]
    locks = "cmd:all()"

    def func(self):
        "Simply close the connection."
        session = self.caller
        session.msg("Good bye! Disconnecting ...")
        session.session_disconnect()

class CmdUnconnectedLook(MuxCommand):
    """
    This is an unconnected version of the look command for simplicity. 
    All it does is re-show the connect screen. 
    """
    key = "look"
    aliases = "l"
    locks = "cmd:all()"
    
    def func(self):
        "Show the connect screen."
        try:
            screen = utils.string_from_module(CONNECTION_SCREEN_MODULE)
            string = ansi.parse_ansi(screen)
            self.caller.msg(string)
        except Exception, e:
            self.caller.msg(e)
            self.caller.msg("Connect screen not found. Enter 'help' for aid.")

class CmdUnconnectedHelp(MuxCommand):
    """
    This is an unconnected version of the help command,
    for simplicity. It shows a pane or info. 
    """
    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def func(self):
        "Shows help"
        
        string = \
            """
You are not yet logged into the game. Commands available at this point:
  {wcreate, connect, look, help, quit{n

To login to the system, you need to do one of the following:

{w1){n If you have no previous account, you need to use the 'create'
   command like this:

     {wcreate "Anna the Barbarian" anna@myemail.com c67jHL8p{n

   It's always a good idea (not only here, but everywhere on the net)
   to not use a regular word for your password. Make it longer than 
   3 characters (ideally 6 or more) and mix numbers and capitalization 
   into it. 

{w2){n If you have an account already, either because you just created 
   one in {w1){n above or you are returning, use the 'connect' command: 

     {wconnect anna@myemail.com c67jHL8p{n

   This should log you in. Run {whelp{n again once you're logged in 
   to get more aid. Hope you enjoy your stay! 

You can use the {wlook{n command if you want to see the connect screen again. 
"""
        self.caller.msg(string)
