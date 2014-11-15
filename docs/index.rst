Curtsies documentation
======================
.. |shoes| image:: http://ballingt.com/assets/curtsies-tritone-small.png

Curtsies is a library for interacting with the terminal.
It does colored strings, grids of formatted characters fit
for display in a terminal, rendering to the terminal and keyboard input.

below

.. python_terminal_session::

   1 + 1
   2 + 3
   from curtsies.fmtfuncs import red, on_green, bold
   s = bold(red(on_green(u'hello!')))
   s
   print s

.. ansi-block::

   hi
   [34m[42mhello![0m

above

Contents:

.. toctree::
   :maxdepth: 2

   coloredstrings
   window
   input

.. automodule:: curtsies


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

