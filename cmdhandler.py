from traceback import format_exc
import commands_privileged
import commands_general
import commands_unloggedin
import functions_db

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
   return functions_db.list_search_object_namestr(exits, searchstr)

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

      if session.logged_in:
         # If it's prefixed by an '@', it's a staff command.
         if parsed_input['root_cmd'][0] != '@':
            cmd = getattr(commands_general, 'cmd_%s' % (parsed_input['root_cmd'],), None )
         else:
            parsed_input['root_cmd'] = parsed_input['root_cmd'][1:]
            cmd = getattr(commands_privileged, 'cmd_%s' % (parsed_input['root_cmd'],), None )
      else:
         cmd = getattr(commands_unloggedin, 'cmd_%s' % (parsed_input['root_cmd'],), None )
      
      if callable(cmd):
         cdat['uinput'] = parsed_input
         try:
            cmd(cdat)
         except:
            session.msg("Untrapped error, please file a bug report:\n%s" % (format_exc(),))
            functions_general.print_errmsg("Untrapped error, evoker %s: %s" %
               (session, format_exc()))
         return
      
      if session.logged_in:
         # If we're not logged in, don't check exits.
         pobject = session.get_pobject()
         exit_matches = match_exits(pobject, ' '.join(parsed_input['splitted']))
         if exit_matches:
            exit = exit_matches[0]
            if exit.get_home():
               cdat['uinput'] = parsed_input
               pobject.move_to(exit.get_home())
               commands_general.cmd_look(cdat)
            else:
               session.msg("That exit leads to nowhere.")
            return
         
      # If we reach this point, we haven't matched anything.   
      raise UnknownCommand
         
   except UnknownCommand:
      session.msg("Unknown command.")
   
