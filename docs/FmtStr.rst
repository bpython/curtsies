FmtStr
^^^^^^

:py:class:`~curtsies.FmtStr` is a string with each character colored
and styled in ways representable by `ANSI escape codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_.

.. automodule:: curtsies.formatstring

FmtStr - Example
================

.. python_terminal_session::

   from curtsies import fmtstr
   red_on_blue = fmtstr(u'hello', fg='red', bg='blue')
   from curtsies.fmtfuncs import *
   blue_on_red = blue(on_red(u'there'))
   bang = bold(underline(green(u'!')))
   full = red_on_blue + blue_on_red + bang
   str(full)
   print(full)

We start here with such a complicated example because if you only need something simple like:

.. python_terminal_session::

   from curtsies.fmtfuncs import *
   print(blue(bold(u'Deep blue sea')))

then another library may be a better fit than Curtsies.
Unlike other libraries, Curtsies allows these colored strings to be further manipulated after
they are created.

Available colours and styles
----------------------------

The following colours are available with corresponding foreground and background functions:

=======  =============  ================
Name     Foreground     Background
=======  =============  ================
black    ``black()``    ``on_black()``
red      ``red()``      ``on_red()``
green    ``green()``    ``on_green()``
yellow   ``yellow()``   ``on_yellow()``
blue     ``blue()``     ``on_blue()``
magenta  ``magenta()``  ``on_magenta()``
cyan     ``cyan()``     ``on_cyan()``
gray     ``gray()``     ``on_gray()``
=======  =============  ================

And the following styles with their corresponding functions:

=========  ===============
Style      Function
=========  ===============
bold       ``bold()``
dark       ``dark()``
underline  ``underline()``
blink      ``blink()``
invert     ``invert()``
=========  ===============

FmtStr - Rationale
==================

If all you need is to print colored text, many other libraries also make `ANSI escape codes <http://en.wikipedia.org/wiki/ANSI_escape_code>`_ easy to use.

* `Blessings <https://github.com/erikrose/blessings>`_ (``pip install blessings``)
  As of version 0.1.0, Curtsies uses Blessings for terminal capabilities other
  than colored output.
* `termcolor <https://pypi.python.org/pypi/termcolor>`_ (``pip install termcolor``)
* `Clint <https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py>`_ (``pip install clint``)
* `colors <https://github.com/verigak/colors/>`_ (``pip install colors``)

