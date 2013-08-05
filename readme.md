Text objects that behave mostly like strings

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
