Getting Started
===============

This will help you download, install and start Evennia for the first
time.

Quick start
-----------

For you who are extremely impatient, here's the gist of getting a
vanilla Evennia install running.

#. *Get the pre-requisites (mainly Python, Django, Twisted and
   Mercurial)*.
#. *Start a command terminal/dos prompt and change directory to where
   you want to have your 'evennia' folder appear*.
#. ``hg clone https://code.google.com/p/evennia/ evennia``
#. *Change directory to evennia/game*.
#. ``python manage.py``
#. ``python manage.py syncdb``
#. ``python evennia.py -i start``

Evennia should now be running and you can connect to it by pointing a
web browser to ``http://localhost:8000`` or a MUD telnet client to
``localhost:4000``.

Read on for more detailed instructions and configurations.

Pre-Requesites
--------------

As far as operating systems go, any system with Python support should
work.

-  Linux/Unix
-  Windows (2000, XP, Vista, Win7)
-  Mac OSX (>=10.5 recommended)

If you run into problems, or have success running Evennia on another
platform, please let us know.

You'll need the following packages and minimum versions in order to run
Evennia:

**Python** (http://www.python.org)

-  Version 2.5+ strongly recommended, although 2.3 or 2.4 **may** work.
   Obs- Python3.x is not supported yet.
-  The default database system SQLite3 only comes as part of Python2.5
   and later.
-  Windows users are recommended to use ActivePython
   (http://www.activestate.com/activepython/downloads)

**Twisted** (http://twistedmatrix.com)

Version 10.0+

Twisted also requires:

-  !ZopeInterface 3.0+ (http://www.zope.org/Products/ZopeInterface)
-  For Windows only: pywin32 (http://sourceforge.net/projects/pywin32)

**Django** (http://www.djangoproject.com)

-  Version 1.2.1+ or latest subversion trunk highly recommended.
-  PIL library (http://www.pythonware.com/products/pil)

To download/update Evennia:

**Mercurial** (http://mercurial.selenic.com/)

-  This is needed to download and update Evennia itself.

Optional packages:

**South** (http://south.aeracode.org/)

-  Version 0.7+
-  Optional. Used for database migrations.

**Apache2** (http://httpd.apache.org)

-  Optional. Most likely you'll not need to bother with this since
   Evennia runs its own threaded web server based on Twisted. Other
   equivalent web servers with a Python interpreter module can also be
   used.

*Note: You don't need to make anything visible to the 'net in order to
run and test out Evennia. Apart from downloading/updating Evennia itself
you don't even need to have an internet connection. Of course you'll
probably want that as your game matures, but until then it works nicely
to develop and play around completely in the sanctity and isolation of
your local machine.*

Installing pre-requisites
~~~~~~~~~~~~~~~~~~~~~~~~~

**Linux** package managers should usually handle all this for you.
Python itself is definitely available through all distributions. On
Debian-derived systems you can do something like this (as root) to get
all you need:

::

    apt-get install python python-django python-twisted mercurial

If some or all dependencies are not readily available (for example,
running some flavors of !RedHat/CentOS or an older Debian version) you
can still retrieve them easily by installing and using Python's
`easyinstall <http://packages.python.org/distribute/easy%3Ci%3Einstall.html>`_
or the alternative
`pip <http://www.pip-installer.org/en/latest/index.html>`_:

::

    easy_install django twisted pil mercurial

::

    pip install django twisted pil mercurial

**Windows** users may choose to install
`ActivePython <http://www.activestate.com/activepython/downloads>`_
instead of the usual Python. If ActivePython is installed, you can use
`pypm <http://docs.activestate.com/activepython/2.6/pypm.html>`_ in the
same manner as ``easy_install``/``pip`` above. This *greatly* simplifies
getting started on Windows:

::

    pypm install Django Twisted PIL Mercurial

Another simple alternative (for all platforms) is to set up a *virtual
Python environment* and install to that - in that case you can even
experiment with different library versions without affecting your main
system configuration. This is covered
`here <GettingStarted#Optional:%3Ci%3EA%3C/i%3Eseparate%3Ci%3Einstallation%3C/i%3Eenvironment%3Ci%3Ewith%3C/i%3Evirtualenv.html>`_.

Windows users not using ActivePython or virtual environments will have
to manually download and install the packages in turn - most have normal
Windows installers, but in some cases you'll need to know how to use the
Windows command prompt to execute some python install scripts.

Step 1: Obtaining the Server
----------------------------

To download Evennia you need the Mercurial client to grab a copy of the
source.

For command-line Mercurial client users, something like this will do the
trick (first place yourself in a directory where you want a new folder
``evennia`` to be created):

::

    hg clone https://code.google.com/p/evennia/ evennia

(``hg`` is the chemical abbreviation of mercury, hence the use of ``hg``
for ``mercurial``)

In the future, you just do

::

    hg pull

from your ``evennia/`` directory to obtain the latest updates.

If you use a graphical Mercurial client, use the equivalent buttons to
perform the above operations.

Step 2: Setting up the Server
-----------------------------

From within the Evennia ``game`` directory (``evennia/game/``, if you
followed the Subversion instructions above) type the following to
trigger the automatic creation of an empty ``settings.py`` file.

::

    python manage.py

Your new ``settings.py`` file will just be an empty template initially.
In ``evennia/src/settings_default.py`` you will find the settings that
may be copied/pasted into your ``settings.py`` to override the defaults.
This will be the case if you want to adjust paths or use something other
than the default SQLite3 database engine. You *never* want to modify
``settings_default.py`` directly - as the server is developed, this file
might be overwritten with new versions and features.

If you would like to use something other than the default SQLite setup
(which works "out of the box"), you'll need to copy the ``DATABASE_*``
variables from ``settings_defaults.py`` and paste them to
``settings.py``, making your modifications there.

*Note that the settings.py file is in fact a normal python module which
imports the default settings. This means that all variables have been
set to default values by the time you get to change things. So to
customize a particular variable you have to copy&paste it to your
settings file - and you have to do so also for variables that depend on
that variable (if any), or the dependent variables will remain at the
default values.*

Finally, enter the following command in a terminal or shell to create
the database file (in the case of SQLite) and populate the database with
the standard tables and values:

::

    python manage.py syncdb

You should be asked for a superuser username, email, and password. Make
**sure** you create a superuser here when asked, this becomes your login
name for the superuser account ``#1`` in game. After this you will see a
lot of spammy install messages. If all goes well, you're ready to
continue to the next step. If not, look at the error messages and
double-check your ``settings.py`` file.

If you installed ``South`` for database schema migrations, you will then
need to do this:

::

    python manage.py migrate

This will migrate the server to the latest version. If you don't use
``South``, migrations will not be used and your server will already be
at the latest version (but your existing database might have to be
manually edited to match future server changes).

Step 3: Starting and Stopping the Server
----------------------------------------

To start the server, make sure you're in the ``evennia/game`` directory
and execute ``evennia.py`` like this:

::

    python evennia.py -i start

This starts the server and portal. The ``-i`` flag means that the server
starts in *interactive mode*, as a foreground process. You will see
debug/log messages directly in the terminal window instead of logging
them to a file.

Running the server in interactive mode is very useful for development
and debugging but is not recommended for production environments. For
the latter you'll want to run it as a *daemon* by skipping the ``-i``
flag:

::

    python evennia.py start

This will start the server as a background process. Server messages will
be logged to a file you specify in your configuration file (default is a
file in ``game/logs``).

To stop Evennia, do:

::

    python evennia.py stop

See `Running
Evennia <https://code.google.com/p/evennia/wiki/StartStopReload.html>`_
for more advanced options on controlling Evennia's processes.

Step 4: Connecting to the server
--------------------------------

The Evennia server is now up and running. You should now be able to
login with any mud client or telnet client using the email address and
password you specified when syncing the database. If you are just
testing the server out on your local machine, the server name will most
likely be ``localhost`` whereas the port used by default is ``4000``.

If the defaults are not changed, Evennia will also start its own
Twisted-based web server on port 8000. Point your web browser to
``http://localhost:8000/``. The *admin interface* allows you to edit the
game database online and you can connect directly to the game by use of
the ajax web client.

Welcome to Evennia! Why not try `building
something <BuildingQuickstart.html>`_ next?

Optional: Database migrations with South
========================================

Evennia supports database migrations using
`South <http://south.aeracode.org/>`_, a Django database schema
migration tool. Installing South is optional, but if it is installed,
Evennia *will* use it automatically, meaning this section comes into
play. You can install South from
`http://south.aeracode.org/. <http://south.aeracode.org/.>`_ It is also
available through the normal package distributions, easy\_install, pip,
or pypm (see above notes).

After your first run of ``migrate.py syncdb`` and whenever you see a
commit or mailing list message telling you that "the Database Schema has
changed", simply do the following from within the ``evennia/game``
directory:

::

    python manage.py migrate

You should see migrations being applied, and should be left with an
updated DB schema afterwards.

Optional: A separate installation environment with virtualenv
=============================================================

Apart from installing the packages and versions as above, you can also
set up a very fast self-contained Evennia install using the
`virtualenv <http://pypi.python.org/pypi/virtualenv>`_ program.
Virtualenv sets aside a folder on your harddrive as a stand-alone Python
environment. It should work both on Linux and Windows. First, install
Python as normal, then get virtualenv and install it so you can run it
from the command line. This is an example for setting up Evennia in an
isolated new folder *mudenv*:

::

    python virtualenv mudenv --no-site-packages
    cd mudenv

Now we should be in our new directory *mudenv*. Next we activate the
virtual environment in here.

::

    # for Linux:
    source bin/activate
    # for Windows:
    <path_to_this_place>\bin\activate.bat

Next we get all the requirements with *pip*, which is included with
virtualenv:

::

    pip install django twisted pil mercurial

(The difference from the normal install described earlier is that these
installed packages are *only* localized to the virtual environment, they
do not affect the normal versions of programs you run in the rest of
your system. So you could for example experiment with bleeding-edge,
unstable libraries or go back to older versions without having to worry
about messing up other things. It's also very easy to uninstall the
whole thing in one go - just delete your ``mudenv`` folder.)

You can now refer to **Step 1** above and continue on from there to
install Evennia into *mudenv*. In the future, just go into the folder
and activate it to make this separate virtual environment available to
Evennia.
