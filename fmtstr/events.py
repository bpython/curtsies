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
    @property
    def name(self):
        return '<WindowChangeEvent>'

def get_key(chars, use_curses_name=True):
    if not ((chars and chars[0] != '\x1b') or
            (len(chars) == 2 and chars[1] not in ['[', 'O', '\x1b']) or
            (len(chars) == 4 and chars[1] == '\x1b' and chars[2] == '[') or
            (len(chars) > 2 and chars[1] in ['[', 'O'] and chars[-1] not in tuple('1234567890;'))):
        return None
    try:
        u = ''.join(chars).decode('utf8')
    except UnicodeDecodeError:
        return None
    return curses_name(u)

def pp_event(seq):
    """Returns pretty version of an Event or keypress"""

    if isinstance(seq, Event):
        return str(seq)

    if seq in REVERSE_CURSES:
        seq = REVERSE_CURSES[seq]

    if seq in SEQUENCE_NAMES:
        return SEQUENCE_NAMES[seq]
    if len(seq) == 1 and '\x00' < seq < '\x1a':
        return '<Ctrl-%s>' % chr(ord(seq) + 0x60)
    if len(seq) == 2 and seq[0] == '\x1b':
        if '\x00' < seq[1] < '\x1a':
            return '<Ctrl-Meta-%s>' % chr(ord(seq[1]) + 0x60)
        return '<Meta-%s>' % seq[1]
    if seq[0] == '':
        pass
    return repr(seq)[2:-1]

def curses_name(seq):
    return CURSES_TABLE.get(seq, seq)

# the first one is the canonical name, the rest are used for equivalence
SEQUENCE_NAMES = dict([
  (' ',        '<SPACE>'),
  ('\x1b ',    '<Meta-SPACE>'),
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
  ('\x00', '<Ctrl-SPACE>'),
  ('\x1c', r'<Ctrl-\>'),
  ('\x1d', '<Ctrl-]>'),
  ('\x1e', '<Ctrl-6>'),
  ('\x1f', '<Ctrl-/>'),
  ('\x7f', '<DELETE>'),
  ('\x1b\x7f', '<Meta-DELETE>'),
  ])

CURSES_TABLE = {}
CURSES_TABLE['\x1b[15~'] = 'KEY_F(5)'
CURSES_TABLE['\x1b[17~'] = 'KEY_F(6)'
CURSES_TABLE['\x1b[18~'] = 'KEY_F(7)'
CURSES_TABLE['\x1b[19~'] = 'KEY_F(8)'
CURSES_TABLE['\x1b[20~'] = 'KEY_F(9)'
CURSES_TABLE['\x1b[21~'] = 'KEY_F(10)'
CURSES_TABLE['\x1b[23~'] = 'KEY_F(11)'
CURSES_TABLE['\x1b[24~'] = 'KEY_F(12)'
CURSES_TABLE['\x1b[A'] = 'KEY_UP'
CURSES_TABLE['\x1b[B'] = 'KEY_DOWN'
CURSES_TABLE['\x1b[C'] = 'KEY_RIGHT'
CURSES_TABLE['\x1b[D'] = 'KEY_LEFT'
CURSES_TABLE['\x08'] = 'KEY_BACKSPACE'
CURSES_TABLE['\x1b[3~'] = 'KEY_DC'
CURSES_TABLE['\x1b[5~'] = 'KEY_PPAGE'
CURSES_TABLE['\x1b[6~'] = 'KEY_NPAGE'
#TODO add home and end? and everything else

REVERSE_CURSES = dict((v, k) for k, v in CURSES_TABLE.items())
