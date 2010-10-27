from game.gamesrc.commands.default.muxcommand import MuxCommand
from game.gamesrc.world.fuss_importer.download import download_and_parse, parse_local
from django.conf import settings
from src.utils import create 
from src.objects.models import ObjectDB
from django.db.transaction import commit_on_success

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
        if not hasattr(self, "dom"):
            self.download_files()

        self.import_rooms()
        self.import_exits()
        self.caller.msg("Done.")

    def importing(self, area_name):
        return True

    @commit_on_success
    def import_rooms(self):
        roomNodeList = self.dom.getElementsByTagName("room")
        # first import rooms
        for roomNode in roomNodeList:
            area_name = roomNode.parentNode.getElementsByTagName("area_data")[0].getAttribute("Name")
            if self.importing(area_name):
		room_alias = roomNode.getAttribute("Vnum")
		vnum = "#%sr" % roomNode.getAttribute("Vnum")
		vnum_result = self.caller.search(vnum, global_search=True)
		room_name = roomNode.getAttribute("Name")
		if not vnum_result:
		    room = create.create_object(settings.BASE_ROOM_TYPECLASS, room_name, aliases=vnum)
		else:
		    room = vnum_result
		    room.name = room_name
		room.set_attribute("desc", roomNode.getAttribute("Desc"))
    def import_exits(self):
         pass
            
    def download_files(self):
        if settings.DEFAULT_FUSS_TGZ_FILENAME:
	    self.caller.msg("Parsing %s." % settings.DEFAULT_FUSS_TGZ_FILENAME)
	    self.dom = parse_local(settings.DEFAULT_FUSS_TGZ_FILENAME)
        else:
	    url = settings.DEFAULT_FUSS_TGZ_DOWNLOAD_URL
	    expected_checksum = settings.DEFAULT_FUSS_TGZ_DOWNLOAD_CHECKSUM
	    self.caller.msg("Downloading and parsing, this may take a bit.")
	    self.dom = download_and_parse(url, expected_checksum)
