"""
This is the base object type/interface that all parents are derived from by
default. Each object type sub-classes this class and over-rides methods as
needed. 

NOTE: This file should NOT be directly modified. Sub-class the BasicObject
class in game/gamesrc/parents/base/basicobject.py and change the 
SCRIPT_DEFAULT_OBJECT variable in settings.py to point to the new class. 
"""
from src.cmdtable import CommandTable
from src.ansi import ANSITable

class EvenniaBasicObject(object):
    def at_object_creation(self):
        """
        This is triggered after a new object is created and ready to go. If
        you'd like to set attributes, flags, or do anything when the object
        is created, do it here and not in __init__().
        """
        pass
    
    def at_object_destruction(self, pobject=None):
        """
        This is triggered when an object is about to be destroyed via
        @destroy ONLY. If an object is deleted via delete(), it is assumed
        that this method is to be skipped.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s looked at %s." % (pobject, self)
        pass
        
    def at_desc(self, pobject=None):
        """
        Perform this action when someone uses the LOOK command on the object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s looked at %s." % (pobject, self)
        pass

    def at_get(self, pobject):
        """
        Perform this action when someone uses the GET command on the object.
        
        values: 
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s got %s." % (pobject, self)
        pass

    def at_before_move(self, target_location):
        """
        This hook is called just before the object is moved.
        arg:
          target_location (obj): the place where this object is to be moved
        returns:
          if this function returns anything but None, the move is cancelled. 
        
        """
        pass

    def announce_move_from(self, target_location):
        """
        Called when announcing to leave a destination. 
        target_location - the place we are going to
        """
        loc = self.get_location()
        if loc:
            loc.emit_to_contents("%s has left." % self.get_name(), exclude=self)
            if loc.is_player():
                loc.emit_to("%s has left your inventory." % (self.get_name()))

    def announce_move_to(self, source_location):
        """
        Called when announcing one's arrival at a destination.
        source_location - the place we are coming from
        """
        loc = self.get_location()
        if loc: 
            loc.emit_to_contents("%s has arrived." % self.get_name(), exclude=self)
            if loc.is_player():
                loc.emit_to("%s is now in your inventory." % self.get_name())

    def at_after_move(self, old_loc=None):
        """
        This hook is called just after the object was successfully moved.
        No return values.
        """
        pass
    
    def at_drop(self, pobject):
        """
        Perform this action when someone uses the DROP command on the object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        # Un-comment the line below for an example
        #print "SCRIPT TEST: %s dropped %s." % (pobject, self)
        pass
    
    def at_obj_receive(self, object=None, old_loc=None):
        """
        Called whenever an object is added to the contents of this object.        
        """
        pass

    def return_appearance(self, pobject=None):
        """
        Returns a string representation of an object's appearance when LOOKed at.
        
        values: 
            * pobject: (Object) The object requesting the action.
        """
        # This is the object being looked at.
        target_obj = self        
        # See if the envoker sees dbref numbers.
        lock_msg = ""
        if pobject:        
            #check visibility lock
            if not target_obj.visible_lock(pobject):
                temp = target_obj.get_attribute_value("visible_lock_msg")
                if temp:
                    return temp
                return "I don't see that here."
            
            show_dbrefs = pobject.sees_dbrefs()                                        

            #check for the defaultlock, this shows a lock message after the normal desc, if one is defined.
            if target_obj.is_room() and \
                   not target_obj.default_lock(pobject):
                temp = target_obj.get_attribute_value("lock_msg")
                if temp:
                    lock_msg = "\n%s" % temp
        else:
            show_dbrefs = False
                        
        description = target_obj.get_attribute_value('desc')
        if description is not None:
            retval = "%s%s\r\n%s%s%s" % ("%ch",
                target_obj.get_name(show_dbref=show_dbrefs),
                target_obj.get_attribute_value('desc'), lock_msg,
                "%cn")
        else:
            retval = "%s%s%s" % ("%ch",
                                 target_obj.get_name(show_dbref=show_dbrefs),
                                 "%cn")

        # Storage for the different object types.
        con_players = []
        con_things = []
        con_exits = []
        
        for obj in target_obj.get_contents():
            # check visible lock.
            if pobject and not obj.visible_lock(pobject):
                continue
            if obj.is_player():
                if (obj != pobject and obj.is_connected_plr()) or pobject == None:            
                    con_players.append(obj)
            elif obj.is_exit():
                con_exits.append(obj)
            else:
                con_things.append(obj)
        
        if not con_players == []:
            retval += "\n\r%sPlayers:%s" % (ANSITable.ansi["hilite"], 
                                            ANSITable.ansi["normal"])
            for player in con_players:
                retval +='\n\r%s' % (player.get_name(show_dbref=show_dbrefs),)
        if not con_things == []:
            retval += "\n\r%sYou see:%s" % (ANSITable.ansi["hilite"], 
                                             ANSITable.ansi["normal"])
            for thing in con_things:
                retval += '\n\r%s' % (thing.get_name(show_dbref=show_dbrefs),)
        if not con_exits == []:
            retval += "\n\r%sExits:%s" % (ANSITable.ansi["hilite"], 
                                          ANSITable.ansi["normal"])
            for exit in con_exits:
                retval += '\n\r%s' %(exit.get_name(show_dbref=show_dbrefs),)

        return retval

    def default_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for picking up
        objects or traversing exits.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.scripted_obj.get_attribute_value("LOCKS")
        if locks: 
            return locks.check("DefaultLock", pobject)
        else:
            return True

    def use_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for seeing whether
        a player can use an object or any of its commands.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.scripted_obj.get_attribute_value("LOCKS")
        if locks: 
            return locks.check("UseLock", pobject)
        else:
            return True

    def enter_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for seeing whether
        a player can enter another object.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.scripted_obj.get_attribute_value("LOCKS")
        if locks: 
            return locks.check("EnterLock", pobject)
        else:
            return True

    def visible_lock(self, pobject):
        """
        This method returns a True or False boolean value to determine whether
        the actor passes the lock. This is generally used for picking up
        objects or traversing exits.
        
        values:
            * pobject: (Object) The object requesting the action.
        """
        locks = self.scripted_obj.get_attribute_value("LOCKS")
        if locks: 
            return locks.check("VisibleLock", pobject)
        else:
            return True
    
    def lock_func(self, obj):
        """
        This is a custom function called by locks with the FuncKey key. Its
        return value should match that specified in the lock (so no true/false
        lock result is actually determined in here). Default desired return
        value is True. Also remember that the comparison in FuncKey is made
        using the string representation of the return value, since @lock can
        only define string lock criteria. 
        """
        return False
