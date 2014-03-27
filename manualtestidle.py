import sys

from curtsies.terminal import Terminal
from curtsies.events import PasteEvent

import time

def idle():
    i = 0
    while True:
        print i
        time.sleep(.1)
        i += 1
        yield

def main():
    i = idle()
    with Terminal(sys.stdin, sys.stdout, paste_mode=True) as tc:
        while True:
            e = tc.get_event(idle=i)
            if isinstance(e, PasteEvent):
                print('PasteEvent!', repr(e.events))
            else:
                print('other event', e)
            if e == '':
                return


if __name__ == '__main__':
    main()
