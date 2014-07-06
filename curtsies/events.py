"""Events for keystrokes and other input events"""
import sys

PY3 = sys.version_info[0] >= 3

if PY3:
    raw_input = input
    unicode = str

chr_byte = lambda i: chr(i).encode('latin-1') if PY3 else chr(i)

CURTSIES_NAMES = {}
control_chars = dict((chr_byte(i), u'<Ctrl-%s' % chr(i + 0x60)) for i in range(0x00, 0x1b))
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
CURSES_NAMES[b'\x1b[3~'] = u'KEY_DC'
CURSES_NAMES[b'\x1b[5~'] = u'KEY_PPAGE'
CURSES_NAMES[b'\x1b[6~'] = u'KEY_NPAGE'
CURSES_NAMES[b'\x1b[Z'] = u'KEY_BTAB'
#TODO add home and end? and everything else

KEYMAP_PREFIXES = set()
for table in (CURSES_NAMES, CURTSIES_NAMES):
    for k in table:
        if k.startswith(b'\x1b'):
            for i in range(1, len(k)):
                KEYMAP_PREFIXES.add(k[:i])

MAX_KEYPRESS_SIZE = max(len(seq) for seq in (list(CURSES_NAMES.keys()) + list(CURTSIES_NAMES.keys())))

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

def decodable(seq, encoding):
    try:
        u = seq.decode(encoding)
    except UnicodeDecodeError:
        return False
    else:
        return True

def get_key(bytes_, encoding, keynames='curses', full=False):
    """Return key pressed from bytes_ or None

    Return a key name (possibly just a plain one like 'a') or None
    meaning it's an incomplete sequence of bytes (more bytes
    needed to determine the key pressed)

    encoding is how the bytes should be interpreted

    if full, match a key even if it could be a prefix to another key
    (useful for detecting a plain escape key for instance, since
    escape is also a prefix to a bunch of char sequences for other keys)

    Events are subclasses of Event, or unicode strings

    Precondition: get_key(prefix, keynames) is None for all proper prefixes of
    bytes. This means get_key should be called on progressively larger inputs
    (for 'asdf', first on 'a', then on 'as', then on 'asd' - until a non-None
    value is returned)
    """
    if not all(isinstance(c, type(b'')) for c in bytes_):
        raise ValueError("get key expects bytes, got %r" % bytes_) # expects raw bytes
    seq = b''.join(bytes_)

    def key_name():
        if keynames == 'curses':
            return CURSES_NAMES.get(seq, seq.decode(encoding))
        elif keynames == 'curtsies':
            return CURTSIES_NAMES.get(seq, seq.decode(encoding))
        else:
            return seq.decode(encoding)

    key_known = seq in CURTSIES_NAMES or seq in CURSES_NAMES or decodable(seq, encoding)

    if full and key_known:
        return key_name()
    elif seq in KEYMAP_PREFIXES:
        return None # need more input to make up a full keypress
    elif key_known:
        return key_name()
    else:
        return seq.decode(encoding) # the plain name

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

def try_keys():
    print('press a bunch of keys (not at the same time, but you can hit them pretty quickly)')
    import tty
    import termios
    import fcntl
    import os
    from termhelpers import Cbreak

    def ask_what_they_pressed(seq, Normal):
        print('Unidentified character sequence!')
        with Normal():
            while True:
                r = raw_input("type 'ok' to prove you're not pounding keys ")
                if r.lower().strip() == 'ok':
                    break
        while True:
            print('Press the key that produced %r again please' % (seq,))
            retry = os.read(sys.stdin.fileno(), 1000)
            if seq == retry:
                break
            print("nope, that wasn't it")
        with Normal():
            name = raw_input('Describe in English what key you pressed')
            f = open('keylog.txt', 'a')
            f.write("%r is called %s\n" % (seq, name))
            f.close()
            print('Thanks! Sent thomasballinger@gmail.com an email with that, or submit a pull request')

    with Cbreak(sys.stdin) as NoCbreak:
        while True:
            try:
                chars = os.read(sys.stdin.fileno(), 1000)
                print('---')
                print(repr(chars))
                if chars in CURTSIES_NAMES:
                    print(CURTSIES_NAMES[chars])
                elif len(chars) == 1:
                    print('literal')
                else:
                    print('unknown!!!')
                    ask_what_they_pressed(chars, NoCbreak)
            except OSError:
                pass

if __name__ == '__main__':
    seq = [b'\x1b', b'O', b'P']
    print(seq)
    print(get_key(seq, sys.stdin.encoding))
    try_keys()
