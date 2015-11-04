"""Events for keystrokes and other input events"""
import sys
import time
import encodings
from functools import wraps

PY3 = sys.version_info[0] >= 3

if PY3:
    raw_input = input
    unicode = str

chr_byte = lambda i: chr(i).encode('latin-1') if PY3 else chr(i)
chr_uni  = lambda i: chr(i) if PY3 else chr(i).decode('latin-1')

CURTSIES_NAMES = {}
control_chars = dict((chr_byte(i), u'<Ctrl-%s>' % chr(i + 0x60)) for i in range(0x00, 0x1b))
CURTSIES_NAMES.update(control_chars)
for i in range(0x00, 0x80):
    CURTSIES_NAMES[b'\x1b'+chr_byte(i)] = u'<Esc+%s>' % chr(i)
for i in range(0x00, 0x1b): # Overwrite the control keys with better labels
    CURTSIES_NAMES[b'\x1b'+chr_byte(i)] = u'<Esc+Ctrl-%s>' % chr(i + 0x40)
for i in range(0x00, 0x80):
    CURTSIES_NAMES[chr_byte(i + 0x80)] = u'<Meta-%s>' % chr(i)
for i in range(0x00, 0x1b): # Overwrite the control keys with better labels
    CURTSIES_NAMES[chr_byte(i + 0x80)] = u'<Meta-Ctrl-%s>' % chr(i + 0x40)

from .curtsieskeys import CURTSIES_NAMES as special_curtsies_names
CURTSIES_NAMES.update(special_curtsies_names)

CURSES_NAMES = {}
CURSES_NAMES[b'\x1bOP'] = u'KEY_F(1)'
CURSES_NAMES[b'\x1bOQ'] = u'KEY_F(2)'
CURSES_NAMES[b'\x1bOR'] = u'KEY_F(3)'
CURSES_NAMES[b'\x1bOS'] = u'KEY_F(4)'
CURSES_NAMES[b'\x1b[15~'] = u'KEY_F(5)'
CURSES_NAMES[b'\x1b[17~'] = u'KEY_F(6)'
CURSES_NAMES[b'\x1b[18~'] = u'KEY_F(7)'
CURSES_NAMES[b'\x1b[19~'] = u'KEY_F(8)'
CURSES_NAMES[b'\x1b[20~'] = u'KEY_F(9)'
CURSES_NAMES[b'\x1b[21~'] = u'KEY_F(10)'
CURSES_NAMES[b'\x1b[23~'] = u'KEY_F(11)'
CURSES_NAMES[b'\x1b[24~'] = u'KEY_F(12)'
CURSES_NAMES[b'\x1b[A'] = u'KEY_UP'
CURSES_NAMES[b'\x1b[B'] = u'KEY_DOWN'
CURSES_NAMES[b'\x1b[C'] = u'KEY_RIGHT'
CURSES_NAMES[b'\x1b[D'] = u'KEY_LEFT'
CURSES_NAMES[b'\x08'] = u'KEY_BACKSPACE'
CURSES_NAMES[b'\x1b[Z'] = u'KEY_BTAB'

# see curtsies #78 - taken from https://github.com/jquast/blessed/blob/e9ad7b85dfcbbba49010ab8c13e3a5920d81b010/blessed/keyboard.py#L409
CURSES_NAMES[b'\x1b[1~'] = u'KEY_FIND'         # find
CURSES_NAMES[b'\x1b[2~'] = u'KEY_IC'           # insert (0)
CURSES_NAMES[b'\x1b[3~'] = u'KEY_DC'           # delete (.), "Execute"
CURSES_NAMES[b'\x1b[4~'] = u'KEY_SELECT'       # select
CURSES_NAMES[b'\x1b[5~'] = u'KEY_PPAGE'        # pgup   (9)
CURSES_NAMES[b'\x1b[6~'] = u'KEY_NPAGE'        # pgdown (3)
CURSES_NAMES[b'\x1b[7~'] = u'KEY_HOME'         # home
CURSES_NAMES[b'\x1b[8~'] = u'KEY_END'          # end
CURSES_NAMES[b'\x1b[OA'] = u'KEY_UP'           # up     (8)
CURSES_NAMES[b'\x1b[OB'] = u'KEY_DOWN'         # down   (2)
CURSES_NAMES[b'\x1b[OC'] = u'KEY_RIGHT'        # right  (6)
CURSES_NAMES[b'\x1b[OD'] = u'KEY_LEFT'         # left   (4)
CURSES_NAMES[b'\x1b[OF'] = u'KEY_END'          # end    (1)
CURSES_NAMES[b'\x1b[OH'] = u'KEY_HOME'         # home   (7)

class Event(object):
    pass

class ScheduledEvent(Event):
    """Event scheduled for a future time.

    args:
        when (float): unix time in seconds for which this event is scheduled

    Custom events that occur at a specific time in the future should
    be subclassed from ScheduledEvent."""
    def __init__(self, when):
        self.when = when

class WindowChangeEvent(Event):
    def __init__(self, rows, columns, cursor_dy=None):
        self.rows = rows
        self.columns = columns
        self.cursor_dy = cursor_dy
    x = width = property(lambda self: self.columns)
    y = height = property(lambda self: self.rows)
    def __repr__(self):
        return "<WindowChangeEvent (%d, %d)%s>" % (self.rows, self.columns,
                '' if self.cursor_dy is None else " cursor_dy: %d" % self.cursor_dy)
    @property
    def name(self):
        return '<WindowChangeEvent>'

class SigIntEvent(Event):
    """Event signifying a SIGINT"""
    def __repr__(self):
        return "<SigInt Event>"
    @property
    def name(self):
        return repr(self)

class PasteEvent(Event):
    """Multiple keypress events combined, likely from copy/paste.

    The events attribute contains a list of keypress event strings.
    """
    def __init__(self):
        self.events = []
    def __repr__(self):
        return "<Paste Event with data: %r>" % self.events
    @property
    def name(self):
        return repr(self)

def pp_event(seq):
    """Returns pretty representation of an Event or keypress"""

    if isinstance(seq, Event):
        return str(seq)

    # Get the original sequence back if seq is a pretty name already
    rev_curses = dict((v, k) for k, v in CURSES_NAMES.items())
    rev_curtsies = dict((v, k) for k, v in CURTSIES_NAMES.items())
    if seq in rev_curses:
        seq = rev_curses[seq]
    elif seq in rev_curtsies:
        seq = rev_curtsies[seq]

    pretty = curtsies_name(seq)
    if pretty != seq:
        return pretty
    return repr(seq).lstrip('u')[1:-1]

def curtsies_name(seq):
    return CURTSIES_NAMES.get(seq, seq)
