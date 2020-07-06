import time

from curtsies.input import *

def main():
    """Ideally we shouldn't lose the first second of events"""
    time.sleep(1)
    with Input() as input_generator:
        for e in input_generator:
            print(repr(e))
            if e == '<ESC>':
                break
if __name__ == '__main__':
    main()