In all of the libraries listed above, the expression ``blue('hi') + ' ' + green('there)``
or equivalent
evaluates to a Python string, not a colored string object. If all you plan
to do with this string is print it, this is great. But, if you need to
do more formatting with this colored string later, the length will be
something like 29 instead of 9; structured formatting information is lost.
Methods like :py:meth:`center <https://docs.python.org/2/library/stdtypes.html#str.center>`
and :py:meth:`ljust <https://docs.python.org/2/library/stdtypes.html#str.ljust>`
won't properly format the string for display.

>>> import blessings
>>> term = blessings.Terminal()
>>> message = term.red_on_green('Red on green?') + ' ' + term.yellow('Ick!')
>>> len(message)
41 # ?!
>>> message.center(50)
u'    \x1b[31m\x1b[42mRed on green?\x1b[m\x0f \x1b[33mIck!\x1b[m\x0f     '

:py:class:`~curtsies.FmtStr` objects can be combined and composited to create more complicated
:py:class:`~curtsies.FmtStr` objects,
useful for building flashy terminal interfaces with overlapping
windows/widgets that can change size and depend on each other's sizes.
One :py:class:`~curtsies.FmtStr` can have several kinds of formatting applied to different parts of it.

>>> from curtsies.fmtfuncs import *
>>> blue('asdf') + on_red('adsf')
blue("asdf")+on_red("adsf")

FmtStr - Using
==============

A :py:class:`~curtsies.FmtStr` can be sliced to produce a new :py:class:`~curtsies.FmtStr` objects:

    >>> from curtsies.fmtfuncs import *
    >>> (blue('asdf') + on_red('adsf'))[3:7]
    blue("f")+on_red("ads")

:py:class:`~curtsies.FmtStr` are *immutable* - but you can create new ones with :py:meth:`~curtsies.FmtStr.splice`:

    >>> from curtsies.fmtfuncs import *
    >>> f = blue('hey there') + on_red(' Tom!')
    >>> g.splice('ot', 1, 3)
    >>> g
    blue("h")+"ot"+blue(" there")+on_red(" Tom!")
    >>> f.splice('something longer', 2)
    blue("h")+"something longer"+blue("ot")+blue(" there")+on_red(" Tom!")

:py:class:`~curtsies.FmtStr` greedily absorb strings, but no formatting is applied to this added text:

    >>> from curtsies.fmtfuncs import *
    >>> f = blue("The story so far:") + "In the beginning..."
    >>> type(f)
    <class curtsies.fmtstr.FmtStr>
    >>> f
    blue("The story so far:")+"In the beginning..."

It's easy to turn ANSI terminal formatted strings into :py:class:`~curtsies.FmtStr`:

    >>> from curtsies.fmtfuncs import *
    >>> from curtsies import FmtStr
    >>> s = str(blue('tom'))
    >>> s
    '\x1b[34mtom\x1b[39m'
    >>> FmtStr.from_str(str(blue('tom')))
    blue("tom")

FmtStr - Using str methods
--------------------------

All sorts of `string methods <https://docs.python.org/2/library/stdtypes.html#string-methods>`_
can be used on a :py:class:`~curtsies.FmtStr`, so you can often
use :py:class:`~curtsies.FmtStr` objects where you had strings in your program before::

    >>> from curtsies.fmtfuncs import *
    >>> f = blue(underline('As you like it'))
    >>> len(f)
    14 
    >>> f == underline(blue('As you like it')) + red('')
    True
    >>> blue(', ').join(['a', red('b')])
    "a"+blue(", ")+red("b")

If :py:class:`~curtsies.FmtStr` doesn't implement a method, it tries its best to use the string
method, which often works pretty well::

    >>> from curtsies.fmtfuncs import *
    >>> f = blue(underline('As you like it'))
    >>> f.center(20)
    blue(underline("   As you like it   "))
    >>> f.count('i')
    2
    >>> f.endswith('it')
    True
    >>> f.index('you')
    3
    >>> f.split(' ')
    [blue(underline("As")), blue(underline("you")), blue(underline("like")), blue(underline("it"))]

But formatting information will be lost for attributes which are not the same throughout the initial string::

    >>> from curtsies.fmtfuncs import *
    >>> f = bold(red('hi')+' '+on_blue('there'))
    >>> f
    bold(red('hi'))+bold(' ')+bold(on_blue('there'))
    >>> f.center(10)
    bold(" hi there ")

FmtStr - Unicode
----------------

In Python 2, you might run into something like this:

.. code-block:: python

   >>> from curtsies.fmtfuncs import *
   >>> red(u'hi')
   red('hi')
   >>> red('hi')
   ValueError: unicode string required, got 'hi'

:py:class:`~curtsies.FmtStr` requires unicode strings, so in Python 2 it is convenient to use the unicode_literals compiler directive:

    >>> from __future__ import unicode_literals
    >>> from curtsies.fmtfuncs import *
    >>> red('hi')
    red('hi')

.. _len-vs-width:

FmtStr - len vs width
---------------------

The amount of horizontal space a string takes up in a terminal may differ from the length of the string returned by ``len()``.
To access this information, :py:class:`~curtsies.FmtStr` objects have a :py:class:`~curtsies.FmtStr.width` property, which can be useful when writing layout code:

>>> #encoding: utf8
... 
>>> from curtsies.fmtfuncs import *
>>> fullwidth = blue(u'ｆｕｌｌwidth')
>>> len(fullwidth), fullwidth.width, fullwidth.s
(9, 13, u'\uff46\uff55\uff4c\uff4cwidth')
>>> combined = red(u'a̤')
>>> len(combined), combined.width, combined.s
(2, 1, u'a\u0324')

As shown above, `full width characters <http://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms>`_ can take up two columns, and `combining characters <http://en.wikipedia.org/wiki/Combining_character>`_ may be combined with the previous character to form a single grapheme. Curtsies uses a `Python implementation of wcwidth <https://github.com/jquast/wcwidth>`_ to do this calculation.

FmtStr - API Docs
=================

.. autofunction:: curtsies.fmtstr

.. autoclass:: curtsies.FmtStr
   :members: width, splice, copy_with_new_atts, copy_with_new_str, join, split, splitlines, width_aware_slice

.. automodule:: curtsies.fmtfuncs

:py:class:`~curtsies.FmtStr` instances respond to most :class:`str` methods as you might expect, but the result
of these methods sometimes loses its formatting.
