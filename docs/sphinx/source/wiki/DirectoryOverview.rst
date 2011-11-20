Evennia directory overview
==========================

Evennia's main directory (``evennia``) is divided into five sub
directories - ``src/``, ``game/``, ``contrib/``, ``locale`` and
``doc/``. The first two are the most important ones. ``game/`` is the
place where you will create your own game, whereas ``src/`` is the home
of the Evennia server itself. Your code should usually just import
resources from ``src/`` and not change anything in there.

All directories contain files ending in ``.py``. These are Python
*modules* and are the basic units of Python code. The roots of
directories also have empty files named ``__init__.py``. These are
required by Python so as to be able to find and import modules in other
directories. When you have run Evennia at least once you will find that
there will also be ``.pyc`` files appearing, these are pre-compiled
binary versions of the ``.py`` files to speed up execution.

The ``docs/`` directory
-----------------------

This contains Evennia's offline documentation. The main source of
up-to-date documentation is the online wiki however.

Read ``sphinx/README`` for instructions on building the ReST
documentation, based on a current snapshot of the wiki. This can be
browsed offline or made into a PDF for printing etc.

You can create the Evennia *autodocs* by following the instructions in
``doxygen/README``. This will make use of the source code itself to
create a nice browsable web-index of all the sources and comments. In
the same way you could in theory also create nice ``LaTeX``-formatted
PDFs of the Evennia source (all 400+ pages of it ...).

The ``locale`` directory
------------------------

This contains internationalization strings for translating the Evennia
core server to different languages. See
`Internationalization <Internationalization.html>`_ for more
information.

The ``contrib/`` ("contributions") directory
--------------------------------------------

This directory contains various stand-alone code snippets that are
potentially useful but which are deemed too game-specific to be a
regular part of the server. Modules in ``contrib/`` are not used unless
you explicitly import and use them. The contrib folder also contains the
`Tutorial World <TutorialWorldIntroduction.html>`_ game example. See
``contrib/README`` for more information.

The ``game/`` directory
-----------------------

``game/`` contains everything related to a particular game world. If you
ever wanted to start over with a new game implementation you could
replace the ``game`` directory and start from scratch. The root of this
directory contains the all-important ``manage.py`` and ``evennia.py``
which you need in order to `get started <GettingStarted.html>`_ and run
the server.

::

    game/
      evennia.py
      manage.py  gamesrc/
        commands/ 
          basecommand.py
          basecmdset.py
          examples/
            cmdset_red_button.py
        scripts/
          basescript.py
          examples/
            red_button_sripts.py
        objects/
          baseobjects.py
          examples/
            red_button.py
        world/     
          examples/
            batch_cmds.ev
            batch_code.py

``game/gamesrc/``
~~~~~~~~~~~~~~~~~

``game/gamesrc`` is where you will be spending most of your time. All
the things going into your own dream game should be put here, by adding
Python modules. Throughout the ``gamesrc`` directories are ``examples``
folders that all define different aspects of an example
`object <Objects.html>`_ called *Red Button*. This is a button that
blinks and does interesting stuff when pressed. It's designed to combine
many different systems and to show off several advanced features of
Evennia.

``gamesrc/commands/``
^^^^^^^^^^^^^^^^^^^^^

