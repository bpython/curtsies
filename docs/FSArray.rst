FSArray
^^^^^^^

:py:class:`~curtsies.FSArray` is a two dimensional grid of colored and styled characters.

FSArray - Example
=================

.. python_terminal_session::

   from curtsies import FSArray, fsarray
   from curtsies.fmtfuncs import green, blue, on_green
   a = fsarray([u'*' * 10 for _ in range(4)], bg='blue', fg='red')
   a.dumb_display()
   a[1:3, 3:7] = fsarray([green(u'msg:'),
                          blue(on_green(u'hey!'))])
   a.dumb_display()

:py:class:`~curtsies.fsarray` is a convenience function returning a :py:class:`~curtsies.FSArray` constructed from its arguments.

FSArray - Using
===============

:py:class:`~curtsies.FSArray` objects can be composed to build up complex text interfaces::

    >>> import time
    >>> from curtsies import FSArray, fsarray, fmtstr
    >>> def clock():
    ...     return fsarray([u'::'+fmtstr(u'time')+u'::',
    ...                     fmtstr(time.strftime('%H:%M:%S').decode('ascii'))])
    ... 
    >>> def square(width, height, char):
    ...     return fsarray(char*width for _ in range(height))
    ... 
    >>> a = square(40, 10, u'+')
    >>> a[2:8, 2:38] = square(36, 6, u'.')
    >>> c = clock()
    >>> a[2:4, 30:38] = c
    >>> a[6:8, 30:38] = c
    >>> message = fmtstr(u'compositing several FSArrays').center(40, u'-')
    >>> a[4:5, :] = [message]
    >>> 
    >>> a.dumb_display()
    ++++++++++++++++++++++++++++++++++++++++
    ++++++++++++++++++++++++++++++++++++++++
    ++............................::time::++
    ++............................21:59:31++
    ------compositing several FSArrays------
    ++....................................++
    ++............................::time::++
    ++............................21:59:31++
    ++++++++++++++++++++++++++++++++++++++++
    ++++++++++++++++++++++++++++++++++++++++

An array like the above might be repeatedly constructed and rendered with a :py:mod:`curtsies.window` object.

Slicing works like it does with a :py:class:`~curtsies.FmtStr`, but in two dimensions.
:py:class:`~curtsies.FSArray` are *mutable*, so array assignment syntax can be used for natural
compositing as in the above exaple.

If you're dealing with terminal output, the *width* of a string becomes more
important than it's *length* (see :ref:`len-vs-width`).

In the future :py:class:`~curtsies.FSArray` will do slicing and array assignment based on width instead of number of characters, but this is not currently implemented.

FSArray - API docs
==================

.. autofunction:: curtsies.fsarray

.. autoclass:: curtsies.FSArray
   :members:
