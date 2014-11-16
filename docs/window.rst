Window
^^^^^^

Windows render 2D grids of text (usually :py:class:`~curtsies.formatstringarray.FSArray` objects)
to the terminal. Thay may do caching for performance

There are two different window classes: :py:class:`~curtsies.window.FullscreenWindow`
renders to the terminal's `alternate screen buffer`_ (no history preserved, like ``Vim``, ``top`` etc.)
while (:py:class:`~curtsies.window.CursorAwareWindow`) renders normally. It also is capable of
asking where the cursor is located, and uses this functionality to detect how a terminal moves
its contents around during a window size change. This information can be used to compensate for
this movement and prevent the overwriting of history on the terminal screen.

.. _alternate screen buffer http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#The%20Alternate%20Screen%20Buffer

API Docs
--------

.. automodule:: curtsies.window

.. autoclass:: BaseWindow
   :members:
   
.. autoclass:: FullscreenWindow
   :members:

.. autoclass:: CursorAwareWindow
   :members:

