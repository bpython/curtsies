Input
*****
.. automodule:: curtsies.input

:py:class:`~curtsies.input.Input` objects provide user keypress events
and other control events.

Example
-------

    >>> from curtsies import Input
    >>> with Input(keynames='curtsies') as input_generator:
    >>>     for e in Input():
    >>>         if e in (u'<ESC>', u'<Ctrl-d>'):
    >>>             break
    >>>         else:
    >>>             print(e)

Using Input
-----------

Within the (context-manager) context of an Input generator, an in-stream
is put in raw mode or cbreak mode, and keypresses are stored to be reported
later.

``Terminal.next()`` waits for a keypress.
Key events are unicode
strings, but ``Terminal.next()`` will sometimes return event objects which
inherit from events.Event. ``Terminal`` objects are
iterable, so these events can be obtained by looping over the object.

``Input`` takes an optional argument for how to name
keypress events, which is 'curtsies' by default.
For compatibility with curses code, you can use 'curses' names,
but note that curses doesn't have nice key names for many key combinations
so you'll be putting up with names like ``u'\xe1'`` for
option-j and ``'\x86'`` for ctrl-option-f.
Pass 'plain' for this parameter to return a simple unicode representation.

The events returned will be unicode strings representing single keypresses,
or subclasses of events.Event.

PasteEvent objects representing multple keystrokes in very rapid succession
(typically because the user pasted in text, but possibly because they typed
two keys simultaneously. How many bytes must occur together to trigger such
an event is customizable via the paste_threshold argument to the ``Input()``
- by default it's one greater than the maximum possible keypress
length in bytes.

If ``sigint_event=True`` is passed to ``Input()``, SIGINT signals from the
operating system (which usually raise a KeyboardInterrupt exception)
will be returned as ``SigIntEvent()`` instances.

To set a timeout on the blocking get, treat it like a generator and call
``.send(timeout)``. The call will return None if no event is available.

Events
------
.. automodule:: curtsies.events

To see what a given keypress is called (what unicode string is returned
by ``Terminal.next()``), try
``python -m curtsies.terminal`` and play around.
Events returned by :py:class:`~curtsies.input.Input` fall into two categories:
instances of subclasses of :class:`curtsies.event.Event` and
Keypress strings.

Event Objects
~~~~~~~~~~~~~

.. autoclass:: curtsies.events.ScheduledEvent

.. autoclass:: curtsies.events.WindowChangeEvent

.. autoclass:: curtsies.events.SigIntEvent

.. autoclass:: curtsies.events.PasteEvent

Keypress Strings
~~~~~~~~~~~~~~~~

Unicode strings (in Python 2 and 3):

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
* Normal Meta (the escape-prepending version) key is ``<Esc+a>`` while control and shift keys are is ``<Ctrl-a>`` (note the ``+`` vs ``-``)
* Letters are capitalized in `<Esc+Ctrl-A>` while they are lowercase in ``<Ctrl-a>``
  (this should be fixed in the next api-breaking release)
* Some special characters lose their special names when used with modifier keys, for example:
  ``<TAB>, <Shift-TAB>, <Esc+Ctrl-Y>, <Esc+Ctrl-I>`` are all produced by the tab key, while ``y, Y, <Shift-TAB>, <Esc+y>, <Esc+Y>, <Esc+Ctrl-y>, <Esc+Ctrl-Y>, <Ctrl-Y>`` are all produced by the y key. (This should really be figured out)

API docs
--------

.. autoclass:: curtsies.Input
   :members:

