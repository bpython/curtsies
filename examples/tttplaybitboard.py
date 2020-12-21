#!/usr/bin/env python
"""
Adapted from https://github.com/darius/circuitexpress/blob/master/sketchpad/tttplaybitboard.py

Super-fancy console tic-tac-toe.
Derived from tttplay.py
Bitboards from https://gist.github.com/pnf/5924614
grid_format from https://github.com/gigamonkey/gigamonkey-tic-tac-toe/blob/master/search.py
"""

import sys

from curtsies.fmtfuncs import * # XXX boo hiss *

from curtsies import FullscreenWindow, Input, fsarray

def main(argv):
    pool = {name[:-5]: play for name, play in globals().items()
                if name.endswith('_play')}
    faceoff = [human_play, max_play]
    try:
        if len(argv) == 1:
            pass
        elif len(argv) == 2:
            faceoff[1] = pool[argv[1]]
        elif len(argv) == 3:
            faceoff = [pool[argv[1]], pool[argv[2]]]
        else:
            raise KeyError
    except KeyError:
        print("Usage: %s [player] [player]" % argv[0])
        print("where a player is one of:", ', '.join(sorted(pool)))
        return 1
    else:
        with Input() as i:
            with FullscreenWindow() as w:
                tictactoe(w, i, *faceoff)
        return 0

def tictactoe(w, i, player, opponent, grid=None):
    "Put two strategies to a classic battle of wits."
    grid = grid or empty_grid
    while True:
        w.render_to_terminal(w.array_from_text(view(grid)))
        if is_won(grid):
            print(whose_move(grid), "wins.")
            break
        if not successors(grid):
            print("A draw.")
            break
        grid = player(w, i, grid)
        player, opponent = opponent, player


# Utilities

def average(ns):
    return float(sum(ns)) / len(ns)

def memo(f):
    "Return a function like f that remembers and reuses results of past calls."
    table = {}
    def memo_f(*args):
        try:
            return table[args]
        except KeyError:
            table[args] = value = f(*args)
            return value
    return memo_f


# Strategies. They all presume the game's not over.

def human_play(w, i, grid):
    "Just ask for a move."
    plaint = ''
    prompt = whose_move(grid) + " move? [1-9] "
    while True:
        w.render_to_terminal(w.array_from_text(view(grid)
                                               + '\n\n' + plaint + prompt))
        key = c = i.next()
        try:
            move = int(key)
        except ValueError:
            pass
        else:
            if 1 <= move <= 9:
                successor = apply_move(grid, from_human_move(move))
                if successor: return successor
        plaint = ("Hey, that's illegal. Give me one of these digits:\n\n"
                  + (grid_format
                     % tuple(move if apply_move(grid, from_human_move(move)) else '-'
                             for move in range(1, 10))
                     + '\n\n'))

grid_format = '\n'.join([' %s %s %s'] * 3)

def drunk_play(w, i, grid):
    "Beatable, but not so stupid it seems mindless."
    return min(successors(grid), key=drunk_value)

def spock_play(w, i, grid):
    "Play supposing both players are rational."
    return min(successors(grid), key=evaluate)

def max_play(w, i, grid):
    "Play like Spock, except breaking ties by drunk_value."
    return min(successors(grid),
               key=lambda succ: (evaluate(succ), drunk_value(succ)))

@memo
def drunk_value(grid):
    "Return the expected value to the player if both players play at random."
    if is_won(grid): return -1
    succs = successors(grid)
    return -average(map(drunk_value, succs)) if succs else 0

@memo
def evaluate(grid):
    "Return the value for the player to move, assuming perfect play."
    if is_won(grid): return -1
    succs = successors(grid)
    return -min(map(evaluate, succs)) if succs else 0


# We represent a tic-tac-toe grid as a pair of bit-vectors (p, q), p
# for the player to move, q for their opponent. So p has 9
# bit-positions, one for each square in the grid, with a 1 in the
# positions where the player has already moved; and likewise for the
# other player's moves in q. The least significant bit is the
# lower-right square; the most significant is upper-left.

# (Some scaffolding to view examples inline, below:)
## def multiview(grids): print('\n'.join(reduce(beside, [view(g).split('\n') for g in grids])), end=" ")
## def beside(block1, block2): return map('  '.join, zip(block1, block2))

empty_grid = 0, 0

def is_won(grid):
    "Did the latest move win the game?"
    p, q = grid
    return any(way == (way & q) for way in ways_to_win)

# Numbers starting with 0 are in octal: 3 bits/digit, thus one row per digit.
ways_to_win = (0o700, 0o070, 0o007, 0o444, 0o222, 0o111, 0o421, 0o124)

## multiview((0, way) for way in ways_to_win)
#.  X X X   . . .   . . .   X . .   . X .   . . X   X . .   . . X
#.  . . .   X X X   . . .   X . .   . X .   . . X   . X .   . X .
#.  . . .   . . .   X X X   X . .   . X .   . . X   . . X   X . .

def successors(grid):
    "Return the possible grids resulting from p's moves."
    return filter(None, (apply_move(grid, move) for move in range(9)))

## multiview(successors(empty_grid))
#.  . . .   . . .   . . .   . . .   . . .   . . .   . . X   . X .   X . .
#.  . . .   . . .   . . .   . . X   . X .   X . .   . . .   . . .   . . .
#.  . . X   . X .   X . .   . . .   . . .   . . .   . . .   . . .   . . .

def apply_move(grid, move):
    "Try to move: return a new grid, or None if illegal."
    p, q = grid
    bit = 1 << move
    return (q, p | bit) if 0 == (bit & (p | q)) else None

## example = ((0112, 0221))
## multiview([example, apply_move(example, 2)])
#.  . O X   . O X
#.  . O X   . O X
#.  . X O   X X O

def from_human_move(n):
    "Convert from a move numbered 1..9 in top-left..bottom-right order."
    return 9 - n

def whose_move(grid):
    "Return the mark of the player to move."
    return player_marks(grid)[0]

def player_marks(grid):
    "Return two results: the player's mark and their opponent's."
    p, q = grid
    return 'XO' if sum(player_bits(p)) == sum(player_bits(q)) else 'OX'

def player_bits(bits):
    return ((bits >> i) & 1 for i in reversed(range(9)))

def view(grid):
    "Show a grid human-readably."
    p_mark, q_mark = player_marks(grid)
    return grid_format % tuple(p_mark if by_p else q_mark if by_q else '.'
                               for by_p, by_q in zip(*map(player_bits, grid)))

# Starting from this board:
## print(view((0610, 0061)), end="")
#.  X X .
#.  O O X
#.  . . O

# Spock examines these choices:
## multiview(successors((0610, 0061)))
#.  X X .   X X .   X X X
#.  O O X   O O X   O O X
#.  . X O   X . O   . . O

# and picks the win:
## print(view(spock_play((0610, 0061))), end="")
#.  X X X
#.  O O X
#.  . . O

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
