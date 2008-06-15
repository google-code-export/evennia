"""
The basic Player object script parent.
"""
import time

from src import comsys
from src.scripts.basicobject import BasicObject

class BasicPlayer(BasicObject):
    def at_pre_login(self):
        """
        Everything done here takes place before the player is actually
        'logged in', in a sense that they're not ready to send logged in
        commands or receive communication.
        """
        pobject = self.source_obj
        session = pobject.get_session()
        
        # Load the player's channels from their JSON __CHANLIST attribute.
        comsys.load_object_channels(pobject)
        pobject.set_attribute("Last", "%s" % (time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()),))
        pobject.set_attribute("Lastsite", "%s" % (session.address[0],))
        pobject.set_flag("CONNECTED", True)
        
    def at_post_login(self):
        """
        The user is now logged in. This is what happens right after the moment
        they are 'connected'.
        """
        pobject = self.source_obj
        session = pobject.get_session()
        
        session.msg("You are now logged in as %s." % (pobject.name,))
        pobject.get_location().emit_to_contents("%s has connected." % 
            (pobject.get_name(show_dbref=False),), exclude=pobject)
        session.execute_cmd("look")
        
def class_factory(source_obj):
    return BasicPlayer(source_obj)  
