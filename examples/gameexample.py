from __future__ import unicode_literals

import itertools
import sys

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red

class Entity(object):
    def __init__(self, display, x, y, speed=1):
        self.display = display
        self.x, self.y = x, y
        self.speed = speed

    def towards(self, entity):
        dx = entity.x - self.x
        dy = entity.y - self.y
        return vscale(self.speed, (sign(dx), sign(dy)))

    def die(self):
        self.speed = 0
        self.display = on_red(bold(yellow('o')))

def sign(n):
    return -1 if n < 0 else 0 if n == 0 else 1

def vscale(c, v):
    return tuple(c*x for x in v)

class World(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        n = 5
        self.player = Entity(on_blue(green(bold(u'5'))), width // 2, height // 2 - 2, speed=5)
        self.npcs = [Entity(on_blue(red(u'X')), i * width // (n * 2), j * height // (n * 2))
                     for i in range(1, 2*n, 2)
                     for j in range(1, 2*n, 2)]
        self.turn = 0

    entities = property(lambda self: self.npcs + [self.player])

    def move_entity(self, entity, dx, dy):
        entity.x = max(0, min(self.width-1, entity.x + dx))
        entity.y = max(0, min(self.height-1, entity.y + dy))

    def process_event(self, c):
        """Returns a message from tick() to be displayed if game is over"""
        if c == "":
            sys.exit()
        elif c in key_directions:
            self.move_entity(self.player, *vscale(self.player.speed, key_directions[c]))
        else:
            return "try arrow keys, w, a, s, d, or ctrl-D (you pressed %r)" % c
        return self.tick()

    def tick(self):
        """Returns a message to be displayed if game is over, else None"""
        for npc in self.npcs:
            self.move_entity(npc, *npc.towards(self.player))
        for entity1, entity2 in itertools.combinations(self.entities, 2):
            if (entity1.x, entity1.y) == (entity2.x, entity2.y):
                if self.player in (entity1, entity2):
                    return 'you lost on turn %d' % self.turn
                entity1.die()
                entity2.die()

        if all(npc.speed == 0 for npc in self.npcs):
            return 'you won on turn %d' % self.turn
        self.turn += 1
        if self.turn % 20 == 0:
            self.player.speed = max(1, self.player.speed - 1)
            self.player.display = on_blue(green(bold(str(self.player.speed).decode('utf8'))))

    def get_array(self):
        a = FSArray(self.height, self.width)
        for entity in self.entities:
            a[self.height - 1 - entity.y, entity.x] = entity.display
        return a

key_directions = {'<UP>':    (0, 1),
                  '<LEFT>': (-1, 0),
                  '<DOWN>':  (0,-1),
                  '<RIGHT>': (1, 0),
                  'w':       (0, 1),
                  'a':       (-1, 0),
                  's':       (0,-1),
                  'd':       (1, 0)}

def main():
    with FullscreenWindow(sys.stdout) as window:
        with Input(sys.stdin) as input_generator:
            world = World(width=window.width, height=window.height)
            window.render_to_terminal(world.get_array())
            for c in input_generator:
                msg = world.process_event(c)
                if msg:
                    break
                window.render_to_terminal(world.get_array())
    print(msg)

if __name__ == '__main__':
    main()
