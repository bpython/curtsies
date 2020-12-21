import itertools
import random
import time

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red

key_directions = {
                  '<UP>':   (-1, 0),
                  '<LEFT>':  (0,-1),
                  '<DOWN>':  (1, 0),
                  '<RIGHT>': (0, 1),
                 }

class Snake:
    """Creates a Snake (game) object"""
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.snake_parts = [self.random_spot()]
        self.direction = (1, 0)
        self.new_apple()

    def random_spot(self):
        """Creates a random spot for characters"""
        return random.choice(range(self.height)), random.choice(range(self.width))

    def new_apple(self):
        """Places a new apple in the window randomly for the snake to find"""
        while True:
            self.apple = self.random_spot()
            if self.apple not in self.snake_parts:
                break

    def advance_snake(self):
        """Adds to snake once it obtains an apple"""
        self.snake_parts.insert(0, (self.snake_parts[0][0]+self.direction[0], self.snake_parts[0][1]+self.direction[1]))

    def render(self):

        a = FSArray(self.height, self.width)
        for row, col in self.snake_parts:
            a[row, col] = 'x'
        a[self.apple[0], self.apple[1]] = 'o'
        return a

    def tick(self, e):
  
        if (e in key_directions and
            abs(key_directions[e][0]) + abs(self.direction[0]) < 2 and
            abs(key_directions[e][1]) + abs(self.direction[1]) < 2):
            self.direction = key_directions[e]
        self.advance_snake()
        if self.snake_parts[0] == self.apple:
            self.new_apple()
        elif ((not (0 <= self.snake_parts[0][0] < self.height and
                    0 <= self.snake_parts[0][1] < self.width)) or
                self.snake_parts[0] in self.snake_parts[1:]):
            return True
        else:
            self.snake_parts.pop()

def main():
    """Sets speed for snake and begins game upon receiving input from user"""
    MAX_FPS = 4 
    time_per_frame = lambda: 1. / MAX_FPS
    input("Press enter to start")

    with FullscreenWindow() as window:
        with Input() as input_generator:
            snake = Snake(window.height, window.width)
            while True:
                c = None
                t0 = time.time()
                while True:
                    t = time.time()
                    temp_c = input_generator.send(max(0, t - (t0 + time_per_frame())))
                    if temp_c == '<ESC>':
                        return
                    elif temp_c == '+':
                        MAX_FPS += 1
                    elif temp_c == '-':
                        MAX_FPS = max(1, MAX_FPS - 1)
                    elif temp_c is not None:
                        c = temp_c # save this keypress to be used on next tick
                    if time_per_frame() < t - t0:
                        break

                if snake.tick(c):
                    return
                window.render_to_terminal(snake.render())

if __name__ == '__main__':
    main()
