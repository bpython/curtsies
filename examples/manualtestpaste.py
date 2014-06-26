import sys

from curtsies.terminal import Terminal
from curtsies.events import PasteEvent

def main():
    with Terminal(sys.stdin, sys.stdout, paste_mode=True) as tc:
        while True:
            e = tc.get_event()
            if isinstance(e, PasteEvent):
                print('PasteEvent!', repr(e.events))
            else:
                print('other event', e)
            if e == '':
                return


if __name__ == '__main__':
    main()
