"""
Models for the help system.

The database-tied help system is only half of Evennia's help
functionality, the other one being the auto-generated command help
that is created on the fly from each command's __doc__ string. The
persistent database system defined here is intended for all other
forms of help that do not concern commands, like information about the
game world, policy info, rules and similar.

"""
from django.db import models
from src.utils.idmapper.models import SharedMemoryModel
from src.help.manager import HelpEntryManager
from src.utils import ansi
from src.locks.lockhandler import LockHandler
from src.utils.utils import is_iter

#------------------------------------------------------------
#
# HelpEntry
#
#------------------------------------------------------------

class HelpEntry(SharedMemoryModel):
    """
    A generic help entry.

    An HelpEntry object has the following properties defined:
      key - main name of entry
      help_category - which category entry belongs to (defaults to General)
      entrytext - the actual help text
      permissions - perm strings

    """

    #
    # HelpEntry Database Model setup
    #
    #
    # These database fields are all set using their corresponding properties,
    # named same as the field, but withtout the db_* prefix.

    # title of the help 
    db_key = models.CharField(max_length=255, unique=True)
    # help category 
    db_help_category = models.CharField(max_length=255, default="General")
    # the actual help entry text, in any formatting. 
    db_entrytext = models.TextField(blank=True)  
    # a string of permissionstrings, separated by commas. 
    db_permissions = models.CharField(max_length=255, blank=True)    
    # lock string storage
    db_lock_storage = models.CharField(max_length=512, blank=True)
    # (deprecated, only here to allow MUX helpfile load (don't use otherwise)).
    # TODO: remove this when not needed anymore. 
    db_staff_only = models.BooleanField(default=False) 

    # Database manager
    objects = HelpEntryManager()

    def __init__(self, *args, **kwargs):
        SharedMemoryModel.__init__(self, *args, **kwargs)
        self.locks = LockHandler(self)
        
    class Meta:
        "Define Django meta options"
        verbose_name = "Help Entry"
        verbose_name_plural = "Help Entries"

    # Wrapper properties to easily set database fields. These are
    # @property decorators that allows to access these fields using
    # normal python operations (without having to remember to save()
    # etc). So e.g. a property 'attr' has a get/set/del decorator
    # defined that allows the user to do self.attr = value, 
    # value = self.attr and del self.attr respectively (where self 
    # is the object in question).
        
    # key property (wraps db_key)
    #@property
    def key_get(self):
        "Getter. Allows for value = self.key"
        return self.db_key
    #@key.setter
    def key_set(self, value):
        "Setter. Allows for self.key = value"
        self.db_key = value
        self.save()
    #@key.deleter
    def key_del(self):
        "Deleter. Allows for del self.key. Deletes entry."
        self.delete()
    key = property(key_get, key_set, key_del)

    # help_category property (wraps db_help_category)
    #@property
    def help_category_get(self):
        "Getter. Allows for value = self.help_category"
        return self.db_help_category
    #@help_category.setter
    def help_category_set(self, value):
        "Setter. Allows for self.help_category = value"
        self.db_help_category = value
        self.save()
    #@help_category.deleter
    def help_category_del(self):
        "Deleter. Allows for del self.help_category"
        self.db_help_category = "General"
        self.save()
    help_category = property(help_category_get, help_category_set, help_category_del)

    # entrytext property (wraps db_entrytext)
    #@property
    def entrytext_get(self):
        "Getter. Allows for value = self.entrytext"
        return self.db_entrytext
    #@entrytext.setter
    def entrytext_set(self, value):
        "Setter. Allows for self.entrytext = value"
        self.db_entrytext = value
        self.save()
    #@entrytext.deleter
    def entrytext_del(self):
        "Deleter. Allows for del self.entrytext"
        self.db_entrytext = ""
        self.save()
    entrytext = property(entrytext_get, entrytext_set, entrytext_del)

    # permissions property
    #@property
    def permissions_get(self):
        "Getter. Allows for value = self.permissions. Returns a list of permissions."
        return [perm.strip() for perm in self.db_permissions.split(',')]
    #@permissions.setter
    def permissions_set(self, value):
        "Setter. Allows for self.permissions = value. Stores as a comma-separated string."
        if is_iter(value):
            value = ",".join([str(val).strip().lower() for val in value])
        self.db_permissions = value
        self.save()        
    #@permissions.deleter
    def permissions_del(self):
        "Deleter. Allows for del self.permissions"
        self.db_permissions = ""
        self.save()
    permissions = property(permissions_get, permissions_set, permissions_del)

        # lock_storage property (wraps db_lock_storage)
    #@property 
    def lock_storage_get(self):
        "Getter. Allows for value = self.lock_storage"
        return self.db_lock_storage
    #@nick.setter
    def lock_storage_set(self, value):
        """Saves the lock_storagetodate. This is usually not called directly, but through self.lock()"""
        self.db_lock_storage = value
        self.save()
    #@nick.deleter
    def lock_storage_del(self):
        "Deleter is disabled. Use the lockhandler.delete (self.lock.delete) instead"""
        logger.log_errmsg("Lock_Storage (on %s) cannot be deleted. Use obj.lock.delete() instead." % self)
    lock_storage = property(lock_storage_get, lock_storage_set, lock_storage_del)

    
    #
    #
    # HelpEntry main class methods
    #
    #
        
    def __str__(self):
        return self.key

    def __unicode__(self):
        return u'%s' % self.key

    def access(self, accessing_obj, access_type='read', default=False):
        """
        Determines if another object has permission to access.
        accessing_obj - object trying to access this one
        access_type - type of access sought
        default - what to return if no lock of access_type was found
        """        
        return self.locks.check(accessing_obj, access_type=access_type, default=default)
