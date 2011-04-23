"""

Admin commands

"""

from django.conf import settings
from django.contrib.auth.models import User
from src.players.models import PlayerDB
from src.server.sessionhandler import SESSIONS
from src.utils import utils
from src.commands.default.muxcommand import MuxCommand

PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]

class CmdBoot(MuxCommand):
    """
    @boot 

    Usage
      @boot[/switches] <player obj> [: reason]

    Switches:
      quiet - Silently boot without informing player
      port - boot by port number instead of name or dbref
      
    Boot a player object from the server. If a reason is
    supplied it will be echoed to the user unless /quiet is set. 
    """
    
    key = "@boot"
    locks = "cmd:perm(boot) or perm(Wizards)"
    help_category = "Admin"

    def func(self):
        "Implementing the function"
        caller = self.caller
        args = self.args
        
        if not args:
            caller.msg("Usage: @boot[/switches] <player> [:reason]")
            return

        if ':' in args:
            args, reason = [a.strip() for a in args.split(':', 1)]
        else:
            args, reason = args, ""

        boot_list = []

        if 'port' in self.switches:
            # Boot a particular port.
            sessions = SESSIONS.get_session_list(True)
            for sess in sessions:
                # Find the session with the matching port number.
                if sess.getClientAddress()[1] == int(args):
                    boot_list.append(sess)
                    break
        else:
            # Boot by player object
            pobj = caller.search("*%s" % args, global_search=True, player=True)
            if not pobj:
                return            
            if pobj.character.has_player:
                if not pobj.access(caller, 'boot'):
                    string = "You don't have the permission to boot %s."
                    pobj.msg(string)
                    return 
                # we have a bootable object with a connected user
                matches = SESSIONS.sessions_from_player(pobj)
                for match in matches:
                    boot_list.append(match)
            else:
                caller.msg("That object has no connected player.")
                return

        if not boot_list:
            caller.msg("No matches found.")
            return

        # Carry out the booting of the sessions in the boot list.

        feedback = None 
        if not 'quiet' in self.switches:
            feedback = "You have been disconnected by %s.\n" % caller.name
            if reason:
                feedback += "\nReason given: %s" % reason

        for session in boot_list:
            name = session.name
            session.msg(feedback)
            session.disconnect()
            caller.msg("You booted %s." % name)


class CmdDelPlayer(MuxCommand):
    """
    delplayer - delete player from server

    Usage:
      @delplayer[/switch] <name> [: reason]
      
    Switch:
      delobj - also delete the player's currently
                assigned in-game object.   

    Completely deletes a user from the server database,
    making their nick and e-mail again available.    
    """

    key = "@delplayer"
    locks = "cmd:perm(delplayer) or perm(Immortals)"
    help_category = "Admin"

    def func(self):
        "Implements the command."

        caller = self.caller
        args = self.args 

        if hasattr(caller, 'player'):
            caller = caller.player 

        if not args:
            caller.msg("Usage: @delplayer[/delobj] <player/user name or #id> [: reason]")
            return

        reason = ""
        if ':' in args:
            args, reason = [arg.strip() for arg in args.split(':', 1)]

        # We use player_search since we want to be sure to find also players
        # that lack characters.
        players = caller.search("*%s" % args, player=True)
        if not players:
            try:
                players = PlayerDB.objects.filter(id=args)
            except ValueError:
                pass

        if not players:            
            # try to find a user instead of a Player
            try:
                user = User.objects.get(id=args)
            except Exception:            
                try:
                    user = User.objects.get(username__iexact=args)                        
                except Exception:
                    string = "No Player nor User found matching '%s'." % args
                    caller.msg(string)
                    return                     
            try:
                player = user.get_profile()
            except Exception:
                player = None 
                                
            if player and not player.access(caller, 'delete'):
                string = "You don't have the permissions to delete this player."
                caller.msg(string)
                return 

            string = ""
            name = user.username
            user.delete()
            if player:
                name = player.name
                player.delete()
                string = "Player %s was deleted." % name
            else:
                string += "The User %s was deleted. It had no Player associated with it." % name
            caller.msg(string)
            return 
    
        elif utils.is_iter(players):
            string = "There were multiple matches:"
            for player in players:
                string += "\n %s %s" % (player.id, player.key) 
            return 
        else:
            # one single match

            player = players
            user = player.user
            character = player.character

            if not player.access(caller, 'delete'):
                string = "You don't have the permissions to delete that player."
                caller.msg(string)
                return 

            uname = user.username
            # boot the player then delete 
            if character and character.has_player:
                caller.msg("Booting and informing player ...")
                string = "\nYour account '%s' is being *permanently* deleted.\n" %  uname
                if reason:
                    string += " Reason given:\n  '%s'" % reason
                character.msg(string)
                caller.execute_cmd("@boot %s" % uname)
                
            player.delete()
            user.delete()    
            caller.msg("Player %s was successfully deleted." % uname)


