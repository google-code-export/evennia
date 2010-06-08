"""
Custom manager for Object objects.
"""
from datetime import datetime, timedelta

from django.db import models
from django.db import connection
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from src.config.models import ConfigValue
from src.objects.exceptions import ObjectNotExist
from src.objects.util import object as util_object
from src import defines_global
from src import logger

from django.db.models.query import QuerySet

class ObjectQuerySet(QuerySet):
    pass    
class ObjectManager(models.Manager):
    def get_query_set(self):
        return ObjectQuerySet(self.model)
 
    #
    # ObjectManager Get methods 
    #
    
    def num_total_players(self):
        """
        Returns the total number of registered players.
        """
        return User.objects.count()

    def get_connected_players(self):
        """
        Returns the a QuerySet containing the currently connected players.
        """
        # TODO gotta hit up the session manager for this
        return False

    def get_recently_created_users(self, days=7):
        """
        Returns a QuerySet containing the player User accounts that have been
        connected within the last <days> days.
        """
        end_date = datetime.now()
        tdelta = timedelta(days)
        start_date = end_date - tdelta
        return User.objects.filter(date_joined__range=(start_date, end_date))

    def get_recently_connected_users(self, days=7):
        """
        Returns a QuerySet containing the player User accounts that have been
        connected within the last <days> days.
        """
        end_date = datetime.now()
        tdelta = timedelta(days)
        start_date = end_date - tdelta
        return User.objects.filter(last_login__range=(start_date, end_date)).order_by('-last_login')
            
    def get_user_from_email(self, uemail):
        """
        Returns a player's User object when given an email address.
        """
        return User.objects.filter(email__iexact=uemail)

    def get_object_from_dbref(self, dbref):
        """
        Returns an object when given a dbref.
        """
        if type(dbref) == type(str()):            
            if len(dbref)>1 and dbref[0]=="#":
                dbref = dbref[1:]
        dbref = "%s" % dbref            
        try:
            return self.get(id=dbref)
        except self.model.DoesNotExist:
            raise ObjectNotExist(dbref)        

    def object_totals(self):
        """
        Returns a dictionary with database object totals.
        """
        dbtotals = {
            "objects": self.count(),
            "things": self.filter(type=defines_global.OTYPE_THING).count(),
            "exits": self.filter(type=defines_global.OTYPE_EXIT).count(),
            "rooms": self.filter(type=defines_global.OTYPE_ROOM).count(),
            "garbage": self.filter(type=defines_global.OTYPE_GARBAGE).count(),
            "players": self.filter(type=defines_global.OTYPE_PLAYER).count(),
        }
        return dbtotals

    def get_nextfree_dbnum(self):
        """
        Figure out what our next free database reference number is.
        
        If we need to recycle a GARBAGE object, return the object to recycle
        Otherwise, return the first free dbref.
        """
        # First we'll see if there's an object of type 6 (GARBAGE) that we
        # can recycle.
        nextfree = self.filter(type__exact=defines_global.OTYPE_GARBAGE)
        if nextfree:
            # We've got at least one garbage object to recycle.
            return nextfree[0]
        else:
            # No garbage to recycle, find the highest dbnum and increment it
            # for our next free.
            return int(self.order_by('-id')[0].id + 1)

    def is_dbref(self, dbstring, require_pound=True):
        """
        Is the input a well-formed dbref number?
        """
        return util_object.is_dbref(dbstring, require_pound=require_pound)


    #
    # ObjectManager Search methods
    #

    def dbref_search(self, dbref_string, limit_types=False):
        """
        Searches for a given dbref.

        dbref_number: (string) The dbref to search for. With # sign.
        limit_types: (list of int) A list of Object type numbers to filter by.
        """
        if not util_object.is_dbref(dbref_string):
            return None
        dbref_string = dbref_string[1:]
        dbref_matches = self.filter(id=dbref_string).exclude(
                type=defines_global.OTYPE_GARBAGE)
        # Check for limiters
        if limit_types is not False:
            for limiter in limit_types:
                dbref_matches.filter(type=limiter)
        try:
            return dbref_matches[0]
        except IndexError:
            return None

    def global_object_name_search(self, ostring, exact_match=True, limit_types=[]):
        """
        Searches through all objects for a name match.
        limit_types is a list of types as defined in defines_global. 
        """
        if self.is_dbref(ostring):
            o_query = self.dbref_search(ostring, limit_types=limit_types)
            if o_query:
                return [o_query]
            return None
        # get rough match 
        o_query = self.filter(name__icontains=ostring)
        o_query = o_query.exclude(type__in=[defines_global.OTYPE_GARBAGE,
                                            defines_global.OTYPE_GOING])
        if not o_query:
            # use list-search to catch N-style queries. Note
            # that we want to keep the original ostring since
            # search_object_namestr does its own N-string treatment
            # on this.
            dum, test_ostring = self._parse_match_number(ostring)
            o_query = self.filter(name__icontains=test_ostring)
            o_query = o_query.exclude(type__in=[defines_global.OTYPE_GARBAGE,
                                                defines_global.OTYPE_GOING])
        match_type = "fuzzy"
        if exact_match:
            match_type = "exact"        
        return self.list_search_object_namestr(o_query, ostring,
                                               limit_types=limit_types,
                                               match_type=match_type)
        return o_query.exclude(type__in=[defines_global.OTYPE_GARBAGE,
                                         defines_global.OTYPE_GOING])

    def global_object_script_parent_search(self, script_parent):
        """
        Searches through all objects returning those which has a certain script parent.
        """
        o_query = self.filter(script_parent__exact=script_parent)           
        return o_query.exclude(type__in=[defines_global.OTYPE_GARBAGE,
                                         defines_global.OTYPE_GOING])

    def local_object_script_parent_search(self, script_parent, location):
        o_query = self.filter(script_parent__exact=script_parent)        
        if o_query:
            o_query = o_query.filter(location__iexact=location)
        return o_query.exclude(type__in=[defines_global.OTYPE_GARBAGE,
                                         defines_global.OTYPE_GOING])

    
    def list_search_object_namestr(self, searchlist, ostring, dbref_only=False, 
                                   limit_types=False, match_type="fuzzy",
                                   attribute_name=None):

        """
        Iterates through a list of objects and returns a list of
        name matches.

        This version handles search criteria of the type N-keyword, this is used
        to differentiate several objects of the exact same name, e.g. 1-box, 2-box etc.
        
        searchlist:  (List of Objects) The objects to perform name comparisons on.
        ostring:     (string) The string to match against.
        dbref_only:  (bool) Only compare dbrefs.
        limit_types: (list of int) A list of Object type numbers to filter by.
        match_type: (string) 'exact' or 'fuzzy' matching.
        attribute_name: (string) attribute name to search, if None, 'name' is used. 

        Note that the fuzzy matching gives precedence to exact matches; so if your
        search query matches an object in the list exactly, it will be the only result.
        This means that if the list contains [box,box11,box12], the search string 'box'
        will only match the first entry since it is exact. The search 'box1' will however
        match both box11 and box12 since neither is an exact match.

        Uses two helper functions, _list_search_helper1/2. 
        """
        if dbref_only:
            #search by dbref - these must always be unique.
            if limit_types:
                return [prospect for prospect in searchlist
                        if prospect.dbref_match(ostring)
                        and prospect.type in limit_types]
            else:
                return [prospect for prospect in searchlist
                        if prospect.dbref_match(ostring)]

        #search by name - this may return multiple matches.
        results = self._match_name_attribute(searchlist,ostring,dbref_only,
                                            limit_types, match_type,
                                            attribute_name=attribute_name)
        match_number = None
        if not results:
            #if we have no match, check if we are dealing
            #with a "N-keyword" query - if so, strip it and run again. 
            match_number, ostring = self._parse_match_number(ostring)
            if match_number != None and ostring:
                results = self._match_name_attribute(searchlist,ostring,dbref_only,
                                                    limit_types, match_type,
                                                    attribute_name=attribute_name) 
        if match_type == "fuzzy":             
            #fuzzy matching; run second sweep to catch exact matches
            if attribute_name:
                exact_results = [prospect for prospect in results
                                 if ostring == getattr(prospect, attribute_name)]
            else:
                exact_results = [prospect for prospect in results
                                 if prospect.name_match(ostring, match_type="exact")]
            if exact_results:
                results = exact_results
        if len(results) > 1 and match_number != None:
            #select a particular match using the "keyword-N" markup.
            try:
                results = [results[match_number]]
            except IndexError:
                pass                        
        return results

    def _match_name_attribute(self, searchlist, ostring, dbref_only,
                             limit_types, match_type,
                             attribute_name=None):            
        """
        Helper function for list_search_object_namestr -
        does name/attribute matching through a list of objects.
        """
        if attribute_name:
            #search an arbitrary attribute name. 
            if limit_types:
                if match_type == "exact":
                    return [prospect for prospect in searchlist
                            if prospect.type in limit_types and 
                            ostring == getattr(prospect, attribute_name)]
                else:
                    return [prospect for prospect in searchlist
                            if prospect.type in limit_types and 
                            ostring in str(getattr(prospect, attribute_name))]
            else:
                if match_type == "exact":
                    return [prospect for prospect in searchlist
                            if ostring == str(getattr(prospect, attribute_name))]
                else:                    
                    return [prospect for prospect in searchlist
                            if ostring in str(getattr(prospect, attribute_name))]
        else:
            #search the default "name" attribute
            if limit_types:
                return [prospect for prospect in searchlist
                        if prospect.type in limit_types and
                        prospect.name_match(ostring, match_type=match_type)] 
            else:
                return [prospect for prospect in searchlist
                        if prospect.name_match(ostring, match_type=match_type)]

    def _parse_match_number(self, ostring):
        """
        Helper function for list_search_object_namestr -
        strips eventual N-keyword endings from a search criterion
        """
        if not '-' in ostring:
            return False, ostring
        try: 
            il = ostring.find('-')
            number = int(ostring[:il])-1
            return number, ostring[il+1:]
        except ValueError:
            #not a number; this is not an identifier.
            return None, ostring
        except IndexError:
            return None, ostring 
    

    def player_alias_search(self, searcher, ostring):
        """
        Search players by alias. Returns a list of objects whose "ALIAS" 
        attribute exactly (not case-sensitive) matches ostring.
        
        searcher: (Object) The object doing the searching.
        ostring:  (string) The alias string to search for.
        """
        if ostring.lower().strip() == "me":
            return searcher
        
        Attribute = ContentType.objects.get(app_label="objects", 
                                            model="attribute").model_class()
        results = Attribute.objects.select_related().filter(attr_name__exact="ALIAS").filter(attr_value__iexact=ostring)
        return [prospect.get_object() for prospect in results if prospect.get_object().is_player()]
    
    def player_name_search(self, search_string):
        """
        Combines an alias and global search for a player's name. If there are
        no alias matches, do a global search limiting by type PLAYER.
        
        search_string:  (string) The name string to search for.
        """
        # Handle the case where someone might have started the search_string
        # with a *
        if search_string.startswith('*') is True:
            search_string = search_string[1:]
        # Use Q objects to build complex OR query to look at either
        # the player name or ALIAS attribute
        player_filter = Q(name__iexact=search_string)
        alias_filter = Q(attribute__attr_name__exact="ALIAS") & \
                Q(attribute__attr_value__iexact=search_string)
        player_matches = self.filter(
                player_filter | alias_filter).filter(
                        type=defines_global.OTYPE_PLAYER).distinct()
        try:
            return player_matches[0]
        except IndexError:
            return None


    def local_and_global_search(self, searcher, ostring, search_contents=True, 
                                search_location=True, dbref_only=False, 
                                limit_types=False, attribute_name=None):
        """
        Searches an object's location then globally for a dbref or name match.
        
        searcher: (Object) The object performing the search.
        ostring: (string) The string to compare names against.
        search_contents: (bool) While true, check the contents of the searcher.
        search_location: (bool) While true, check the searcher's surroundings.
        dbref_only: (bool) Only compare dbrefs.
        limit_types: (list of int) A list of Object type numbers to filter by.
        attribute_name: (string) Which attribute to search in each object.
                                 If None, the default 'name' attribute is used.        
        """
        search_query = str(ostring).strip()

        # This is a global dbref search. Not applicable if we're only searching
        # searcher's contents/locations, dbref comparisons for location/contents
        # searches are handled by list_search_object_namestr() below.
        if util_object.is_dbref(ostring):
            dbref_match = self.dbref_search(search_query, limit_types)
            if dbref_match is not None:
                return [dbref_match]

        # If the search string is one of the following, return immediately with
        # the appropriate result.
        
        if searcher.location.dbref_match(ostring) or ostring == 'here':
            return [searcher.location]
        elif ostring == 'me' and searcher:
            return [searcher]

        if search_query and search_query[0] == "*":
            # Player search- gotta search by name or alias
            search_target = search_query[1:]
            player_match = self.player_name_search(search_target)
            if player_match is not None:
                return [player_match]
            
        # Handle our location/contents searches. list_search_object_namestr() does
        # name and dbref comparisons against search_query.
        local_objs = []
        if search_contents: 
            local_objs.extend(searcher.contents)
        if search_location:
            local_objs.extend(searcher.location.contents)
        return self.list_search_object_namestr(local_objs, search_query,
                                               limit_types=limit_types,
                                               attribute_name=attribute_name)        

