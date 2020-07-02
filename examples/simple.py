import random

from curtsies import FullscreenWindow, Input, FSArray

def main():
    """Returns user input placed randomly on the screen"""
    with FullscreenWindow() as window:
        print('Press escape to exit')
        with Input() as input_generator:
            a = FSArray(window.height, window.width)
            for c in input_generator:
                if c == '<ESC>':
                    break
                elif c == '<SPACE>':
                    a = FSArray(window.height, window.width)
                else:
                    row = random.choice(range(window.height))
                    column = random.choice(range(window.width-len(repr(c))))
                    a[row, column:column+len(repr(c))] = [repr(c)]
                window.render_to_terminal(a)

if __name__ == '__main__':
    main()
