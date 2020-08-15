import sys

from curtsies.fmtfuncs import *
from curtsies import FullscreenWindow, Input, fsarray

class Board(object):
    """
    >>> Board().rows
    ((' ', ' ', ' '), (' ', ' ', ' '), (' ', ' ', ' '))
    >>> Board().columns
    ((' ', ' ', ' '), (' ', ' ', ' '), (' ', ' ', ' '))
    >>> Board().turn
    0
    >>> Board().whose_turn
    'x'
    >>> b = Board().move(2); print(b)
     | |x
    -----
     | | 
    -----
     | | 
    >>> b.possible()
    [< Board |o.x......| >, < Board |.ox......| >, < Board |..xo.....| >, < Board |..x.o....| >, < Board |..x..o...| >, < Board |..x...o..| >, < Board |..x....o.| >, < Board |..x.....o| >]
    """
    def __init__(self, width=3, height=3):
        self._rows = [[' ' for _ in range(width)] for _ in range(height)]

    rows = property(lambda self: tuple(tuple(row) for row in self._rows))
    columns = property(lambda self: tuple(zip(*self._rows)))
    spots = property(lambda self: tuple(c for row in self._rows for c in row))
    def __str__(self):
        return ('\n'+'-'*(len(self.columns)*2-1) + '\n').join(['|'.join(row) for row in self._rows])
    def __repr__(self): return '< Board |'+''.join(self.spots).replace(' ','.')+'| >'
    @property
    def turn(self):
        return 9 - self.spots.count(' ')
    @property
    def whose_turn(self):
        return 'xo'[self.turn % 2]
    def winner(self):
        """Returns either x or o if one of them won, otherwise None"""
        for c in 'xo':
            for comb in [(0,3,6), (1,4,7), (2,5,8), (0,1,2), (3,4,5), (6,7,8), (0,4,8), (2,4,6)]:
                if all(self.spots[p] == c for p in comb):
                    return c
        return None
    def move(self, pos):
        if not self.spots[pos] == ' ': raise ValueError('That spot it taken')
        new = Board(len(self.rows), len(self.columns))
        new._rows = list(list(row) for row in self.rows)
        new._rows[pos // 3][pos % 3] = self.whose_turn
        return new
    def possible(self):
        return [self.move(p) for p in range(len(self.spots)) if self.spots[p] == ' ']
    def display(self):
        colored = {' ':' ', 'x':blue(bold('x')), 'o':red(bold('o'))}
        s = ('\n'+green('-')*(len(self.columns)*2-1) + '\n').join([green('|').join(colored[mark] for mark in row) for row in self._rows])
        a = fsarray([bold(green('enter a number, 0-8' if self.whose_turn == 'x' else 'wait for computer...'))] + s.split('\n'))
        return a

def opp(c):
    """
    >>> opp('x'), opp('o')
    ('o', 'x')
    """
    return 'x' if c == 'o' else 'o'

def value(board, who='x'):
    """Returns the value of a board
    >>> b = Board(); b._rows = [['x', 'x', 'x'], ['x', 'x', 'x'], ['x', 'x', 'x']]
    >>> value(b)
    1
    >>> b = Board(); b._rows = [['o', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'o']]
    >>> value(b)
    -1
    >>> b = Board(); b._rows = [['x', 'o', ' '], ['x', 'o', ' '], [' ', ' ', ' ']]
    >>> value(b)
    1
    >>> b._rows[0][2] = 'x'
    >>> value(b)
    -1
    """
    w = board.winner()
    if w == who:
        return 1
    if w == opp(who):
        return -1
    if board.turn == 9:
        return 0

    if who == board.whose_turn:
        return max([value(b, who) for b in board.possible()])
    else:
        return min([value(b, who) for b in board.possible()])

def ai(board, who='x'):
    """
    Returns best next board

    >>> b = Board(); b._rows = [['x', 'o', ' '], ['x', 'o', ' '], [' ', ' ', ' ']]
    >>> ai(b)
    < Board |xo.xo.x..| >
    """
    return sorted(board.possible(), key=lambda b: value(b, who))[-1]

def main():
    with Input() as input:
        with FullscreenWindow() as window:
            b = Board()
            while True:
                window.render_to_terminal(b.display())
                if b.turn == 9 or b.winner():
                    c = input.next() # hit any key
                    sys.exit()
                while True:
                    c = input.next()
                    if c == '':
                        sys.exit()
                    try:
                        if int(c) in range(9):
                            b = b.move(int(c))
                    except ValueError:
                        continue
                    window.render_to_terminal(b.display())
                    break
                if b.turn == 9 or b.winner():
                    c = input.next() # hit any key
                    sys.exit()
                b = ai(b, 'o')

if __name__ == '__main__':
    main()
