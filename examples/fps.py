from __future__ import unicode_literals

import time

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.fmtfuncs import red, bold, green, on_blue, yellow, on_red
import curtsies.events

FPS = 15

class Frame(curtsies.events.ScheduledEvent):
    pass

reactor = Input()
schedule_next_frame = reactor.scheduled_event_trigger(Frame)
schedule_next_frame(when=time.time())
dt = float(1)/FPS
events_since_frame = []

class World(object):
    def __init__(self):
        self.s = 'Hello'
    def tick(self, events):
        self.s += '|' + ''.join(str(x) for x in events)
        self.s = self.s[max(1, len(self.s)-80):]

world = World()

with reactor:
    for e in reactor:
        if isinstance(e, Frame):
            world.tick(events_since_frame)
            del events_since_frame[:]
            print(world.s)
            when = e.when + dt
            while when < time.time():
                when += dt
            schedule_next_frame(when)
        elif e == u'<ESC>':
            break
        else:
            events_since_frame.append(e)

