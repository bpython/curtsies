Colored/Styled Strings for the Terminal
=======================================

Annotate portions of strings with terminal colors and formatting!

Most terminals will display text in color if you use [ANSI escape codes]
(http://en.wikipedia.org/wiki/ANSI_escape_code) - fmtstr makes rendering such
text to the terminal easy.

The three objects in fmtstr you probably want to use:

* [FmtStr](readme.md#fmtstr) objects are colored strings
* [FSArray](readme.md#fsarray) objects are 2D arrays of colored text
* [Terminal](readme.md#terminal) is a terminal wrapper (like curses) for rendering text to the terminal
and handling user input

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

If all you need are colored strings, you've got some other great options:

* https://github.com/erikrose/blessings (`pip install blessings`) Blessings
  also does a lot of what `Terminal` objects do, with a really nice api.
* https://github.com/verigak/colors/ (`pip install colors`)
* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py (`pip install clint`)

In all of these libraries the expression `blue('hi') + ' ' + green('there)`
or equivalent
evaluates to a Python string, not a colored string object. If all you plan
to do with this string is print it, this is fine. But if you need to
do more formatting with this colored string later, the length will be
something like 29 instead of 9; structured formatting information is lost.
Methods like `.ljust()` won't properly format the string for display.

FmtStrs can be combined and composited to create more complicated FmtStrs,
useful for example for building flashy terminal interfaces with overlapping
windows/widgets than can change size and depend on each others sizes.

Details
-------

One FmtStr can have several kinds of formatting applied to different parts of it.

    >>> from fmtstr.fmtfuncs import *
    >>> blue('asdf') + on_red('adsf')
    blue("asdf")+on_red("adsf")

They allow slicing, which returns a new FmtStr object:

    >>> from fmtstr.fmtfuncs import *
    >>> (blue('asdf') + on_red('adsf'))[3:7]
    blue("f")+on_red("ads")

FmtStrs are *immutable* - but you can create new ones with `insert`:

    >>> from fmtstr.fmtfuncs import *
    >>> f = blue('hey there') + on_red(' Tom!')
    >>> g.insert('ot', 1, 3)
    >>> g
    blue("h")+"ot"+blue(" there")+on_red(" Tom!")

which can even change their length:

    >>> f.insert('something longer', 2)
    blue("h")+"something longer"+blue("ot")+blue(" there")+on_red(" Tom!")

Thanks to @OufeiDong for fixing this!

FmtStrs greedily absorb strings, but no formatting is applied

    >>> from fmtstr.fmtfuncs import *
    >>> f = blue("The story so far:") + "In the beginning..."
    >>> type(f)
    <class fmtstr.fmtstr.FmtStr>
    >>> f
    blue("The story so far:")+"In the beginning..."

It's easy to turn ANSI terminal formatted strings into FmtStrs:

    >>> from fmtstr.fmtfuncs import *
    >>> from fmtstr.fmtstr import FmtStr
    >>> s = str(blue('tom'))
    >>> s
    '\x1b[34mtom\x1b[39m'
    >>> FmtStr.from_str(str(blue('tom')))
    blue("tom")

Using str methods on FmtStr objects
-----------------------------------

All sorts of string methods can be used on a FmtStr, so you can often
use FmtStr objects where you had strings in your program before:

    >>> from fmtstr.fmtstr import *
    >>> f = blue(underline('As you like it'))
    >>> len(f)
    14 
    >>> f == underline(blue('As you like it')) + red('')
    True
    >>> blue(', ').join(['a', red('b')])
    "a"+blue(", ")+red("b")

If FmtStr doesn't implement a method, it tries its best to use the string
method, which often works pretty well:

    >>> from fmtstr.fmtstr import *
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

    >>> from fmtstr.fmtstr import *
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

    >>> from fmtstr.fsarray import FSArray
    >>> from fmtstr.fmtstr import FSArray
    >>> a = fsarray('-'*10 for _ in range(4))
    >>> a[1:3, 3:7] = fsarray([green('msg:'),
    ...                blue(on_green('hey!'))])
    >>> a.dumb_display()
    ----------
    ---msg:---
    ---hey!---
    ----------

`Terminal`
==========

Interact with the Terminal object by passing .render_to_terminal()
fsarrays, 2D numpy arrays of characters, or arrays of strings or FmtStr objects.
Terminal objects typically to be initialized with a TerminalController object
which sets up the terminal
window and catches input in raw mode. Context managers make it so fatal
exceptions won't prevent necessary cleanup to make the terminal usable again.

Putting all that together:

    import sys
    from fmtstr.fmtfuncs import *
    from fmtstr.terminal import Terminal
    from fmtstr.terminalcontrol import TerminalController

    with TerminalController(sys.stdin, sys.stdout) as tc:
        with Terminal(tc) as t:
            rows, columns = t.tc.get_screen_size()
            while True:
                c = t.tc.get_event()
                if c == "\x04":
                    sys.exit()
                elif c == "a":
                    a = [blue(on_red(c*columns)) for _ in range(rows)]
                    # covers the entire screen with blue a's on a red background
                elif c == "b":
                    a = t.array_from_text("this is a small array")
                    # renders a small array where the cursor is
                else:
                    a = t.array_from_text("try a, b, or ctrl-D")
                t.render_to_terminal(a)

When a Terminal object is passed an array with more rows than it's height, it writes
the entire array to the terminal, scrolling down so that the extra rows at the
top of the 2D array end up out of view. This behavior is particularly useful for
writing command line interfaces.

Examples
--------

* [Tic-Tac-Toe](tictactoeexample.py)

![screenshot](http://i.imgur.com/AucB55B.png)

* [Avoid the X's game](gameexample.py)

![screenshot](http://i.imgur.com/nv1RQd3.png)

* [Bpython frontend bpython-scroll](https://bitbucket.org/thomasballinger/bpython/src/764d6710346db8d94d2e318d0f183cdf5ebf1174/bpython/scroll.py?at=scroll-frontend)

[![ScreenShot](http://i.imgur.com/r7rZiBS.png)](http://www.youtube.com/watch?v=lwbpC4IJlyA)

Notes
=====

No Windows support currently for Terminal objects- I'm hoping
[colorama](https://pypi.python.org/pypi/colorama)
will eventually make Windows support possible, but it currently doesn't implement many of
the ANSI terminal control sequences used by the terminal controller.

Using colorama, Fmtstr and FSArray should work find in Windows, but I haven't tried this.

Authors
-------
* Thomas Ballinger
* Fei Dong - work on making FmtStr and BaseFmtStr immutable
* Julia Evans - help with Python 3 Conversion
* Zach Allaun, Mary Rose Cook, Alex Clemmer - early code review of terminal.py
* inspired by a conversation with Scott Feeney