class CmdEmit(MuxCommand):                    
    """
    @emit

    Usage:
      @emit[/switches] [<obj>, <obj>, ... =] <message>
      @remit           [<obj>, <obj>, ... =] <message> 
      @pemit           [<obj>, <obj>, ... =] <message> 

    Switches:
      room : limit emits to rooms only (default)
      players : limit emits to players only 
      contents : send to the contents of matched objects too
      
    Emits a message to the selected objects or to
    your immediate surroundings. If the object is a room,
    send to its contents. @remit and @pemit are just 
    limited forms of @emit, for sending to rooms and 
    to players respectively.
    """
    key = "@emit"
    aliases = ["@pemit", "@remit"]
    locks = "cmd:perm(emit) or perm(Builders)"
    help_category = "Admin"

    def func(self):
        "Implement the command"
        
        caller = self.caller
        args = self.args

        if not args:
            string = "Usage: "
            string += "\n@emit[/switches] [<obj>, <obj>, ... =] <message>"
            string += "\n@remit           [<obj>, <obj>, ... =] <message>"
            string += "\n@pemit           [<obj>, <obj>, ... =] <message>"
            caller.msg(string)
            return 

        rooms_only = 'rooms' in self.switches
        players_only = 'players' in self.switches
        send_to_contents = 'contents' in self.switches
        
        # we check which command was used to force the switches
        if self.cmdstring == '@remit':
            rooms_only = True
        elif self.cmdstring == '@pemit':
            players_only = True

        if not self.rhs:
            message = self.args
            objnames = [caller.location.key]
        else:
            message = self.rhs
            objnames = self.lhslist
            
        # send to all objects
        for objname in objnames:
            obj = caller.search(objname, global_search=True)
            if not obj:
                return 
            if rooms_only and not obj.location == None:
                caller.msg("%s is not a room. Ignored." % objname)
                continue
            if players_only and not obj.has_player:
                caller.msg("%s has no active player. Ignored." % objname)
                continue
            if obj.access(caller, 'tell'):
                obj.msg(message)
                if send_to_contents:
                    for content in obj.contents:
                        content.msg(message)
                    caller.msg("Emitted to %s and its contents." % objname)
                else:
                    caller.msg("Emitted to %s." % objname)
            else:
                caller.msg("You are not allowed to send to %s." % objname)



class CmdNewPassword(MuxCommand):
    """
    @setpassword

    Usage:
      @userpassword <user obj> = <new password>

    Set a player's password.
    """
    
    key = "@userpassword"
    locks = "cmd:perm(newpassword) or perm(Wizards)"
    help_category = "Admin"

    def func(self):
        "Implement the function."

        caller = self.caller

        if not self.rhs:
            caller.msg("Usage: @userpassword <user obj> = <new password>")
            return 
        
        # the player search also matches 'me' etc. 
        player = caller.search("*%s" % self.lhs, global_search=True, player=True)            
        if not player:
            return     
        player.user.set_password(self.rhs)
        player.user.save()
        caller.msg("%s - new password set to '%s'." % (player.name, self.rhs))
        if player.character != caller:
            player.msg("%s has changed your password to '%s'." % (caller.name, self.rhs))


