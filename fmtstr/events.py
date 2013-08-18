"""Language for describing events that in terminal"""
import threading
class Event(object):
    pass

class RefreshRequestEvent(Event):
    def __init__(self):
        self.who = threading.currentThread()
    def __repr__(self):
        return "<RefreshRequestEvent from %r>" % (self.who)

class WindowChangeEvent(Event):
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
    x = width = property(lambda self: self.columns)
    y = height = property(lambda self: self.rows)
    def __repr__(self):
        return "<WindowChangeEvent (%d, %d)>" % (self.rows, self.columns)

class Keypress(Event):
    __slots__ = ['name', 'seq']
    def __init__(self, name, seq):
        self.seq = seq
        self.name = name
    def __repr__(self, seq):
        return "<Key %r>" % self.seq
