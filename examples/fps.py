import time

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red
import curtsies.events

class Frame(curtsies.events.ScheduledEvent):
    pass

class World:
    def __init__(self):
        self.s = 'Hello'
    def tick(self):
        self.s += '|'
        self.s = self.s[max(1, len(self.s)-80):]
    def process_event(self, e):
        self.s += str(e)

def realtime(fps=15):
    world = World()
    dt = 1/fps

    reactor = Input()
    schedule_next_frame = reactor.scheduled_event_trigger(Frame)
    schedule_next_frame(when=time.time())

    with reactor:
        for e in reactor:
            if isinstance(e, Frame):
                world.tick()
                print(world.s)
                when = e.when + dt
                while when < time.time():
                    when += dt
                schedule_next_frame(when)
            elif e == '<ESC>':
                break
            else:
                world.process_event(e)

if __name__ == "__main__":
    realtime()
