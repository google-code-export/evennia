from django.db import models
from django.contrib.auth.models import User
from src.objects.models import BaseObject

#------------------------------------------------------------
# The base player object
#------------------------------------------------------------

class Player(BaseObject):
    user = models.ForeignKey(User)
    #TODO: Add stub functions

#------------------------------------------------------------
# The base in-game non-player object.
#------------------------------------------------------------

class Object(BaseObject):
    #TODO: Add stub functions
    pass 

#------------------------------------------------------------
# The base in-game room object.
#------------------------------------------------------------

class Room(BaseObject):
    #TODO: Add stub functions
    pass
