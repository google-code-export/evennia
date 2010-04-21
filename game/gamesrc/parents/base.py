#------------------------------------------------------------
# The base player object
#------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User
from src.objects.models import Object as ObjectBase

class Player(ObjectBase):
    user = models.ForeignKey(User)
    #TODO: Add stub functions

#------------------------------------------------------------
# The base in-game non-player object.
#------------------------------------------------------------

class Object(ObjectBase):
    #TODO: Add stub functions
    pass 


    
