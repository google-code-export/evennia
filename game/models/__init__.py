from src.objects.models import Object as OBJECT
from django.db import models
from django.contrib.auth.models import User


class Object(OBJECT):
   pass
class Player(Object):
    user = models.ForeignKey(User)
    pc = True


#from django.db.models.loading import register_models, get_model
#register_models("game", red.RedButton)
#from django.contrib.contenttypes.models import ContentType
#ContentType.objects.get_or_create(app_label = "game", model="game.RedButton",name="game.RedButton")
