Contributing to Evennia
=======================

Wanna help out? Great! Here's how.

Contributing with Documentation
-------------------------------

Evennia depends heavily on good documentation and we are always looking
for extra eyes and hands to improve it. Even small things such as fixing
typos is a great help. To edit the wiki yourself you need contributor
access. Otherwise, it goes a long way just pointing out wiki errors so
devs can fix them.

Contributing with Code through a clone repository
-------------------------------------------------

We always need more eyes and hands on the code. Even if you don't feel
confident with tackling any major bugs or features, just correcting
typos, adjusting formatting or simply using the thing helps us a lot in
improving things.

The most elegant way to contribute code to Evennia is to use Mercurial
to create an online *clone* of the Evennia repository and make your
changes to that. .

#. Go to the
   `Checkout <http://code.google.com/p/evennia/source/checkout>`_ page.
#. If you are logged in, you should see a button named *Create a Clone*.
   Click that.
#. You are asked to fill in a few fields. Name your clone repository
   something useful, like "Johns-evennia-fixes". Give a brief summary,
   like "my repo for contributing to Evennia". Accept.
#. Your new repo is created. You should see it appear in the `clone-repo
   list <https://code.google.com/p/evennia/source/clones.html>`_. This
   is actually your own mini-version of the Evennia page! Choose your
   repo and you will find it has its own Checkout page. Use the command
   there to get a local copy of your clone to your computer.
#. Code away on your computer, fixing bugs or whatnot (you can be
   offline for this). Commit your code to your local clone as you work,
   as often as you like.
#. When you have something you feel is worthwhile (or just want to ask
   people's opinions or make an online backup), *push* your local code
   up to your online repository with Mercurial.
#. Let people know what you did, talk discuss. If you think your changes
   should be merged into main Evennia (maybe you have made bugfixes,
   added new features etc), make a new
   `Issue <http://code.google.com/p/evennia/issues/list>`_ using the
   "Merge Request" template. Try to separate features with different
   commits, so it's possible to pick individual features.

From your online repo, Evennia devs can then, assuming the change is
deemed good, pick and merge your work into Evennia proper.

Contributing with Patches
-------------------------

To help with Evennia development it's recommended to do so using a clone
repository as described above. But for small, well isolated fixes you
are also welcome to submit your suggested Evennia fixes/addendums as
`patches <https://secure.wikimedia.org/wikipedia/en/wiki/Patch_(computing).html>`_
if you like. Depending on what fits best, post your patch to the `issue
tracker <https://code.google.com/p/evennia/issues/list.html>`_ or to the
`discussion
forum <https://groups.google.com/forum/#!forum/evennia.html>`_. Please
avoid pasting the full patch text directly in your post though, best is
to use a site like `Pastebin <http://pastebin.com/>`_ and just supply
the link.
