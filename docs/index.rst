Welcome to the Curtsies documentation
=====================================
.. |shoes| image:: http://ballingt.com/assets/curtsies-tritone-small.png
.. |curtsiestitle| image:: http://ballingt.com/assets/curtsiestitle.png

|curtsiestitle|

Curtsies is a library for interacting with the terminal.
It has ANSI formatted strings (:py:meth:`~curtsies.formatstring.FmtStr`),
2D grids of formatted characters fit for display in a terminal(:py:class:`~curtsies.formatstringarray.FSArray`),
cached rendering to the terminal in alternate screen
(no history, like ``Vim``, ``top`` etc; :py:class:`~curtsies.window.FullscreenWindow`)
or normal history-preserving mode (:py:class:`~curtsies.window.CursorAwareWindow`)
and detection of keyboard input (:py:clas:`~curtsies.input.Input`).

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   FmtStr
   FSArray
   window
   input


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

