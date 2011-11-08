Attributes
==========

When performing actions in Evennia it is often important that you store
data for later. If you write a menu system, you have to keep track of
the current location in the menu tree so that the player can give
correct subsequent commands. If you are writing a combat system, you
might have a combattant's next roll get easier dependent on if their
opponent failed. Your characters will probably need to store
roleplaying-attributes like strength and agility. And so on.

`Typeclassed <Typeclasses.html>`_ game entities
(`Players <Players.html>`_, `Objects <Objects.html>`_ and
`Scripts <Scripts.html>`_) always have *Attributes* associated with
them. Attributes are used to store any type of data 'on' such entities.
This is different from storing data in properties already defined on
entities (such as ``key`` or ``location``) - these have very specific
names and require very specific types of data (for example you couldn't
assign a python *list* to the ``key`` property no matter how hard you
tried). ``Attributes`` come into play when you want to assign arbitrary
data to arbitrary names.

Saving and Retrieving data
--------------------------

To save persistent data on a Typeclassed object you normally use the
``db`` operator. Let's try to save some data to a *Rose* (an
`Object <Objects.html>`_):

::

    # saving 
    rose.db.has_thorns = True # getting it back
    is_ouch = rose.db.has_thorns

This looks like any normal Python assignment, but that ``db`` makes sure
that an *Attribute* is created behind the scenes and is stored in the
database. Your rose will continue to have thorns throughout the life of
the server now, until you deliberately remove them.

To be sure to save **non-persistently**, i.e. to make sure NOT create a
database entry, you use ``ndb`` (!NonDataBase). It works in the same
way:

::

    # saving 
    rose.ndb.has_thorns = True # getting it back
    is_ouch = rose.ndb.has_thorns

Strictly speaking, ``ndb`` has nothing to do with ``Attributes``,
despite how similar they look. No ``Attribute`` object is created behind
the scenes when using ``ndb``. In fact the database is not invoked at
all since we are not interested in persistence.

You can also ``del`` properties on ``db`` and ``ndb`` as normal. This
will for example delete an ``Attribute``:

::

    del rose.db.has_thorns

Fast assignment
---------------

For quick testing you can most often skip the ``db`` operator and assign
Attributes like you would any normal Python property:

::

    # saving
    rose.has_thorns = True# getting it back
    is_ouch = rose.has_thorns

This looks like any normal Python assignment, but calls ``db`` behind
the scenes for you.

Assigning attributes this way is intuitive and makes for slightly less
to write. There is a drawback to using this short-form though: Database
objects and typeclasses *already* have a number of Python methods and
properties defined on themselves. If you use one of those already-used
names with this short form you will not be setting a new Attribute but
will infact be editing an existing engine property.

For example, the property ``self.location`` on yourself is tied directly
to the ``db_location`` database field and will not accept anything but
an ``ObjectDB`` object or it will raise a traceback. ``self.delete`` is
a method handling the deletion of objects, and so on. The reason these
are available is of course that you may *want* to overload these
functions with your own implementations - this is one of the main powers
of Evennia. But if you blindly do e.g. ``self.msg = "Hello"`` you will
happily be overloading the core ``msg()`` method and be in a world of
pain.

Using ``db`` will always work like you expect. ``self.db.msg = 'Hello'``
will create a new Attribute ``msg`` without affecting the core method
named ``msg()`` at all. So in principle, whereas you can use the
short-form for simple testing, it's best to use ``db`` when you want
Attributes and skip it only when you explicitly want to edit/overload
something in the base classes.

Persistent vs non-persistent
----------------------------

So *persistent* data means that your data will survive a server reboot,
whereas with *non-persistent* data it will not ...

... So why would you ever want to use non-persistent data? The answer
is, you don't have to. Most of the time you really want to save as much
as you possibly can. Non-persistent data is potentially useful in a few
situations though.

-  You are worried about database performance. Maybe you are
   reading/storing data many times a second (for whatever reason) or you
   have many players doing things at the same time. Hitting the database
   over and over might not be ideal in that case. Non-persistent data
   simply writes to memory, it doesn't hit the database at all. It
   should be said that with the speed and quality of hardware these
   days, this point is less likely to be of any big concern except for
   the most extreme of situations. The default database even runs in RAM
   if possible, alleviating the need to write to disk.
-  You *want* to loose your state when logging off. Maybe you are
   testing a buggy `Script <Scripts.html>`_ that does potentially
   harmful stuff to your character object. With non-persistent storage
   you can be sure that whatever the script messes up, it's nothing a
   server reboot can't clear up.
