Window Objects
^^^^^^^^^^^^^^
.. automodule:: curtsies.window

Windows successively render 2D grids of text (usually :py:class:`~curtsies.formatstringarray.FSArray` objects)
to the terminal. Window should own its output stream - it is assumed no additional output occurs between renders, an assumption required for example to prevent redrawing portions of the screen which have not changed between renders.

There are two useful window classes, both subclasses of :py:class:`~curtsies.window.BaseWindow`: :py:class:`~curtsies.window.FullscreenWindow`
renders to the terminal's `alternate screen buffer`_ (no history preserved, like ``Vim``, ``top`` etc.)
while :py:class:`~curtsies.window.CursorAwareWindow` renders to the normal screen.
It is also is capable of querying the terminal for the cursor location,
and uses this functionality to detect how a terminal moves
its contents around during a window size change.
This information can be used to compensate for
this movement and prevent the overwriting of history on the terminal screen.

.. _alternate screen buffer http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#The%20Alternate%20Screen%20Buffer

Exaple
-------

    >>> from curtsies import FullscreenWindow, fsarray
    >>> import time
    >>> with FullscreenWindow() as win:
    ...     win.render_to_terminal(fsarray([u'asdf', u'asdf']j
    ...     time.sleep(1)
    ...     win.render_to_terminal(fsarray([u'asdf', u'qwer'])
    ...     time.sleep(1)

Use as a context manager
------------------------

:py:meth:`~curtsies.window.BaseWindow.render_to_terminal` should only be called within the context
of a window. Within the context of an instance of :py:class:`~curtsies.window.BaseWindow`
it's important not to write to the stream the window is using (usually ``sys.stdout``).
Displayed content and even cursor position are assumed not to change between renders.
Any change that does occur in cursor position is attributed to movement of content
in response to a window size change and is used to calculate how this content has moved,
since this behavior differs on different terminal emulators.

Entering the context of a FullscreenWindow object hides the cursor and switches to
the alternate terminal screen. Entering the context of a CursorAwareWindow hides
the cursor, turns on cbreak mode, and records the cursor position. Leaving the context
does more or less the inverse.

API Docs
--------

.. autoclass:: BaseWindow
   :members:
   
.. autoclass:: FullscreenWindow
   :members:

.. autoclass:: CursorAwareWindow
   :members:

