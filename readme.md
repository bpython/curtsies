Text objects that behave mostly like strings
============================================

`fmtstr` lets you work with colored strings like they are strings.
`str(yourstring)` will be the string with [ANSI escape codes]
(http://en.wikipedia.org/wiki/ANSI_escape_code)
specifying color to a terminal.

A 2d character array is also included, which allows compositing of these
formatted strings, useful for example for a terminal GUI display.

This library was created for
[scottwasright](https://github.com/thomasballinger/scottwasright),
but is probably the more reusable and useful project of the two.

fmtstr.FmtStr
-------------

![fmtstr example screenshot](http://i.imgur.com/7lFaxsz.png)

You can use convenience functions instead:

    >>> from fmtstr.fmtstr import *
    >>> blue(on_red('hey')) + " " + underline("there")

* str(FmtStr) -> escape sequence-laden text bound that looks cool in a terminal
* repr(FmtStr) -> how to create an identical FmtStr
* FmtStr[3:10] -> a new FmtStr
* FmtStr.upper (any string method) -> a new FmtStr or list of FmtStrs or int (str.count)

fmtstr.FSArray
--------------

2d array in which each line is a FmtStr

![fsarray example screenshot](http://i.imgur.com/rvTRPv1.png)

See also

* https://github.com/verigak/colors/ (`pip install colors`)
* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py (`pip install clint`)

Why this one?
=============

Other Python libraries do this, and those libraries have more tests! Why should I
use fmtstr?

FmtStr objects have multiple component strings, so one FmtStr can have several
kinds of formatting applied to different parts of it. They allow slicing and
compositing (`__getitem__` and `__setitem__`) of FmtStr objects, so can be
useful for building complexly formatted colored strings.

    >>> from fmtstr.fmtstr import *
    >>> (blue('asdf') + on_red('adsf'))[3:7]
    blue("f")+on_red("ads")
    >>> f = blue('hey there') + on_red(' Tom!')
    >>> f[1:3] = 'ot'
    >>> f
    blue("h")+"ot"+blue(" there")+on_red(" Tom!")

It's easy to turn ANSI terminal encoded strings into FmtStrs:

    >>> from fmtstr.fmtstr import *
    >>> s = str(blue('tom'))
    >>> s
    '\x1b[34mtom\x1b[39m'
    >>> FmtStr.from_str(str(blue('tom')))
    blue("tom")

And it's easy to use all sorts of string methods on a FmtStr, so you can often
use FmtStr objects where you had string in your program before:

    >>> from fmtstr.fmtstr import *
    >>> f = blue(underline('As you like it'))
    >>> len(f)  # (len(str(f) -> 32)
    14 
    >>> f == underline(blue('As you like it')) + red('')
    True
    >>> blue(', ').join(['a', red('b')])
    "a"+blue(", ")+red("b")


Using str methods on FmtStr objects
-----------------------------------

If FmtStr doesn't implement a method, it tries its best to use the string
method, which often works pretty well:

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

But formatting information will be lost if the FmtStr has different formats in
it:

    f = bold(red('hi')+' '+on_blue('there')
    >>> f.center(10)
    bold(" hi there ")
