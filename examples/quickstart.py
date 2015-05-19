from __future__ import unicode_literals # convenient for Python 2
import random

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow

print(yellow('this prints normally, not to the alternate screen'))
with FullscreenWindow() as window:
    with Input() as input_generator:
        msg = red(on_blue(bold('Press escape to exit')))
        a = FSArray(window.height, window.width)
        a[0:1, 0:msg.width] = [msg]
        window.render_to_terminal(a)
        for c in input_generator:
            if c == '<ESC>':
                break
            elif c == '<SPACE>':
                a = FSArray(window.height, window.width)
            else:
                s = repr(c)
                row = random.choice(range(window.height))
                column = random.choice(range(window.width-len(s)))
                color = random.choice([red, green, on_blue, yellow])
                a[row, column:column+len(s)] = [color(s)]
            window.render_to_terminal(a)
