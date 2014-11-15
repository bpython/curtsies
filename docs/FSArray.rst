FSArray
=======

If you're dealing with terminal output, the *width* of a string becomes more
important than it's *length* (`len(s)`). Graphemes, full width characters, etc.

FSArrays deal with the display width of strings.

This module also contains useful formatting tools for constructing and modifying
FSArrays: getting width

.. autoclass:: curtsies.FSArray
   :members:

.. automodule:: curtsies.formatstringarray
   :members: FSArray, fsarray

