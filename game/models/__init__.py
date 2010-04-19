from src.objects.models import Object as OBJECT, Primitive
from django.db import models
from django.contrib.auth.models import User
from src.objects.models import AttributeField
from src.locks import Locks

class Object(OBJECT):
    LOCKS = AttributeField(default=Locks())
    SAFE = AttributeField(default=False)
    msg = OBJECT.emit_to

# the session-handler expects players to have a user attribute
# and evennia expects that it descends from OBJECT somewhere
# other than that, nothing special about a player


#room redefined in rhns
#class Room(Object):
#    pass

# exits are just objects with a destination attribute that points to an object

from django.db.models.loading import register_models, get_model
import red
if red.RedButton._meta.abstract:
   register_models("game", red.RedButton)

# MY GAME SPECIFIC STUFF STARTS HERE
# NOTE HOW EVERYTHING IS DESCENDED FROM THING!
#from rhns import *
import os.path
from game.settings import GAME_DIR
for include_file in ["rhns.py"]:
    filename = os.path.join(GAME_DIR, "models", include_file)
    execfile(filename)

class Exit(Object):
    destination = PolymorphicPrimitiveForeignKey(blank=True,null=True,db_index=True)
    #destination = models.ForeignKey(Object,related_name = "_exits")
    #destination = models.IntegerField()

class Player(Combatant):
    user = models.ForeignKey(User)
    # mush combat
    MONEY = AttributeField(default=0)
    # the only thing different from a normal Object is that the session handler expects
    # it to have a user
    pc = True
    npc = False
    pc = False
    immort = False
    is_staff = lambda self: self.user.is_staff
