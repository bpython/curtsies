"""Language for describing events that in terminal"""
import sys

PY3 = sys.version_info[0] >= 3

class Event(object):
    pass

class RefreshRequestEvent(Event):
    def __init__(self, who='?'):
        self.who = who
    def __repr__(self):
        return "<RefreshRequestEvent from %r>" % (self.who)

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
    def __repr__(self):
        return "<SigInt Event>"
    @property
    def name(self):
        return repr(self)

class PasteEvent(Event):
    def __init__(self):
        self.events = []
    def __repr__(self):
        return "<Paste Event with data: %r>" % self.events
    @property
    def name(self):
        return repr(self)

def get_key(chars, keynames='curses'):
    if not ((chars and chars[0] != '\x1b') or
            (len(chars) == 2 and chars[1] not in ['[', 'O', '\x1b']) or
            (len(chars) == 4 and chars[1] == '\x1b' and chars[2] == '[') or
            (len(chars) > 2 and chars[1] in ['[', 'O'] and chars[-1] not in tuple('1234567890;'))):
        return None
    if PY3:
        try:
            u = ''.join(chars)
        except UnicodeDecodeError:
            return None
    else:
        chars = ''.join(chars)
        try:
            u = chars.decode('utf8')
        except UnicodeDecodeError:
            return None
    if keynames == 'curses':
        return curses_name(u)
    elif keynames == 'curtsies':
        return curtsies_name(u)
    elif keynames is None or keynames == 'plain':
        return u
    else:
        raise ValueError('keyname must but one of "curtsies", "curses"')

def pp_event(seq):
    """Returns pretty representation of an Event or keypress"""

    if isinstance(seq, Event):
        return str(seq)

    if seq in REVERSE_CURSES:
        seq = REVERSE_CURSES[seq]

    fsname = curtsies_name(seq)
    if fsname != seq:
        return fsname
    return repr(seq)[2:-1]

def curtsies_name(seq):
    if isinstance(seq, Event):
        return seq

    if seq in SEQUENCE_NAMES:
        return SEQUENCE_NAMES[seq]
    if len(seq) == 1 and '\x00' < seq < '\x1a':
        return '<Ctrl-%s>' % chr(ord(seq) + 0x60)
    if len(seq) == 2 and seq[0] == '\x1b':
        if '\x00' < seq[1] < '\x1a':
            return '<Ctrl-Meta-%s>' % chr(ord(seq[1]) + 0x60)
        return '<Meta-%s>' % seq[1]
    return seq

def curses_name(seq):
    return CURSES_NAMES.get(seq, seq)

# the first one is the canonical name, the second is the pretty str
SEQUENCE_NAMES = dict([
  (' ',        '<SPACE>'),
  ('\x1b ',    '<Meta-SPACE>'),
  ('\t',       '<TAB>'),
  ('\x1b[Z',   '<Shift-TAB>'),
  ('\r',       '<RETURN>'),
  ('\n',       '<RETURN>'),
  ('\x1b[A',   '<UP>'),
  ('\x1b[B',   '<DOWN>'),
  ('\x1b[C',   '<RIGHT>'),
  ('\x1b[D',   '<LEFT>'),
  ('\x1bOP',   '<F1>'),
  ('\x1bOQ',   '<F2>'),
  ('\x1bOR',   '<F3>'),
  ('\x1bOS',   '<F4>'),
  ('\x1b[15~', '<F5>'),
  ('\x1b[17~', '<F6>'),
  ('\x1b[18~', '<F7>'),
  ('\x1b[19~', '<F8>'),
  ('\x1b[20~', '<F9>'),
  ('\x1b[21~', '<F10>'),
  ('\x1b[23~', '<F11>'),
  ('\x1b[24~', '<F12>'),
  ('\x1b\x7f', '<Meta-DELETE>'),
# Until I understand how universal these are, I'm putting in the keys from
# my American macbook air with macos with US Qwerty layout
# Mac terminal binds option left and right keys to meta - b & f 
  ('\x00', '<Ctrl-SPACE>'),
  ('\x1c', r'<Ctrl-\>'),
  ('\x1d', '<Ctrl-]>'),
  ('\x1e', '<Ctrl-6>'),
  ('\x1f', '<Ctrl-/>'),
  ('\x7f', '<DELETE>'),
  ('\x1b\x7f', '<Meta-DELETE>'),
  ('\xff', '<Meta-DELETE>'),
  ('\x1b\x1b[A',   '<Meta-UP>'),
  ('\x1b\x1b[B',   '<Meta-DOWN>'),
  ('\x1b\x1b[C',   '<Meta-RIGHT>'),
  ('\x1b\x1b[D',   '<Meta-LEFT>'),
  ])

CURSES_NAMES = {}
CURSES_NAMES['\x1b[15~'] = 'KEY_F(5)'
CURSES_NAMES['\x1b[17~'] = 'KEY_F(6)'
CURSES_NAMES['\x1b[18~'] = 'KEY_F(7)'
CURSES_NAMES['\x1b[19~'] = 'KEY_F(8)'
CURSES_NAMES['\x1b[20~'] = 'KEY_F(9)'
CURSES_NAMES['\x1b[21~'] = 'KEY_F(10)'
CURSES_NAMES['\x1b[23~'] = 'KEY_F(11)'
CURSES_NAMES['\x1b[24~'] = 'KEY_F(12)'
CURSES_NAMES['\x1b[A'] = 'KEY_UP'
CURSES_NAMES['\x1b[B'] = 'KEY_DOWN'
CURSES_NAMES['\x1b[C'] = 'KEY_RIGHT'
CURSES_NAMES['\x1b[D'] = 'KEY_LEFT'
CURSES_NAMES['\x08'] = 'KEY_BACKSPACE'
CURSES_NAMES['\x1b[3~'] = 'KEY_DC'
CURSES_NAMES['\x1b[5~'] = 'KEY_PPAGE'
CURSES_NAMES['\x1b[6~'] = 'KEY_NPAGE'
CURSES_NAMES['\x1b[Z'] = 'KEY_BTAB'
#TODO add home and end? and everything else

REVERSE_CURSES = dict((v, k) for k, v in CURSES_NAMES.items())
