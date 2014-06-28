import random

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red

def main():
    with FullscreenWindow() as window:
        print 'Press escape to exit'
        with Input() as input_generator:
            a = FSArray(window.height, window.width)
            for c in input_generator:
                if c == '<Esc>':
                    break
                row = random.choice(range(window.height))
                column = random.choice(range(window.width-len(repr(c))))
                a[row, column:column+len(repr(c))] = [repr(c)]
                window.render_to_terminal(a)

if __name__ == '__main__':
    main()
