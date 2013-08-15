Text objects that behave mostly like strings

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

* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py
