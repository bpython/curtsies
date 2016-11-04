Curtsies documentation
^^^^^^^^^^^^^^^^^^^^^^
.. |shoes| image:: http://ballingt.com/assets/curtsies-tritone-small.png
.. |curtsiestitle| image:: http://ballingt.com/assets/curtsiestitle.png

|curtsiestitle|

Curtsies is a Python 2.6+ & 3.3+ compatible library for interacting with the terminal.

:py:class:`~curtsies.FmtStr` objects are strings formatted with
colors and styles displayable in a terminal with `ANSI escape sequences <http://en.wikipedia.org/wiki/ANSI_escape_code>`_.
:py:class:`~curtsies.FSArray` objects contain multiple such strings
with each formatted string on its own row, and
can be superimposed onto each other
to build complex grids of colored and styled characters.

Such grids of characters can be efficiently rendered to the terminal in alternate screen mode
(no scrollback history, like ``Vim``, ``top`` etc.) by :py:class:`~curtsies.FullscreenWindow` objects
or to the normal history-preserving screen by :py:class:`~curtsies.CursorAwareWindow` objects.
User keyboard input events like pressing the up arrow key are detected by an
:py:class:`~curtsies.Input` object. See the :doc:`quickstart` to get started using
all of these classes.

.. toctree::
   :maxdepth: 3

   quickstart
   FmtStr
   FSArray
   window
   Input
   gameloop
   examples
   about

