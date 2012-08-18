"""
This implements the common managers that are used by the
abstract models in dbobjects.py (and which are thus shared by
all Attributes and TypedObjects).
"""
from functools import update_wrapper
from django.db import models
from src.utils import idmapper
from src.utils.utils import make_iter
__all__ = ("AttributeManager", "TypedObjectManager")

# Managers

class AttributeManager(models.Manager):
    "Manager for handling Attributes."

    def attr_namesearch(self, searchstr, obj, exact_match=True):
        """
        Searches the object's attributes for name matches.

        searchstr: (str) A string to search for.
        """
        # Retrieve the list of attributes for this object.
        if exact_match:
            return self.filter(db_obj=obj).filter(
                db_key__iexact=searchstr)
        else:
            return self.filter(db_obj=obj).filter(
                db_key__icontains=searchstr)

#
# helper functions for the TypedObjectManager.
#

def returns_typeclass_list(method):
    """
    Decorator: Chantes return of the decorated method (which are
    TypeClassed objects) into object_classes(s) instead.  Will always
    return a list (may be empty).
    """
    def func(self, *args, **kwargs):
        "decorator. Returns a list."
        self.__doc__ = method.__doc__
        matches = method(self, *args, **kwargs)
        return [(hasattr(dbobj, "typeclass") and dbobj.typeclass) or dbobj for dbobj in make_iter(matches)]
    return update_wrapper(func, method)

def returns_typeclass(method):
    """
    Decorator: Will always return a single typeclassed result or None.
    """
    def func(self, *args, **kwargs):
        "decorator. Returns result or None."
        self.__doc__ = method.__doc__
        rfunc = returns_typeclass_list(method)
        try:
            return rfunc(self, *args, **kwargs)[0]
        except IndexError:
            return None
    return update_wrapper(func, method)


#class TypedObjectManager(idmap.CachingManager):
#class TypedObjectManager(models.Manager):
class TypedObjectManager(idmapper.manager.SharedMemoryManager):
    """
    Common ObjectManager for all dbobjects.
    """

    def dbref(self, dbref):
        """
        Valid forms of dbref (database reference number)
        are either a string '#N' or an integer N.
        Output is the integer part.
        """
        if isinstance(dbref, basestring):
            dbref = dbref.lstrip('#')
        try:
            if int(dbref) < 0:
                return None
        except Exception:
            return None
        return dbref

    @returns_typeclass_list
    def get_with_attr(self, attribute_name, attribute_value=None):
        """
        Returns the typeclassed entity depending on having a given attribute.

        attribute_name - only entities with an attribute of this name will be included in match
        attribute_value - if != None, only entities with db.attribute_name=attribute_value will match.
        """
        self.filter()


    @returns_typeclass
    def dbref_search(self, dbref):
        """
        Returns an object when given a dbref.
        """
        dbref = self.dbref(dbref)
        if dbref :
            try:
                return self.get(id=dbref)
            except self.model.DoesNotExist:
                return None
        return None

    @returns_typeclass_list
    def get_dbref_range(self, min_dbref=None, max_dbref=None):
        """
        Return all objects inside and including the
        given boundaries.
        """
        min_dbref, max_dbref = self.dbref(min_dbref), self.dbref(max_dbref)
        if not min_dbref or not max_dbref:
            return self.all()
        if not min_dbref:
            return self.filter(id__lte=max_dbref)
        elif not max_dbref:
            return self.filter(id__gte=min_dbref)
        return self.filter(id__gte=min_dbref).filter(id__lte=min_dbref)

    def get_id(self, idnum):
        """
        Alias to dbref_search
        """
        return self.dbref_search(idnum)

    def object_totals(self):
        """
        Returns a dictionary with all the typeclasses active in-game
        as well as the number of such objects defined (i.e. the number
        of database object having that typeclass set on themselves).
        """
        dbtotals = {}
        typeclass_paths = set(self.values_list('db_typeclass_path', flat=True))
        for typeclass_path in typeclass_paths:
            dbtotals[typeclass_path] = \
               self.filter(db_typeclass_path=typeclass_path).count()
        return dbtotals

    @returns_typeclass_list
    def typeclass_search(self, typeclass):
        """
        Searches through all objects returning those which has a certain
        typeclass. If location is set, limit search to objects in
        that location.
        """
        if callable(typeclass):
            cls = typeclass.__class__
            typeclass = "%s.%s" % (cls.__module__, cls.__name__)
        o_query = self.filter(db_typeclass_path__exact=typeclass)
        return o_query
