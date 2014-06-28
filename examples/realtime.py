import itertools
import random
import time

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red

MAX_FPS = 1000
time_per_frame = 1. / MAX_FPS

class FrameCounter(object):
    def __init__(self):
        self.render_times = []
        self.dt = .5
    def frame(self):
        self.render_times.append(time.time())
    def fps(self):
        now = time.time()
        while self.render_times and self.render_times[0] < now - self.dt:
            self.render_times.pop(0)
        return len(self.render_times) / max(self.dt, now - self.render_times[0] if self.render_times else self.dt)

def main():
    counter = FrameCounter()
    with FullscreenWindow() as window:
        print('Press escape to exit')
        with Input() as input_generator:
            a = FSArray(window.height, window.width)
            c = None
            for framenum in itertools.count(0):
                t0 = time.time()
                while True:
                    t = time.time()

                    temp_c = input_generator.send(max(0, t - (t0 + time_per_frame)))
                    if temp_c is not None:
                        c = temp_c

                    if c is None:
                        pass
                    elif c == '<ESC>':
                        return
                    elif c == '<SPACE>':
                        a = FSArray(window.height, window.width)
                    else:
                        row = random.choice(range(window.height))
                        column = random.choice(range(window.width-len(c)))
                        a[row:row+1, column:column+len(c)] = [c]

                    c = None
                    if time_per_frame < t - t0:
                        break

                row = random.choice(range(window.height))
                column = random.choice(range(window.width))
                a[row:row+1, column:column+1] = [random.choice(".,-'`~")]

                fps = 'FPS: %.1f' % counter.fps()
                a[0:1, 0:len(fps)] = [fps]

                window.render_to_terminal(a)
                counter.frame()

if __name__ == '__main__':
    main()
