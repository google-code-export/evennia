"""
Master configuration file for Evennia.

NOTE: NO MODIFICATIONS SHOULD BE MADE TO THIS FILE! All settings changes should
be done by copy-pasting the variable and its value to your game directory's
settings.py file.
"""
import os

# A list of ports to listen on. Can be one or many.
GAMEPORTS = [4000]

# While DEBUG is False, show a regular server error page on the web stuff,
# email the traceback to the people in the ADMINS tuple below. By default (True),
# show a detailed traceback for the web browser to display.
DEBUG = True

# While true, show "pretty" error messages for template syntax errors.
TEMPLATE_DEBUG = DEBUG

# Emails are sent to these people if the above DEBUG value is False. If you'd
# rather nobody recieve emails, leave this commented out or empty.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# These guys get broken link notifications when SEND_BROKEN_LINK_EMAILS is True.
MANAGERS = ADMINS

# The path that contains this settings.py file (no trailing slash).
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the game directory (containing the database file if using sqlite).
GAME_DIR = os.path.join(BASE_PATH, 'game')

# Logging paths
LOG_DIR = os.path.join(GAME_DIR, 'logs')
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, 'evennia.log')

# Path to the src directory containing the bulk of the codebase's code.
SRC_DIR = os.path.join(BASE_PATH, 'src')

# Absolute path to the directory that holds media (no trailing slash).
# Example: "/home/media/media.lawrence.com"
MEDIA_ROOT = os.path.join(GAME_DIR, 'web', 'media')

# Import style path to the script parent module. Must be in the import path.
SCRIPT_IMPORT_PATH = 'game.gamesrc.parents'
# Default parent associated with non-player objects. This starts from where
# the SCRIPT_IMPORT_PATH left off.
SCRIPT_DEFAULT_OBJECT = 'base.basicobject'
# Default parent associated with player objects. This starts from where
# the SCRIPT_IMPORT_PATH left off.
SCRIPT_DEFAULT_PLAYER = 'base.basicplayer'

# 'postgresql', 'mysql', 'mysql_old', 'sqlite3' or 'ado_mssql'.
DATABASE_ENGINE = 'sqlite3'
# Database name, or path to DB file if using sqlite3.
DATABASE_NAME = os.path.join(GAME_DIR, 'evennia.db3')
# Unused for sqlite3
DATABASE_USER = ''
# Unused for sqlite3
DATABASE_PASSWORD = ''
# Empty string defaults to localhost. Not used with sqlite3.
DATABASE_HOST = ''
# Empty string defaults to localhost. Not used with sqlite3.
DATABASE_PORT = ''

"""
IMC Configuration

This is static and important enough to put in the server-side settings file.
Copy and paste this section to your game/settings.py file and change the
values to fit your needs.

Evennia's IMC2 client was developed against MudByte's network. You may
register and join it by going to:
http://www.mudbytes.net/imc2-intermud-join-network

Choose "Other unsupported IMC2 version" and enter your information there.
You'll want to change the values below to reflect what you entered.
"""
# Make sure this is True in your settings.py.
IMC2_ENABLED = False
# The hostname/ip address of your IMC2 server of choice.
IMC2_SERVER_ADDRESS = None
# The port to connect to on your IMC2 server.
IMC2_SERVER_PORT = None
# This is your game's IMC2 name.
IMC2_MUDNAME = None
# Your IMC2 client-side password. Used to authenticate with your network.
IMC2_CLIENT_PW = None
# Your IMC2 server-side password. Used to verify your network's identity.
IMC2_SERVER_PW = None
# This isn't something you should generally change.
IMC2_PROTOCOL_VERSION = '2'

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.0/interactive/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'en-us'

# It's safe to dis-regard this, as it's a Django feature we only half use as a
# dependency, not actually what it's primarily meant for.
SITE_ID = 1

# The age for sessions.
# Default: 1209600 (2 weeks, in seconds)
SESSION_COOKIE_AGE = 1209600

# Session cookie domain
# Default: None
# SESSION_COOKIE_DOMAIN = None

# The name of the cookie to use for sessions.
# Default: 'sessionid'
SESSION_COOKIE_NAME = 'sessionid'

# Should the session expire when the browser closes?
# Default: False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you'd like to serve media files via Django (strongly not recommended!),
# set SERVE_MEDIA to True. This is appropriate on a developing site, or if 
# you're running Django's built-in test server. Normally you want a webserver 
# that is optimized for serving static content to handle media files (apache, 
# lighttpd).
SERVE_MEDIA = True

# The master urlconf file that contains all of the sub-branches to the
# applications.
ROOT_URLCONF = 'game.web.urls'

# Where users are redirected after logging in via contribu.auth.login.
LOGIN_REDIRECT_URL = '/'

# Where to redirect users when using the @login_required decorator.
LOGIN_URL = '/accounts/login'

# Where to redirect users who wish to logout.
LOGOUT_URL = '/accounts/login'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/amedia/'

# Make this unique, and don't share it with anybody.
# NOTE: If you change this after creating any accounts, your users won't be
# able to login, as the SECRET_KEY is used to salt passwords.
SECRET_KEY = 'changeme!(*#&*($&*(#*(&SDFKJJKLS*(@#KJAS'

# The name of the currently selected web template. This corresponds to the
# directory names shown in the webtemplates directory.
ACTIVE_TEMPLATE = 'prosimii'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(GAME_DIR, "web", "html", ACTIVE_TEMPLATE),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

# MiddleWare are semi-transparent extensions to Django's functionality.
# see http://www.djangoproject.com/documentation/middleware/ for a more detailed
# explanation.
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

# Context processors define context variables, generally for the template
# system to use.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'game.web.apps.website.webcontext.general_context',
)

# Global and Evennia-specific apps. This ties everything together so we can
# refer to app models and perform DB syncs.
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.flatpages',
    'src.config',
    'src.objects',
    'src.helpsys',
    'src.genperms',
    'game.web.apps.news',
    'game.web.apps.website',
)

"""
A tuple of strings representing all of the Evennia (IE: non-custom) commnad
modules that are used at the login screen in the UNLOGGED command table. Do
not modify this directly, add your custom command modules to
CUSTOM_UNLOGGED_COMMAND_MODULES.
"""
UNLOGGED_COMMAND_MODULES = (
    'src.commands.unloggedin',
)

"""
Add your custom command modules under game/gamesrc/commands and to this list.
These will be loaded after the Evennia codebase modules, meaning that any
duplicate command names will be overridden by your version.
"""
CUSTOM_UNLOGGED_COMMAND_MODULES = ()

"""
A tuple of strings representing all of the Evennia (IE: non-custom)
command modules. Do not modify this directly, add your custom command
modules to CUSTOM_COMMAND_MODULES.
"""
COMMAND_MODULES = (
    'src.commands.comsys',
    'src.commands.general',
    'src.commands.info',
    'src.commands.objmanip',
    'src.commands.paging',
    'src.commands.parents',
    'src.commands.privileged',
    'src.commands.search',
    'src.commands.imc2',
)

"""
Add your custom command modules under game/gamesrc/commands and to this list.
These will be loaded after the Evennia codebase modules, meaning that any
duplicate command names will be overridden by your version.
"""
CUSTOM_COMMAND_MODULES = ()

# If django_extensions is present, import it and install it. Otherwise fail
# silently.
try:
    import django_extensions
    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)
except ImportError:
    pass