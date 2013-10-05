Colored/Styled Strings for the Terminal
=======================================

`fmtstr` annotates portions of strings with terminal colors and formatting
`str(yourstring)` will be the string with [ANSI escape codes]
(http://en.wikipedia.org/wiki/ANSI_escape_code)
specifying color and other formatting to a terminal.

`FmtStr`s
=========

![fmtstr example screenshot](http://i.imgur.com/7lFaxsz.png)

You can use convenience functions instead:

    >>> from fmtstr.fmtfuncs import *
    >>> blue(on_red('hey')) + " " + underline("there")

* `str(FmtStr)` -> escape sequence-laden text that looks cool in an ANSI-compatible terminal
* `repr(FmtStr)` -> how to create an identical FmtStr
* `FmtStr[3:10]` -> a new FmtStr
* `FmtStr.upper()` (any string method) -> a new FmtStr or list of FmtStrs or int (str.count)

See also

* https://github.com/verigak/colors/ (`pip install colors`)
* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py (`pip install clint`)

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

FmtStrs are *mutable* - you can change them via slice assignment:

    >>> from fmtstr.fmtfuncs import *
    >>> f = blue('hey there') + on_red(' Tom!')
    >>> f[1:3] = 'ot'
    >>> f
    blue("h")+"ot"+blue(" there")+on_red(" Tom!")

You can even change their length:

    >>> f[1:3] = 'something longer'

though this will be fixed and FmtStrs won't be mutable at all due to efforts of @OufeiDong

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

2d array in which each line is a FmtStr

![fsarray example screenshot](http://i.imgur.com/rvTRPv1.png)

`Terminal`
==========

Interact with the Terminal object by passing it 2d numpy arrays of characters;
or even better, arrays of FmtStr objects! Terminal objects typically need a
TerminalController passed to them in their init methods, which sets the terminal
window up and catches input in raw mode. Context managers make it so fatal
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
                if c == "":
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
top of the 2d array end up out of view. This behavior is particularly useful for
writing command line interfaces like the REPL
[scottwasright](https://github.com/thomasballinger/scottwasright).

No Windows support currently - hoping to use [colorama](https://pypi.python.org/pypi/colorama)
for this, but currently Colorama doesn't implement many of the ANSI terminal control sequences
used by the terminal controller.
