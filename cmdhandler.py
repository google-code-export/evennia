from traceback import format_exc
import time

import defines_global
import cmdtable
import functions_db
import functions_general
import functions_comsys

"""
This is the command processing module. It is instanced once in the main
server module and the handle() function is hit every time a player sends
something.
"""

class UnknownCommand(Exception):
   """
   Throw this when a user enters an an invalid command.
   """

def match_exits(pobject, searchstr):
   """
   See if we can find an input match to exits.
   """
   exits = pobject.get_location().get_contents(filter_type=4)
   return functions_db.list_search_object_namestr(exits, searchstr, match_type="exact")

def handle(cdat):
   """
   Use the spliced (list) uinput variable to retrieve the correct
   command, or return an invalid command error.

   We're basically grabbing the player's command by tacking
   their input on to 'cmd_' and looking it up in the GenCommands
   class.
   """
   session = cdat['session']
   server = cdat['server']
   
   try:
      # TODO: Protect against non-standard characters.
      if cdat['uinput'] == '':
         raise UnknownCommand

      uinput = cdat['uinput'].split()
      parsed_input = {}

      # First we split the input up by spaces.
      parsed_input['splitted'] = uinput
      # Now we find the root command chunk (with switches attached).
      parsed_input['root_chunk'] = parsed_input['splitted'][0].split('/')
      # And now for the actual root command. It's the first entry in root_chunk.
      parsed_input['root_cmd'] = parsed_input['root_chunk'][0].lower()

      # Now we'll see if the user is using an alias. We do a dictionary lookup,
      # if the key (the player's root command) doesn't exist on the dict, we
      # don't replace the existing root_cmd. If the key exists, its value
      # replaces the previously splitted root_cmd. For example, sa -> say.
      alias_list = server.cmd_alias_list
      parsed_input['root_cmd'] = alias_list.get(parsed_input['root_cmd'],parsed_input['root_cmd'])

      # This will hold the reference to the command's function.
      cmd = None

      if session.logged_in:
         # Store the timestamp of the user's last command.
         session.cmd_last = time.time()

         # Lets the users get around badly configured NAT timeouts.
         if parsed_input['root_cmd'] == 'idle':
            return

         # Increment our user's command counter.
         session.cmd_total += 1
         # Player-visible idle time, not used in idle timeout calcs.
         session.cmd_last_visible = time.time()

         # Just in case. Prevents some really funky-case crashes.
         if len(parsed_input['root_cmd']) == 0:
            raise UnknownCommand

         # Shortened say alias.
         if parsed_input['root_cmd'][0] == '"':
            parsed_input['splitted'].insert(0, "say")
            parsed_input['splitted'][1] = parsed_input['splitted'][1][1:]
            parsed_input['root_cmd'] = 'say'
         # Shortened pose alias.
         elif parsed_input['root_cmd'][0] == ':':
            parsed_input['splitted'].insert(0, "pose")
            parsed_input['splitted'][1] = parsed_input['splitted'][1][1:]
            parsed_input['root_cmd'] = 'pose'
         # Pose without space alias.
         elif parsed_input['root_cmd'][0] == ';':
            parsed_input['splitted'].insert(0, "pose/nospace")
            parsed_input['root_chunk'] = ['pose', 'nospace']
            parsed_input['splitted'][1] = parsed_input['splitted'][1][1:]
            parsed_input['root_cmd'] = 'pose'
         # Channel alias match.
         elif functions_comsys.plr_has_channel(session, 
            parsed_input['root_cmd'], 
            alias_search=True, 
            return_muted=True):
            
            calias = parsed_input['root_cmd']
            cname = functions_comsys.plr_cname_from_alias(session, calias)
            cmessage = ' '.join(parsed_input['splitted'][1:])
            
            if cmessage == "who":
               functions_comsys.msg_cwho(session, cname)
               return
            elif cmessage == "on":
               functions_comsys.plr_chan_on(session, calias)
               return
            elif cmessage == "off":
               functions_comsys.plr_chan_off(session, calias)
               return
            elif cmessage == "last":
               functions_comsys.msg_chan_hist(session, cname)
               return
               
            second_arg = "%s=%s" % (cname, cmessage)
            parsed_input['splitted'] = ["@cemit/sendername", second_arg]
            parsed_input['root_chunk'] = ['@cemit', 'sendername', 'quiet']
            parsed_input['root_cmd'] = '@cemit'

         # Get the command's function reference (Or False)
         cmdtuple = cmdtable.return_cmdtuple(parsed_input['root_cmd'])
         if cmdtuple:
            # If there is a permissions element to the entry, check perms.
            if cmdtuple[1]:
               if not session.get_pobject().user_has_perm_list(cmdtuple[1]):
                  session.msg(defines_global.NOPERMS_MSG)
                  return
            # If flow reaches this point, user has perms and command is ready.
            cmd = cmdtuple[0]
               
      else:
         # Not logged in, look through the unlogged-in command table.
         cmdtuple = cmdtable.return_cmdtuple(parsed_input['root_cmd'], unlogged_cmd=True)
         if cmdtuple:
            cmd = cmdtuple[0]

      # Debugging stuff.
      #session.msg("ROOT : %s" % (parsed_input['root_cmd'],))
      #session.msg("SPLIT: %s" % (parsed_input['splitted'],))
      
      if callable(cmd):
         cdat['uinput'] = parsed_input
         try:
            cmd(cdat)
         except:
            session.msg("Untrapped error, please file a bug report:\n%s" % (format_exc(),))
            functions_general.log_errmsg("Untrapped error, evoker %s: %s" %
               (session, format_exc()))
         return

      if session.logged_in:
         # If we're not logged in, don't check exits.
         pobject = session.get_pobject()
         exit_matches = match_exits(pobject, ' '.join(parsed_input['splitted']))
         if exit_matches:
            targ_exit = exit_matches[0]
            if targ_exit.get_home():
               cdat['uinput'] = parsed_input
               
               # SCRIPT: See if the player can traverse the exit
               if not targ_exit.get_scriptlink().default_lock({
                  "pobject": pobject
               }):
                  session.msg("You can't traverse that exit.")
               else:
                  pobject.move_to(targ_exit.get_home())
                  session.execute_cmd("look")
            else:
               session.msg("That exit leads to nowhere.")
            return

      # If we reach this point, we haven't matched anything.   
      raise UnknownCommand

   except UnknownCommand:
      session.msg("Huh?  (Type \"help\" for help.)")

