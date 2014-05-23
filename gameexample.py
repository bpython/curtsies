import itertools
import sys

from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red

from curtsies.window import Window
from curtsies.terminal import Terminal
from curtsies.fsarray import FSArray

class Entity(object):
    def __init__(self, display, x, y, speed=1):
        self.display = display
        self.x, self.y = x, y
        self.speed = speed

    def towards(self, entity):
        dx = entity.x - self.x
        dy = entity.y - self.y
        return sign(dx) * self.speed, sign(dy) * self.speed

    def die(self):
        self.speed = 0
        self.display = on_red(bold(yellow('o')))

def sign(n):
    return -1 if n < 0 else 0 if n == 0 else 1

class World(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        n = 10
        self.player = Entity(on_blue(green(bold('5'))), width // 2, height // 2 - 2, speed=5)
        self.npcs = [Entity(on_blue(red('X')), i * width // (n * 2), j * height // (n * 2))
                     for i in range(1, 2*n, 2)
                     for j in range(1, 2*n, 2)]
        self.turn = 0

    entities = property(lambda self: self.npcs + [self.player])

    def move_entity(self, entity, dx, dy):
        entity.x = max(0, min(self.width-1, entity.x + dx))
        entity.y = max(0, min(self.height-1, entity.y + dy))

    def process_event(self, c):
        if c == "":
            sys.exit()
        elif c in ('KEY_UP', 'KEY_LEFT', 'KEY_DOWN', 'KEY_RIGHT'):
            self.move_entity(self.player, *{'KEY_UP':(0,self.player.speed),
                                            'KEY_LEFT':(-self.player.speed, 0),
                                            'KEY_DOWN':(0,-self.player.speed),
                                            'KEY_RIGHT':(self.player.speed, 0)}[c])
        else:
            self.msg = Window.array_from_text_rc("try w, a, s, d, or ctrl-D", self.height, self.width)
        return self.tick()

    def tick(self):
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
            self.player.speed = max(0, self.player.speed - 1)
            self.player.display = on_blue(green(bold(str(self.player.speed))))

    def get_array(self):
        a = FSArray(self.height, self.width, bg='blue')
        for entity in self.entities:
            a[self.height - 1 - entity.y, entity.x] = entity.display
        return a

def main():
    with Terminal(sys.stdin, sys.stdout) as tc:
        with Window(tc) as t:
            rows, columns = t.tc.get_screen_size()
            world = World(width=columns, height=rows) # note the row/column x/y swap!
            while True:
                t.render_to_terminal(world.get_array())
                c = t.tc.get_event()
                msg = world.process_event(c)
                if msg:
                    break
    print(msg)

if __name__ == '__main__':
    main()