``gamesrc/commands/`` contains modules for defining
`Commands <Commands.html>`_. It contains a file ``basecommand.py`` which
defines the root object from which all your own command classes will
inherit.The file ``basecmdset.py`` is where you'll inherit your `Command
Set <Commands.html>`_ classes from. ``commands/examples`` contains the
main interactive commands and cmdsets of the *Red Button*.

``gamesrc/scripts/``
^^^^^^^^^^^^^^^^^^^^

``gamesrc/scripts/`` holds everything related to
`Scripts <Scripts.html>`_. It has a file ``basescript.py`` that hold the
parent for all scripts and which you should inherit from.
``scripts/examples`` holds the *Red Button*'s scripts.

``gamesrc/objects/``
^^^^^^^^^^^^^^^^^^^^

``gamesrc/objects/`` should contain the definitions for all your
`Objects <Objects.html>`_. ``baseobjects.py`` contains the parent
classes for the normal *Object* as well as its three basic subclasses
*Character*, *Room* and *Exit*. Your own objects will inherit from the
classes in this file. ``objects/examples`` define the example *Red
Button* object itself.

``gamesrc/world/``
^^^^^^^^^^^^^^^^^^

``gamesrc/world/``, finally, contains all the rest that make up your
world. This is where you would put your own custom economic system,
combat mechanic, emote-parser or what have you; organized in whatever
way you like. Just remember that if you create new folders under
``world``, they must contain an empty file ``__init__.py``, or Python
will not know how to import modules from them. The ``world`` folder is
also where Evennia's `batch processors <BatchProcessors.html>`_ by
default look for their input files. These allow you to build your world
offline using your favourite text editor rather than have to do it
online over a command line. The `Batch-Command
processor <BatchCommandProcessor.html>`_ expects files ending with
``.ev``, whereas the more advanced `Batch-Code
processor <BatchCodeProcessor.html>`_ takes ``.py`` with some special
formatting.

``world/examples/`` contains one batch file for each processor. Each
creates a *Red Button* object in *Limbo* using their respective special
syntax.

The ``src/`` directory
----------------------

``src/`` contains the main running code of the Evennia server. You will
often need to import modules from here to access the functionality of
Evennia. You should generally not modify anything in this folder
directly since it might be changed when we release updates. If you find
bugs or features missing, file a bug report or send us a message.

::

    src/
      settings_defaults.py  commands/
      comms/
      help/
      objects/
      locks/
      players/
      scripts/
      server/
      typeclasses/
      utils/
      web/

Most of the folders in ``src/`` are technically "Django apps",
identified by containing a file ``models.py`` and usually
``managers.py``. A Django *model* is a template for how to save data to
the database. In order to offer full-persistence, Evennia uses models
extensively. The *manager* is used to conveniently access objects in the
database. Even if you don't know Django, you can easily use the methods
in the respective managers by accessing them through the *objects*
property of each corresponding model. Example: in
``src/objects/models.py`` there is a model named ``ObjectDB``. In the
same folder, there is also a manager found in
``src/objects/managers.py``. To access one of the manager's methods,
such as ``object_search()``, you would need to do
``ObjectDB.objects.object_search(...)``.

All Django app folders also have a file ``admin.py``. This tells
Django's web features to automatically build a nice web-based admin
interface to the database. This means that you can add/edit/delete
objects through your browser.

In the root of the ``src`` directory lies the ``settings_defaults.py``
file. This is the main configuration file of Evennia. You should
copy&paste entries from this file to your ``game/settings.py`` file if
you want to customize any setting.

``src/commands/``
~~~~~~~~~~~~~~~~~

This directory contains the `command system <Commands.html>`_ of
Evennia. It defines basic command function, parsing and command-set
handling.

``commands/default/`` holds a multitude of modules that together form
Evennia's default ('`MUX-like <UsingMUXAsAStandard.html>`_') command
set. The files ``game/gamesrc/basecommand.py`` and
``game/gamesrc/basecmdset.py`` both link to their respective parents
here. If you want to edit a default command, copy&paste the respective
module to ``game/gamesrc/commands/`` and edit the default cmdset to
point to your copy.

``src/comms/``
~~~~~~~~~~~~~~

``src/comms/`` defines all aspects of OOC
`communication <Communications.html>`_, notably *channels* and the basic
operations for storing listeners to channels.

``src/help/``
~~~~~~~~~~~~~

This defines the `help system <HelpSystem.html>`_ of Evennia, the
command auto-help as well as the database-centric storage of in-game
help files.

``src/objects/``
~~~~~~~~~~~~~~~~

``src/objects/`` defines how the in-game `objects <Objects.html>`_ are
stored, found and handled in the database.

``src/locks/``
~~~~~~~~~~~~~~

This directory defines the powerful `lock system <Locks.html>`_ of
Evennia, a system that serves to restrict access to objects. The default
lock functions are found here.

``src/players/``
~~~~~~~~~~~~~~~~

The `Player <Players.html>`_ is the OOC-represention of the person
behind the game character. This directory defines the database handling
and methods acting on the Player object.

``src/scripts/``
~~~~~~~~~~~~~~~~

``src/scripts/`` defines all aspects of `Scripts <Scripts.html>`_ - how
they are activated, repeated and stored in-memory or in-database. The
main engine scripts (e.g. for keeping track of game-time, uptime and
connection timeouts) are also defined here.

``src/server/``
~~~~~~~~~~~~~~~

This directory is the heart of Evennia. It holds the server process
itself (started from ``game/evennia.py``) and all `sessions and
protocols <SessionProtocols.html>`_ that allow users to connect to it.
It also knows how to store dynamic server info in the database.

``src/typeclasses/``
~~~~~~~~~~~~~~~~~~~~

``src/typeclasses/`` defines the `Typeclass system <Typeclasses.html>`_
that permeates Evennia, allowing coders to interact with normal Python
classes instead of caring about the underlying database implementation.
This directory is rarely accessed directly, rather both Objects, Scripts
and Players all inherit from its core classes. Also
`attributes <Attributes.html>`_ are defined here, being an vital part of
the typeclass system.

``src/utils/``
~~~~~~~~~~~~~~

``src/utils/`` is a useful directory that contains helper functions for
the MUD coder. The ``utils/create.py`` module for example gathers
methods for creating all sorts of database models (objects, scripts,
help entries etc) without having to go into the respective database
managers directly. ``utils/search.py`` search a similar function for
searching the database. This directory also contains many helper modules
for parsing and converting data in various ways.

``src/web/``
~~~~~~~~~~~~

This directory contains features related to running Evennia's `web site
and ajax web client <WebFeatures.html>`_. It will be customizable by the
user, but it's currently not established how to conveniently hook into
this from game/, so for the moment the suggested way is to make a copy
of this directory in ``game/gamesrc``, re-link the right settings in
your settings file and edit things from there.

Assorted notes
==============

Whereas ``game/gamesrc/`` contains a set of directories already, you
might find that another structure suits your development better. For
example, it could sometimes easier to put all the commands and scripts a
certain object needs in the same module as that object, rather than
slavishly split them out into their respective directories and import.
Don't be shy to define your own directory structure as needed. A basic
rule of thumb should nevertheless be to avoid code-duplication. So if a
certain script or command could be useful for other objects, break it
out into its own module and import from it.