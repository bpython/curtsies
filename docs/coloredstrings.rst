Formatted Strings
*****************

.. automodule:: curtsies


FmtStr
======

This is something I want to say that is not in the docstring.

.. autoclass:: FmtStr
   :members: width, splice, copy_with_new_atts, copy_with_new_str, join, split

FmtStr instances respond to most :class:`str` methods as you might expect, but the result
of these methods sometimes loses its formatting.

.. automodule:: curtsies.formatstring
   :members: linesplit

FSArray
=======

If you're dealing with terminal output, the *width* of a string becomes more
important than it's *length* (`len(s)`). Graphemes, full width characters, etc.

.. autoclass:: curtsies.FSArray
   :members:

.. automodule:: curtsies.formatstringarray
   :members: FSArray, fsarray



