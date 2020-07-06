import time

from curtsies import *

def main():
    """Ideally we shouldn't lose the first second of events"""
    with Input() as input_generator:
        def extra_bytes_callback(string):
            print('got extra bytes', repr(string))
            print('type:', type(string))
            input_generator.unget_bytes(string)
        time.sleep(1)
        with CursorAwareWindow(extra_bytes_callback=extra_bytes_callback) as window:
            window.get_cursor_position()
            for e in input_generator:
                print(repr(e))
                if e == '<ESC>':
                    break

if __name__ == '__main__':
    main()
