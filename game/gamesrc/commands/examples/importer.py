from game.gamesrc.commands.default.muxcommand import MuxCommand
from game.gamesrc.world.fuss_importer.download import download_and_parse
from django.conf import settings
from src.utils import create 
from src.objects.models import ObjectDB


class CmdFussImport(MuxCommand):
    """
    Imports data from a .tgz of a FUSS game directory.

    Usage:
      @fussimport

    This downloads the tgz and does the import.
    """
    key = "@fussimport"
    permissions = "cmd:reload"
    help_category = "System"

    def func(self):
        """
        Import a fuss .tgz.
        """        
        caller = self.caller 
        url = settings.DEFAULT_FUSS_TGZ_DOWNLOAD_URL
        expected_checksum = settings.DEFAULT_FUSS_TGZ_DOWNLOAD_CHECKSUM
        caller.msg("Downloading and parsing, this may take a bit.")
        dom = download_and_parse(url, expected_checksum)
        roomNodeList = dom.getElementsByTagName("room")
        # first import rooms
        for room in roomNodeList:
	    room_alias = room.getAttribute("Vnum")
	    room_name = room.getAttribute("Name")
	    new_room = create.create_object(settings.BASE_ROOM_TYPECLASS, room_name, aliases=["#%sr" % room_alias])
            new_room.db.vnum = "#%sr" % room_alias
        # then import doors
        #for room in roomNodeList:
        #    exitNodeList = dom.getElementsByTagName("door")
        #    room = 
        results = ObjectDB.objects.get_objs_with_attr_match("vnum", "10300r")
        caller.msg("Found %s items  with vnum = 10300r." % len(results))
            
        caller.msg("Done.")
        caller.msg("Found %s rooms." % len(roomNodeList))
