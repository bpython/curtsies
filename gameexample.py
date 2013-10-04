import sys

from fmtstr.fmtfuncs import red, bold, green, on_blue, yellow, on_red

from fmtstr.terminal import Terminal
from fmtstr.terminalcontrol import TerminalController
from fmtstr.fsarray import FSArray

class Entity(object):
    def __init__(self, display, x, y, speed=1):
        self.display = display
        self.x, self.y = x, y
        self.speed = speed

    def move_towards(self, entity):
        dx = entity.x - self.x
        dy = entity.y - self.y
        desired_x = dx/abs(dx) * self.speed if dx else 0
        desired_y = dy/abs(dy) * self.speed if dy else 0
        return desired_x, desired_y

class World(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Entity(on_blue(green(bold('5'))), width // 2, height // 2 - 2, speed=5)
        self.npcs = [Entity(on_blue(red('X')), i * width // 10, j * height // 10) for i in range(10) for j in range(10)]
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
            self.msg = Terminal.array_from_text_rc("try w, a, s, d, or ctrl-D", self.height, self.width)
        return self.tick()

    def tick(self):
        for npc in self.npcs:
            self.move_entity(npc, *npc.move_towards(self.player))
        for entity1 in self.entities:
            for entity2 in self.entities:
                if entity1 is entity2: continue
                if (entity1.x, entity1.y) == (entity2.x, entity2.y):
                    if entity1 is self.player:
                        return 'you lost on turn %d' % self.turn
                    entity1.speed = 0
                    entity2.speed = 0
                    entity1.display = on_red(bold(yellow('o')))
                    entity2.display = on_red(bold(yellow('o')))

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
    with TerminalController(sys.stdin, sys.stdout) as tc:
        with Terminal(tc) as t:
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
