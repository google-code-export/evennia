"""
This module is responsible for managing scripts and their connection to the
Object class model. It is important to keep this as independent from the
codebase as possible in order to allow for drop-in replacements. All
interaction with actual script methods should happen via calls to Objects.
"""
import os
from traceback import format_exc
from twisted.python.rebuild import rebuild
from django.conf import settings
from src import logger

# A dictionary with keys equivalent to the script's name and values that
# contain references to the associated module for each key.
CACHED_SCRIPTS = {}

def rebuild_cache():
    """
    Rebuild all cached scripts.
    """
    cache_dict = CACHED_SCRIPTS.items()
    for key, val in cache_dict:
        rebuild(val)

def scriptlink(scriptname):
    """
    Each Object will refer to this function when trying to execute a function
    contained within a scripted module. For the sake of ease of management,
    modules are cached and compiled as they are requested and stored in
    the CACHED_SCRIPTS dictionary.
    
    Returns a reference to an instance of the script's class as per it's
    class_factory() method.
    
    scriptname: (str) Name of the module to load (minus 'scripts').
    """
    assert(not scriptname.startswith("game."))
    # The module is already cached, just return it rather than re-load.
    retval = CACHED_SCRIPTS.get(scriptname, False)
    if retval:
        return retval

    """
    NOTE: Only go past here when the script isn't already cached.
    """
    
    # Split the script name up by periods to give us the directory we need
    # to change to. I really wish we didn't have to do this, but there's some
    # strange issue with __import__ and more than two directories worth of
    # nesting.

    full_script = "%s.%s" % (settings.SCRIPT_IMPORT_PATH, scriptname)
    #full_script = scriptname
    script_name = str(full_script.split('.')[-1])
    script_module = ".".join(full_script.split('.')[0:-1])
    try:
        # Change the working directory to the location of the script and import.
        logger.log_infomsg("SCRIPT: Caching and importing %s." % (scriptname))
        modreference = __import__(script_module, fromlist=[script_name])
        mdl = getattr(modreference, script_name)
        # Store the module reference for later fast retrieval.
        CACHED_SCRIPTS[scriptname] = mdl
    except ImportError:
        print 'Error importing %s: %s' % (scriptname, format_exc())
        logger.log_infomsg('Error importing %s: %s' % (scriptname, format_exc()))
        os.chdir(settings.BASE_PATH)
        return
    except OSError:
        print 'Invalid module path: %s' % (format_exc())
        logger.log_infomsg('Invalid module path: %s' % (format_exc()))
        os.chdir(settings.BASE_PATH)
        return

    # The new script module has been cached, return the reference.
    return mdl
