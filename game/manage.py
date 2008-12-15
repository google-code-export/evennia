#!/usr/bin/env python
import sys
import os
from django.core.management import execute_manager

# Tack on the root evennia directory to the python path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
If settings.py doesn't already exist, create it and populate it with some
basic stuff.
"""
if not os.path.exists('settings.py'):
    print "Can't find a settings.py file, creating one for you."
    f = open('settings.py', 'w')
    f.write('"""\rMaster server configuration file. You may override any of the values in the\rsrc/config_defaults.py here. Copy-paste the variables here, and make changes to\rthis file rather than editing config_defaults.py directly.\r"""\r')
    f.write('from src.config_defaults import *')

try:
    from game import settings
except ImportError:
     import sys
     sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
     sys.exit(1)

if __name__ == "__main__":
     execute_manager(settings)
