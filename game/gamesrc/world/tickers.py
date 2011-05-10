"""
This is a basic ticker system for the basicmud. 

"""
from random import random
from src.objects.models import ObjectDB
from game.gamesrc.scripts.basescript import Script

#
# Subscribable script 
# 
# This is a global script that objects can 
# subscribe to. 
#
#
# Note that these scripts should only be created once!
# They can be created using src.utils.create.create_script(), 
# possibly called from the smaug importer after first having
# checked that no same-key scripts are already available
# in the database. 
#

class Tick(Script):
    """
    Parent for all ticks; implements a subscribe/unsubscribe
    mechanism.
    """

    def at_script_creation(self):
        "Expand the base definition. Make sure to super() this in children."
        self.db.subscriptions = {}
        
    def at_start(self):
        """
        Called at start, at least once every server start.
        We move storage from attribute into memory cache for efficiency.
        """
        self.ndb.subscriptions = self.db.subscriptions

    def subscribe(self, obj):
        """
        An object sends itself to this script to subscribe. 
        """
        self.db.subscriptions[obj.id] = obj
        self.ndb.subscriptions[obj.id] = obj 

    def unsubscribe(self, obj):
        """
        An object sends itself to this script to unsubscribe.
        """
        if obj.id in self.db.subscriptions:
            del self.db.subscriptions[obj.id]
            del self.ndb.subscriptions[obj.id]

class CombatTick(Tick):
    """
    This is a fast-ticking tick for combat mobs. Mobs should
    subscribe to this when increasing their update pace. Will
    call the at_combat_tick() hook. 

    """
    def at_script_creation(self):
        "Called when script is first created."
        super(CombatTick, self).at_script_creation()
        self.key = "combat_tick"
        self.desc = "Ticks the mobs in combat mode"
        self.interval = 2 # seconds
        self.start_delay = True # wait at least self.interval seconds before calling at_repeat the first time
        self.persistent = True 
        
    def at_repeat(self):
        "Called when script repeats, every self.interval seconds."
        for obj in self.ndb.subscriptions.values():
            try:
                obj.at_combat()
            except Exception:
                # kill the errors 
                pass

class ResetTick(Tick):
    """
    This is a slow tick for eventual reset operations. 
    Calls at_reset_tick() on the subscribed typeclasses. 
    """
    def at_script_creation(self):
        "Called when script is first created."
        super(ResetTick, self).at_script_creation()
        self.key = "reset_tick"
        self.desc = "Ticks the reset counter"
        self.interval = 60 # seconds
        self.start_delay = False
        self.persistent = True 
        
    def at_repeat(self):
        "Called when script repeats, every self.interval seconds."
        for obj in self.ndb.subscriptions.values():
            try:
                obj.at_reset_tick()
            except Exception:
                # kill the errors 
                pass

class RandomTick(Tick):
    """
    This is a fast-ticking tick for combat mobs. Mobs should
    subscribe to this when increasing their update pace. 

    Calls at_random_tick() on subscribed objects. There is a random
    chance of calling each object, defined by the attribute
    random_chance.
    """
    def at_script_creation(self):
        "Called when script is first created."
        super(RandomTick, self).at_script_creation()
        self.key = "reset_tick"
        self.desc = "Ticks the reset counter"
        self.interval = 60 * 5 # seconds
        self.start_delay = True # wait at least self.interval seconds before calling at_repeat the first time
        self.persistent = True 
        self.db.random_chance = 0.2
        
    def at_repeat(self):
        "Called when script repeats, every self.interval seconds. Random call."
        rchance = self.rchance
        for obj in [obj for obj in self.ndb.subscriptions.values() if random() < rchance]:
            try:
                obj.at_random_tick()
            except Exception:
                # kill the errors 
                pass

#
# Example room typeclass working with the ticker system.
# (Split this out into a separate module as needed)
#

from django.conf import settings
from src.utils.utils import inherits_from 
from game.gamesrc.objects.baseobjects import Room

class TickerRoom(Room):
    """
    This is an example of using the ticker system. The Tickerroom
    will analyze objects entering it, and if the entered object
    inherits (at any distance) to BASE_CHARACTER_TYPECLASS, it will
    try to call the activate() hook on each object. The activate() method
    should make sure that the object subscribes to the right ticker and 
    track its state so it can switch between tickers as needed. When
    no players are left in the room, the room tries to deactivate all
    objects again by calling their deactivate() method. It's up to each
    object to act on this deactivation as desired (some mobs might instead
    want to follow the leaving player instead, for example).

    This object should be subscribed to the reset ticker so that it 
    detects characters inside it also if they are there during server start.

    """

    def at_reset(self):
        "Called by the reset script during startup and resets."
        for obj in self.contents:
            self.at_object_receive(obj, self)
    
    def at_object_receive(self, obj, source_location):
        """
        Called when a new object arrives in the room
        """
        if inherits_from(obj, settings.BASE_CHARACTER_TYPECLASS) and obj.has_player:
            # this is an active player character. 
            for tick_obj in (tobj for tobj in self.contents if tobj != obj):
                try:
                    tick_obj.activate() 
                except Exception:
                    # kill errors.
                    pass 

    def at_object_leave(self, obj, target_location):
        """
        Called when a new object leaves the room.
        """
        if not any(tobj for tobj in self.contents 
                   if tobj != obj and inherits_from(tobj, settings.BASE_CHARACTER_TYPECLASS) and not tobj.has_player):
            # no active players remain in the room. 
            for tick_obj in (tobj for tobj in self.contents if tobj != obj):
                try:
                    tick_obj.deactivate() 
                except Exception:
                    # kill errors.
                    pass 
