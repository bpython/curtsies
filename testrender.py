import sys

from fmtstr.fmtfuncs import blue, red, bold, on_red

from fmtstr.terminal import Terminal
from fmtstr.terminalcontrol import TerminalController

import time

if __name__ == '__main__':

    print(blue('hey') + ' ' + red('there') + ' ' + red(bold('you')))

    with TerminalController(sys.stdin, sys.stdout) as tc:
        with Terminal(tc) as t:
            rows, columns = t.tc.get_screen_size()
            t0 = time.time()
            for i in range(100):
                a = [blue(on_red('qwertyuiop'[i%10]*columns)) for _ in range(rows)]
                t.render_to_terminal(a)
            t1 = time.time()

print t1 - t0


