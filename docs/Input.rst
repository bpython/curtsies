Input
^^^^^
.. automodule:: curtsies.Input

:py:class:`~curtsies.Input` objects provide user keypress events
and other control events.

Input - Example
===============

    >>> from curtsies import Input
    >>> with Input(keynames='curtsies') as input_generator:
    ...     for e in Input():
    ...         if e in (u'<ESC>', u'<Ctrl-d>'):
    ...             break
    ...         else:
    ...             print(e)

Input - Getting Keyboard Events
===============================

The simplest way to use an :py:class:`~curtsies.Input` object is to
iterate over it in a for loop:
each time a keypress is detected or other event occurs, an event is produced
and can be acted upon.
Since it's iterable, ``next()`` can be used to wait for a single event.
:py:meth:`~curtsies.Input.send` works like ``next()`` but takes a timeout
in seconds, which if reached will cause None to be returned signalling
that no keypress or other event occured within the timeout.

Key events are unicode strings, but sometimes event objects
(see :class:`~curtsies.events.Event`) are returned instead.
Built-in events signal :py:class:`~curtsies.events.SigIntEvent` 
events from the OS and :py:class:`~curtsies.events.PasteEvent` consisting
of multiple keypress events if reporting of these types of events was enabled
in instantiation of the :py:class:`~curtsies.Input` object.

Input - Using as a Reactor
==========================

Custom events can also be scheduled to be returned from
:py:class:`~curtsies.Input` with callback functions
created by the event trigger methods.

Each of these methods returns a callback that will schedule an instance of the
desired event type:

* Using a callback created by :py:meth:`~curtsies.Input.event_trigger`
  schedules an event to be returned the next time an event is requested, but
  not if an event has already been requested (if called from another thread).

* :py:meth:`~curtsies.Input.threadsafe_event_trigger` does the same,
  but may notify a concurrent request for an event so that the custom event
  is immediately returned.

* :py:meth:`~curtsies.Input.scheduled_event_trigger` schedules an event
  to be returned at some point in the future.

Input - Context
===============

``next()`` and :meth:`~curtsies.Input.send()`
must be used within the context of that :class:`~curtsies.Input` object.

Within the (context-manager) context of an Input generator, an in-stream
is put in raw mode or cbreak mode, and keypresses are stored to be reported
later. Original tty attributes are recorded to be restored on exiting
the context. The SigInt signal handler may be replaced if this behavior was
specified on creation of the :class:`~curtsies.Input` object.

Input - Notes
=============

:py:class:`~curtsies.Input` takes an optional argument ``keynames`` for how to name
keypress events, which is ``'curtsies'`` by default.
For compatibility with curses code, you can use ``'curses'`` names,
but note that curses doesn't have nice key names for many key combinations
so you'll be putting up with names like ``u'\xe1'`` for
``option-j`` and ``'\x86'`` for ``ctrl-option-f``.
Pass ``'plain'`` for this parameter to return a simple unicode representation.

:py:class:`~curtsies.events.PasteEvent` objects representing multiple 
keystrokes in very rapid succession
(typically because the user pasted in text, but possibly because they typed
two keys simultaneously). How many bytes must occur together to trigger such
an event is customizable via the ``paste_threshold`` argument to the :py:class:`~curtsies.Input`
object - by default it's one greater than the maximum possible keypress
length in bytes.

If ``sigint_event=True`` is passed to :py:class:`~curtsies.Input`, ``SIGINT`` signals from the
operating system (which usually raises a ``KeyboardInterrupt`` exception)
will be returned as :py:class:`~curtsies.events.SigIntEvent` instances.

To set a timeout on the blocking get, treat it like a generator and call
``.send(timeout)``. The call will return ``None`` if no event is available.

Input - Events
==============

To see what a given keypress is called (what unicode string is returned
by ``Terminal.next()``), try
``python -m curtsies.events`` and play around.
Events returned by :py:class:`~curtsies.Input` fall into two categories:
instances of subclasses of :py:class:`~curtsies.events.Event` and
Keypress strings.

Input - Event Objects
---------------------

.. autoclass:: curtsies.events.Event

.. autoclass:: curtsies.events.SigIntEvent

.. autoclass:: curtsies.events.PasteEvent

.. autoclass:: curtsies.events.ScheduledEvent

Input - Keypress Strings
------------------------

Keypress events are Unicode strings in both Python 2 and 3 like:

* ``a, 4, *, ?``
* ``<UP>, <DOWN>, <RIGHT>, <LEFT>``
* ``<SPACE>, <TAB>, <F1>, <F12>``
* ``<BACKSPACE>, <HOME>, <PADENTER>, <PADDELETE>``
* ``<Ctrl+a>, <Ctrl+SPACE>``
* ``A, <Shift-TAB>, ?``
* ``<Esc+a>, <Esc+A>, <Esc+Ctrl-A>``
* ``<Esc+Ctrl+A>``
* ``<Meta-J>, <Meta-Ctrl-J>`` (this is old-style meta)

Likely points of confusion for keypress strings:

* Enter is ``<Ctrl-j>``
* Modern meta (the escape-prepending version) key is ``<Esc+a>`` while control and shift keys are ``<Ctrl-a>`` (note the + vs -)
* Letter keys are capitalized in ``<Esc+Ctrl-A>`` while they are lowercase in ``<Ctrl-a>``
  (this should be fixed in the next api-breaking release)
* Some special characters lose their special names when used with modifier keys, for example:
  ``<TAB>, <Shift-TAB>, <Esc+Ctrl-Y>, <Esc+Ctrl-I>`` are all produced by the tab key, while ``y, Y, <Shift-TAB>, <Esc+y>, <Esc+Y>, <Esc+Ctrl-y>, <Esc+Ctrl-Y>, <Ctrl-Y>`` are all produced by the y key. (This should really be figured out)


Input - API docs
================

.. autoclass:: curtsies.Input
   :members:
   :member-order: bysource

