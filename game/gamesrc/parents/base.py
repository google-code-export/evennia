#------------------------------------------------------------
# The base player object
#------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User
from src.objects.models import BaseObject

class Player(BaseObject):
    user = models.ForeignKey(User)
    #TODO: Add stub functions

#------------------------------------------------------------
# The base in-game non-player object.
#------------------------------------------------------------

class Object(BaseObject):
    #TODO: Add stub functions
    pass 
