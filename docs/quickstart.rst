Quickstart
*****************
Curtsies is a library for interacting with the terminal.
It does colored strings, grids of formatted characters fit
for display in a terminal, rendering to the terminal and keyboard input.

This is what using (nearly every feature of) curtsies looks like::

    import random

    from curtsies import FullscreenWindow, Input, FSArray
    from curtsies.fmtfuncs import red, bold, green, on_blue, yellow

    print yellow('this prints normally, not to the alternate screen')
    with FullscreenWindow() as window:
        print(red(on_blue(bold('Press escape to exit'))))
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
                    color = random.choice([red, green, on_blue, yellow])
                    a[row, column:column+len(repr(c))] = [color(repr(c))]
                window.render_to_terminal(a)

Paste it into a file to try it out!