-  You want to implement a fully or partly *non-persistent world*. Who
   are we to argue with your grand vision!

What types of data can I save?
------------------------------

If you store a single object (that is, not a iterable list of objects),
you can practically store any Python object that can be
`pickled <http://docs.python.org/library/pickle.html>`_. Evennia uses
the ``pickle`` module to serialize data into the database.

There is one notable type of object that cannot be pickled - and that is
a Django database object. These will instead be stored as a wrapper
object containing the ID and its database model. It will be read back to
a new instantiated `typeclass <Typeclasses.html>`_ when the Attribute is
accessed. Since erroneously trying to save database objects in an
Attribute will lead to errors, Evennia will try to detect database
objects by analyzing the data being stored. This means that Evennia must
recursively traverse all iterables to make sure all database objects in
them are stored safely. So for efficiency, it can be a good idea is to
avoid deeply nested lists with objects if you can.

To store several objects, you may only use python *lists*,
*dictionaries* or *tuples* to store them. If you try to save any other
form of iterable (like a ``set`` or a home-made class), the Attribute
will convert, store and retrieve it as a list instead. Since you can
nest dictionaries, lists and tuples together in any combination, this is
usually not a limitation you need to worry about.

*Note that you could fool the safety check if you for example created
custom, non-iterable classes and stored database objects in them. So to
make this clear - saving such an object is **not supported** and will
probably make your game unstable. Store your database objects using
lists, dictionaries or a combination of the two and you should be fine.*

Examples of valid attribute data:

::

    # a single value
    obj.db.test1 = 23
    obj.db.test1 = False 
    # a database object (will be stored as dbref)
    obj.db.test2 = myobj
    # a list of objects
    obj.db.test3 = [obj1, 45, obj2, 67]
    # a dictionary
    obj.db.test4 = 'str':34, 'dex':56, 'agi':22, 'int':77
    # a mixed dictionary/list
    obj.db.test5 = 'members': [obj1,obj2,obj3], 'enemies':[obj4,obj5]
    # a tuple with a list in it
    obj.db.test6 = (1,3,4,8, ["test", "test2"], 9)
    # a set will still be stored and returned as a list [1,2,3,4,5]!
    obj.db.test7 = set([1,2,3,4,5])

Example of non-supported save:

::

    # this will fool the dbobj-check since myobj (a database object) is "hidden"
    # inside a custom object. This is unsupported and will lead to unexpected
    # results! 
    class BadStorage(object):
        pass
    bad = BadStorage()
    bad.dbobj = myobj
    obj.db.test8 = bad # this will likely lead to a traceback

Storing nested data directly on the variable
--------------------------------------------

Evennia needs to do a lot of work behind the scenes in order to save and
retrieve data from the database. Most of the time, things work just like
normal Python, but there is one further exception except the one about
storing database objects above. It is related to updating already
existing attributes in-place. Normally this works just as it should. For
example, you can do

::

    # saving data
    obj.db.mydict["key"] = "test1"
    obj.db.mylist[34] = "test2"
    obj.db.mylist.append("test3")
    # retrieving data
    obj.db.mydict["key"] # returns "test1"
    obj.db.mylist[34] # returns "test2
    obj.db.mylist[-1] # returns "test3"

and it will work fine, thanks to a lot of magic happening behind the
scenes. What will *not* work however is editing *nested*
lists/dictionaries in-place. This is due to the way Python referencing
works. Consider the following:

::

    obj.db.mydict = 1:2:3

This is a perfectly valid nested dictionary and Evennia will store it
just fine.

::

    obj.db.mydict[1][2] # correctly returns 3

However:

::

    obj.db.mydict[1][2] = "test" # fails!

will not work - trying to edit the nested structure will fail silently
and nothing will have changed. No, this is not consistent with normal
Python operation, it's where the database magic fails. All is not lost
however. In order to change a nested structure, you simply need to use a
temporary variable:

::

    # retrieve old db data into temporary variable
    mydict = obj.db.mydict
    # update temporary variable
    mydict[1][2] = "test"
    # save back to database
    obj.db.mydict = mydict
    # test
    obj.db.mydict[1][2] # now correctly returns "test"

mydict was updated and recreated in the database.

Notes
-----

There are several other ways to assign Attributes to be found on the
typeclassed objects, all being more 'low-level' underpinnings to
``db``/``ndb``. Read their descriptions in the respective modules.
