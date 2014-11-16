Input
*****************
.. automodule:: curtsies.input

Within the (context-manager) context of an Input generator, an in-stream
is put in raw mode or cbreak mode, and keypresses are stored to be reported
later.

`Terminal.next()` waits for a keypress.
To see what a given keypress is called (what unicode string is returned
by `Terminal.next()`), try
`python -m curtsies.terminal` and play around. Key events are unicode
strings, but `Terminal.next()` will sometimes return event objects which
inherit from events.Event. `Terminal` objects are
iterable, so these events can be obtained by looping over the object.

`Input` takes an optional argument for how to name
keypress events, which is 'curtsies' by default.
For compatibility with curses code, you can use 'curses' names,
but note that curses doesn't have nice key names for many key combinations
so you'll be putting up with names like `u'\xe1'` for
option-j and `'\x86'` for ctrl-option-f.
Pass 'plain' for this parameter to return a simple unicode representation.

The events returned will be unicode strings representing single keypresses,
or subclasses of events.Event.

PasteEvent objects representing multple keystrokes in very rapid succession
(typically because the user pasted in text, but possibly because they typed
two keys simultaneously. How many bytes must occur together to trigger such
an event is customizable via the paste_threshold argument to the `Input()`
- by default it's one greater than the maximum possible keypress
length in bytes.

If `sigint_event=True` is passed to `Input()`, SIGINT signals from the
operating system (which usually raise a KeyboardInterrupt exception)
will be returned as `SigIntEvent()`s.

To set a timeout on the blocking get, treat it like a generator and call
`.send(timeout)`. The call will return None if no event is available.

API docs
--------


.. autoclass:: curtsies.Input
   :members:

