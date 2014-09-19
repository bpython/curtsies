[![Build Status](https://travis-ci.org/thomasballinger/curtsies.svg?branch=master)](https://travis-ci.org/thomasballinger/curtsies)
Curtsies: Terminal interaction w/o curses
=========================================
![Curtsies Logo](http://ballingt.com/assets/curtsies-tritone-small.png)

Annotate portions of strings with terminal colors and formatting!
Render that text to the terminal, and clean up afterwards!
Get user keystrokes when they happen!

This is what using (nearly every feature of) curtsies looks like:

    import random

    from curtsies import FullscreenWindow, Input, FSArray
    from curtsies.fmtfuncs import red, bold, green, on_blue, yellow

    print yellow('the following code takes over the screen')
    with FullscreenWindow() as window:
        print(red(on_blue(bold('Press escape to exit'))))
        with Input() as input_generator:
            a = FSArray(window.height, window.width)
            for c in input_generator:
                if c == '<ESC>':
                    break
                elif c == '<SPACE>':
                    a = FSArray(window.height, window.width)
                else:
                    row = random.choice(range(window.height))
                    column = random.choice(range(window.width-len(repr(c))))
                    color = random.choice([red, green, on_blue, yellow])
                    a[row, column:column+len(repr(c))] = [color(repr(c))]
                window.render_to_terminal(a)

There are a few main objects in curtsies you probably want to use:

* [FmtStr](readme.md#fmtstr) objects are colored strings
* [FSArray](readme.md#fsarray) objects are 2D arrays of colored text
* [Input](readme.md#input) provides keys as they are pressed by the user
* [FullscreenWindow](readme.md#fullscreenwindow) sets up a fullscreen environment for rendering arrays of colored text
* [CursorAwareWindow](readme.md#cursorawarewindow) is a terminal wrapper (like curses) for rendering text to the terminal

`FmtStr`
=========

![fmtstr example screenshot](http://i.imgur.com/7lFaxsz.png)

You can use convenience functions instead:

    >>> from fmtstr.fmtfuncs import *
    >>> blue(on_red('hey')) + " " + underline("there")

* `str(FmtStr)` -> escape sequence-laden text that looks cool in an ANSI-compatible terminal
* `repr(FmtStr)` -> how to create an identical FmtStr
* `FmtStr[3:10]` -> a new FmtStr
* `FmtStr.upper()` (any string method) -> a new FmtStr or list of FmtStrs (str.split) or int (str.count)

Other Libraries
---------------

If all you need are colored strings, you've got some other great options (other wrappings of
[ANSI escape codes](http://en.wikipedia.org/wiki/ANSI_escape_code)):

* [Blessings](https://github.com/erikrose/blessings) (`pip install blessings`)
  As of version 0.1.0, Curtsies uses Blessings for terminal capabilities other
  than colored output.
* https://github.com/verigak/colors/ (`pip install colors`)
* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py (`pip install clint`)
* https://pypi.python.org/pypi/termcolor (`pip install termcolor`)

In all of these libraries the expression `blue('hi') + ' ' + green('there)`
or equivalent
evaluates to a Python string, not a colored string object. If all you plan
to do with this string is print it, this is fine. But if you need to
do more formatting with this colored string later, the length will be
something like 29 instead of 9; structured formatting information is lost.
Methods like `.ljust()` won't properly format the string for display.

    >>> import blessings
    >>> t = blessings.Terminal()
    >>> message = term.red_on_green('Red on green?') + ' ' + term.yellow('Ick!')
    >>> len(message)
    41 # ?!
    >>> message.center(50)
    u'    \x1b[31m\x1b[42mRed on green?\x1b[m\x0f \x1b[33mIck!\x1b[m\x0f     '

FmtStrs can be combined and composited to create more complicated FmtStrs,
useful for example for building flashy terminal interfaces with overlapping
windows/widgets than can change size and depend on each others sizes.
One FmtStr can have several kinds of formatting applied to different parts of it.

    >>> from curtsies.fmtfuncs import *
    >>> blue('asdf') + on_red('adsf')
    blue("asdf")+on_red("adsf")

Details
-------

FmtStrs allow slicing, which returns a new FmtStr object:

    >>> from curtsies.fmtfuncs import *
    >>> (blue('asdf') + on_red('adsf'))[3:7]
    blue("f")+on_red("ads")

FmtStrs are *immutable* - but you can create new ones with `splice`:

    >>> from curtsies.fmtfuncs import *
    >>> f = blue('hey there') + on_red(' Tom!')
    >>> g.splice('ot', 1, 3)
    >>> g
    blue("h")+"ot"+blue(" there")+on_red(" Tom!")

which can even change their length:

    >>> f.splice('something longer', 2)
    blue("h")+"something longer"+blue("ot")+blue(" there")+on_red(" Tom!")

(Thanks to @OufeiDong for fixing this!)

FmtStrs greedily absorb strings, but no formatting is applied

    >>> from curtsies.fmtfuncs import *
    >>> f = blue("The story so far:") + "In the beginning..."
    >>> type(f)
    <class curtsies.fmtstr.FmtStr>
    >>> f
    blue("The story so far:")+"In the beginning..."

It's easy to turn ANSI terminal formatted strings into FmtStrs:

    >>> from curtsies.fmtfuncs import *
    >>> from curtsies import FmtStr
    >>> s = str(blue('tom'))
    >>> s
    '\x1b[34mtom\x1b[39m'
    >>> FmtStr.from_str(str(blue('tom')))
    blue("tom")

Using str methods on FmtStr objects
-----------------------------------

All sorts of string methods can be used on a FmtStr, so you can often
use FmtStr objects where you had strings in your program before:

    >>> from curtsies.fmtfuncs import *
    >>> f = blue(underline('As you like it'))
    >>> len(f)
    14 
    >>> f == underline(blue('As you like it')) + red('')
    True
    >>> blue(', ').join(['a', red('b')])
    "a"+blue(", ")+red("b")

If FmtStr doesn't implement a method, it tries its best to use the string
method, which often works pretty well:

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

But formatting information will be lost for attributes which are not the same through the whole string

    >>> from curtsies.fmtfuncs import *
    >>> f = bold(red('hi')+' '+on_blue('there'))
    >>> f
    bold(red('hi'))+bold(' ')+bold(on_blue('there'))
    >>> f.center(10)
    bold(" hi there ")

`FSArray`
=========

2D array in which each line is a FmtStr.

![fsarray example screenshot](http://i.imgur.com/rvTRPv1.png)

Slicing works like it does with FmtStrs, but in two dimensions.
FSArrays are *mutable*, so array assignment syntax can be used for natural
compositing.

    >>> from curtsies import FSArray, fsarray
    >>> a = fsarray('-'*10 for _ in range(4))
    >>> a[1:3, 3:7] = fsarray([green('msg:'),
    ...                blue(on_green('hey!'))])
    >>> a.dumb_display()
    ----------
    ---msg:---
    ---hey!---
    ----------

`fsarray` is a convenience function returning a FSArray constructed from its arguments.

`FullscreenWindow`
==================

FullscreenWindow will only render arrays the size of the terminal
or smaller, and leaves no trace on exit (like top or vim). It never
scrolls the terminal. Changing the terminal size doesn't do anything,
but 2d array rendered needs to fit on the screen.

`CursorAwareWindow`
===================

CursorAwareWindow provides the ability to find the
location of the cursor, and allows scrolling.
Sigwinches can be annotated with how the terminal scroll changed
Changing the terminal size breaks the cache, because it
is unknown how the window size change affected scrolling / the cursor.
Leaving the context of the window deletes everything below the cursor
at the beginning of the its current line.
(use scroll_down() from the last rendered line if you want to save all history)

`Input`
=======

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

Examples
--------

* [Tic-Tac-Toe](/examples/tictactoeexample.py)

![screenshot](http://i.imgur.com/AucB55B.png)

* [Avoid the X's game](/examples/gameexample.py)

![screenshot](http://i.imgur.com/nv1RQd3.png)

* [Bpython-curtsies uses curtsies](http://ballingt.com/2013/12/21/bpython-curtsies.html)

[![ScreenShot](http://i.imgur.com/r7rZiBS.png)](http://www.youtube.com/watch?v=lwbpC4IJlyA)

* [More examples](/examples)

Authors
-------
* Thomas Ballinger
* Fei Dong - work on making FmtStr and Chunk immutable
* Julia Evans - help with Python 3 Conversion
* Zach Allaun, Mary Rose Cook, Alex Clemmer - early code review of terminal.py
* Rachel King - several bugfixes on blessings use
* Amber Wilcox-O'Hearn - paired on a refactoring
* Darius Bacon - lots of great code review
* inspired by a conversation with Scott Feeney
* Lea Albaugh - beautiful Curtsies logo
* Nick Sweeting - fish-style history search and completion
