Text objects that behave mostly like strings

fmtstr.FmtStr
-------------

    >>> fromt fmtstr.fmtstr import fmtstr
    >>> red_on_blue = fmtstr('hello', 'red', 'on_blue')
    >>> blue_on_red = fmtstr('there', fg='blue', bg='red')
    >>> green = fmtstr('!', 'green')
    >>> full = red_on_blue + ' ' + blue_on_red + green
    >>> full
    on_blue(red("hello"))+" "+on_red(blue("there"))+green("!")
    >>> str(full)
    '\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m'

and `print full` should display something like this:

<span style="color:red;"></span><span style="color:red;background-color:blue;">hello</span><span style="color:red;background-color:white;"></span><span style="color:black;background-color:white;"> </span><span style="color:blue;background-color:white;"></span><span style="color:blue;background-color:red;">there</span><span style="color:blue;background-color:white;"></span><span style="color:black;background-color:white;"></span><span style="color:green;background-color:white;">!</span><span style="color:black;background-color:white;">

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

    >>> a = FSArray(3, 14, bg='blue')
    >>> a[0:2, 5:11] = fmtstr("hey", 'on_blue') + ' ' + fmtstr('yo', 'on_red'), fmtstr('qwe qw')
    >>> a.dumb_display()

<span style="background-color:blue;">     </span><span style="background-color:white;"></span><span style="background-color:blue;">hey</span><span style="background-color:white;"> </span><span style="background-color:red;">yo</span><span style="background-color:white;"></span><span style="background-color:blue;">   </span><span style="background-color:white;">
</span><span style="background-color:blue;">     </span><span style="background-color:white;">qwe qw</span><span style="background-color:blue;">   </span><span style="background-color:white;">
</span><span style="background-color:blue;">              </span><span style="background-color:white;">

    >>> a = fsarray(['hey', 'there'], bg='cyan')
    >>> a.dumb_display()

</span><span style="background-color:teal;">hey</span><span style="background-color:white;"></span><span style="background-color:teal;">  </span><span style="background-color:white;">
</span><span style="background-color:teal;">there</span><span style="background-color:white;">
</span>

See also

* https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py