class CmdPerm(MuxCommand):
    """
    @perm - set permissions

    Usage:
      @perm[/switch] <object> [= <permission>[,<permission>,...]]
      @perm[/switch] *<player> [= <permission>[,<permission>,...]]
      
    Switches:
      del : delete the given permission from <object> or <player>.
      player : set permission on a player (same as adding * to name)

    This command sets/clears individual permission strings on an object 
    or player. If no permission is given, list all permissions on <object>.
    """
    key = "@perm"
    aliases = "@setperm"
    locks = "cmd:perm(perm) or perm(Immortals)"
    help_category = "Admin"

    def func(self):
        "Implement function"

        caller = self.caller
        switches = self.switches
        lhs, rhs = self.lhs, self.rhs

        if not self.args:            
            string = "Usage: @perm[/switch] object [ = permission, permission, ...]" 
            caller.msg(string)
            return
        
        playermode = 'player' in self.switches or lhs.startswith('*')
        
        # locate the object        
        obj = caller.search(lhs, global_search=True, player=playermode)
        if not obj:
            return         
                
        if not rhs: 
            if not obj.access(caller, 'examine'):
                caller.msg("You are not allowed to examine this object.")
                return

            string = "Permissions on {w%s{n: " % obj.key
            if not obj.permissions:
                string += "<None>"
            else:
                string += ", ".join(obj.permissions)
                if hasattr(obj, 'player') and hasattr(obj.player, 'is_superuser') and obj.player.is_superuser:
                    string += "\n(... but this object is currently controlled by a SUPERUSER! "
                    string += "All access checks are passed automatically.)"            
            caller.msg(string)
            return 
            
        # we supplied an argument on the form obj = perm

        if not obj.access(caller, 'control'):
            caller.msg("You are not allowed to edit this object's permissions.")
            return         

        cstring = ""
        tstring = ""
        if 'del' in switches:
            # delete the given permission(s) from object.
            for perm in self.rhslist:
                try:
                    index = obj.permissions.index(perm)
                except ValueError:
                    cstring += "\nPermission '%s' was not defined on %s." % (perm, obj.name)
                    continue
                permissions = obj.permissions
                del permissions[index]
                obj.permissions = permissions 
                cstring += "\nPermission '%s' was removed from %s." % (perm, obj.name)
                tstring += "\n%s revokes the permission '%s' from you." % (caller.name, perm)
        else:
            # add a new permission             
            permissions = obj.permissions

            caller.permissions 
            


            for perm in self.rhslist:
                
                # don't allow to set a permission higher in the hierarchy than the one the
                # caller has (to prevent self-escalation)
                if perm.lower() in PERMISSION_HIERARCHY and not obj.locks.check_lockstring(caller, "dummy:perm(%s)" % perm):
                    caller.msg("You cannot assign a permission higher than the one you have yourself.")
                    return 

                if perm in permissions:
                    cstring += "\nPermission '%s' is already defined on %s." % (rhs, obj.name)
                else:
                    permissions.append(perm)
                    obj.permissions = permissions
                    cstring += "\nPermission '%s' given to %s." % (rhs, obj.name)
                    tstring += "\n%s gives you the permission '%s'." % (caller.name, rhs)        
        caller.msg(cstring.strip())
        if tstring:
            obj.msg(tstring.strip())

class CmdWall(MuxCommand):
    """
    @wall

    Usage:
      @wall <message>
      
    Announces a message to all connected players.
    """
    key = "@wall"
    locks = "cmd:perm(wall) or perm(Wizards)"
    help_category = "Admin"

    def func(self):
        "Implements command"
        if not self.args:
            self.caller.msg("Usage: @wall <message>")
            return
        message = "%s shouts \"%s\"" % (self.caller.name, self.args)
        SESSIONS.announce_all(message)
