from src.objects.models import Object as OBJECT
from django.db import models
from django.contrib.auth.models import User
from src.objects.models import AttributeField

class Object(OBJECT):
    pass

class Player(Object):
    user = models.ForeignKey(User)
    pc = True
    MONEY = AttributeField(default=0)

from django.db.models.loading import register_models, get_model
import red
if red.RedButton._meta.abstract:
   register_models("game", red.RedButton)
