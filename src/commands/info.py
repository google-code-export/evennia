"""
Commands that are generally staff-oriented that show information regarding
the server instance.
"""
import os
import time
from src.util import functions_general
if not functions_general.host_os_is('nt'):
    # Don't import the resource module if the host OS is Windows.
    import resource
import django
from django.conf import settings
from src.objects.models import Object
from src import scheduler
from src import defines_global
from src import flags
from src.cmdtable import GLOBAL_CMD_TABLE
from src import gametime 

def cmd_version(command):
    """
    @version - game version

    Usage:
      @version

    Display the game version info
    """
    retval = "-"*50 +"\n\r"
    retval += " Evennia %s\n\r" % (defines_global.EVENNIA_VERSION,)
    retval += " Django %s\n\r" % (django.get_version())
    retval += "-"*50
    command.source_object.emit_to(retval)
GLOBAL_CMD_TABLE.add_command("@version", cmd_version, help_category="Admin"),

def cmd_time(command):
    """
    @time

    Usage:
      @time 
    
    Server local time.
    """
    gtime = gametime.time()
    gtime_h = functions_general.time_format(gtime, style=2)
    ictime = gtime * settings.TIME_FACTOR
    ictime_h = functions_general.time_format(ictime, style=2)
    uptime =  time.time() - command.session.server.start_time    
    uptime_h = functions_general.time_format(uptime, style=2)
    synctime = gametime.time_last_sync()
    synctime_h = functions_general.time_format(synctime, style=2)
    ltime = time.strftime('%a %b %d %H:%M:%S %Y (%Z)', time.localtime())    
    string = " Real-world times:"
    string += "\n -- Main time counter: %s (%i s)." % (gtime_h, gtime)

    string += "\n -- Time since last reboot: %s (%i s). " % (uptime_h, uptime) 
    string += "\n -- Current server time: %s" % ltime
    string +=  "\n In-game time (time factor %s):" % settings.TIME_FACTOR
    string += "\n -- Time passed: %s" % ictime_h                                         

    command.source_object.emit_to(string)

GLOBAL_CMD_TABLE.add_command("@time", cmd_time,  priv_tuple=("genperms.game_info",),
                             help_category="Admin")

def cmd_uptime(command):
    """
    @uptime

    Usage:
      @uptime

    Server uptime and stats.
    """
    source_object = command.source_object
    server = command.session.server
    start_delta = time.time() - server.start_time
    
    string = " Server time info:"
    string += "\n -- Current server time : %s" % \
              (time.strftime('%a %b %d %H:%M %Y (%Z)', time.localtime(),))
    string += "\n -- Server start time   : %s" % \
              (time.strftime('%a %b %d %H:%M %Y',
                             time.localtime(server.start_time),))
    string += "\n -- Server uptime       : %s" % \
                (functions_general.time_format(start_delta, style=2))        
    if not functions_general.host_os_is('nt'):
        # os.getloadavg() is not available on Windows.
        loadavg = os.getloadavg()
        string += "\n -- Server load (1 min) : %.2f" % loadavg[0]
    source_object.emit_to(string)
GLOBAL_CMD_TABLE.add_command("@uptime",
                             cmd_uptime,
                             priv_tuple=("genperms.game_info",),
                             help_category="Admin")

def cmd_list(command):
    """ 
    @list - list info

    Usage:
      @list commands | flags | process
    
    Shows game related information depending
    on which argument is given. 
    """
    server = command.session.server
    source_object = command.source_object
    
    msg_invalid = "Usage @list commands|flags|process"
    
    if not command.command_argument:    
        source_object.emit_to(msg_invalid)
    elif command.command_argument == "commands":
        clist = GLOBAL_CMD_TABLE.ctable.keys()
        clist.sort()
        source_object.emit_to('Commands: '+ ' '.join(clist))
    elif command.command_argument == "process":
        if not functions_general.host_os_is('nt'):
            loadvg = os.getloadavg()
            psize = resource.getpagesize()
            rusage = resource.getrusage(resource.RUSAGE_SELF)
            source_object.emit_to("Process ID:  %10d         %10d bytes per page" % 
                                  (os.getpid(), psize))
            source_object.emit_to("Time used:   %10d user    %10d sys" % 
                                  (rusage[0],rusage[1]))
            source_object.emit_to("Integral mem:%10d shared  %10d private%10d stack" % 
                                  (rusage[3], rusage[4], rusage[5]))
            source_object.emit_to("Max res mem: %10d pages   %10d bytes" % 
                                  (rusage[2],rusage[2] * psize))
            source_object.emit_to("Page faults: %10d hard    %10d soft   %10d swapouts" % 
                                  (rusage[7], rusage[6], rusage[8]))
            source_object.emit_to("Disk I/O:    %10d reads   %10d writes" % 
                                  (rusage[9], rusage[10]))
            source_object.emit_to("Network I/O: %10d in      %10d out" % 
                                  (rusage[12], rusage[11]))
            source_object.emit_to("Context swi: %10d vol     %10d forced %10d sigs" % 
                                  (rusage[14], rusage[15], rusage[13]))
        else:
            source_object.emit_to("Feature not available on Windows.")
            return
    elif command.command_argument == "flags":
        source_object.emit_to("Flags: "+" ".join(flags.SERVER_FLAGS))
    else:
        source_object.emit_to(msg_invalid)
GLOBAL_CMD_TABLE.add_command("@list", cmd_list,priv_tuple=("genperms.game_info",), help_category="Admin")

def cmd_ps(command):
    """
    @ps - list processes

    Usage
      @ps 

    Shows the process/event table.
    """
    source_object = command.source_object
    
    source_object.emit_to("Processes Scheduled:\n-- PID [time/interval] [repeats] description --")
    for event in scheduler.SCHEDULE:
        repeats = "[inf] "
        if event.repeats != None: 
            repeats = "[%i] " % event.repeats
        source_object.emit_to("   %i [%d/%d] %s%s" % (
            event.pid,
            event.get_nextfire(),
            event.interval,
            repeats,
            event.description))        
    source_object.emit_to("Totals: %d interval events" % (len(scheduler.SCHEDULE),))
GLOBAL_CMD_TABLE.add_command("@ps", cmd_ps,
                             priv_tuple=("genperms.process_control",), help_category="Admin")

def cmd_stats(command):
    """
    @stats - show object stats

    Usage:
      @stats

    Example:
      @stats
        -> 
      4012 objects = 144 rooms, 212 exits, 613 things, 1878 players. (1165 garbage)

    Shows stats about the database.
    """

    stats_dict = Object.objects.object_totals()
    command.source_object.emit_to(
        "%d objects = %d rooms, %d exits, %d things, %d players. (%d garbage)" % 
       (stats_dict["objects"],
        stats_dict["rooms"],
        stats_dict["exits"],
        stats_dict["things"],
        stats_dict["players"],
        stats_dict["garbage"]))
GLOBAL_CMD_TABLE.add_command("@stats", cmd_stats, priv_tuple=("genperms.game_info",), help_category="Admin"),
