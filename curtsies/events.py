"""Language for describing events that in terminal"""
import sys

PY3 = sys.version_info[0] >= 3

CURTSIES_NAMES = {}
control_chars = dict((chr(i), '<Ctrl-%s' % chr(i + 0x60)) for i in range(0x00, 0x1b))
CURTSIES_NAMES.update(control_chars)
for i in range(0x00, 0x80):
    CURTSIES_NAMES[b'\x1b'+chr(i)] = '<Esc+%s>' % chr(i)
for i in range(0x00, 0x1b): # Overwrite the control keys with better labels
    CURTSIES_NAMES[b'\x1b'+chr(i)] = '<Esc+Ctrl-%s>' % chr(i + 0x40)
for i in range(0x00, 0x80):
    CURTSIES_NAMES[chr(i + 0x80)] = '<Meta-%s>' % chr(i)
for i in range(0x00, 0x1b): # Overwrite the control keys with better labels
    CURTSIES_NAMES[chr(i + 0x80)] = '<Meta-Ctrl-%s>' % chr(i + 0x40)
from curtsieskeys import CURTSIES_NAMES as special_curtsies_names
CURTSIES_NAMES.update(special_curtsies_names)

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

KEYMAP_PREFIXES = set()
for table in (CURSES_NAMES, CURTSIES_NAMES):
    for k in table:
        if k.startswith('\x1b'):
            for i in range(1, len(k)):
                KEYMAP_PREFIXES.add(k[:i])

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

def get_key(chars, keynames='curses', full=False):
    """the plain name
    Return a key name (possibly just a plain one like 'a') or None
    meaning it's an incomplete sequence of characters (more chars
    needed to determine the key pressed)

    if full, match a key even if it could be a prefix to another key
    (useful for detecting a plain escape key for instance, since
    escape is also a prefix to a bunch of char sequences for other keys)

    Precondition: get_key(prefix, keynames) is None for all proper prefixes of
    chars. This means get_key should be called on progressively larger inputs
    (for 'asdf', first on 'a', then on 'as', then on 'asd' - until a non-None
    value is returned)
    """
    seq = ''.join(chars)

    def known_key():
        if keynames == 'curses':
            return CURSES_NAMES.get(seq, seq)
        elif keynames == 'curtsies':
            return CURTSIES_NAMES.get(seq, seq)
        else:
            return seq

    if full and (seq in CURTSIES_NAMES or seq in CURSES_NAMES):
        return known_key()
    elif seq in KEYMAP_PREFIXES:
        return None # need more input to make up a full keypress
    elif seq in CURTSIES_NAMES or seq in CURSES_NAMES:
        return known_key()
    else:
        return seq # the plain name

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
    return repr(seq)[2:-1]

def curtsies_name(seq):
    return CURTSIES_NAMES.get(seq, seq)

def curses_name(seq):
    return CURSES_NAMES.get(seq, seq)


# What if we assume we'll always get all of the bytes from a keypress at the same time?
# So our only job is to identify when we have more than one key.
# While a char sequence is a prefix, get more characters.
# Once it's not, is it a key? Return if so, error if not.


def try_keys():
    print 'press a bunch of keys (not at the same time, but you can hit them pretty quickly)'
    import tty
    import termios
    import fcntl
    import os

    def ask_what_they_pressed(seq, Normal):
        print 'Unidentified character sequence!'
        with Normal():
            while True:
                r = raw_input("type 'ok' to prove you're not pounding keys ")
                if r.lower().strip() == 'ok':
                    break
        while True:
            print 'Press the key that produced %r again please' % (seq,)
            retry = os.read(sys.stdin.fileno(), 1000)
            if seq == retry:
                break
            print "nope, that wasn't it"
        with Normal():
            name = raw_input('Describe in English what key you pressed')
            f = open('keylog.txt', 'a')
            f.write("%r is called %s\n" % (seq, name))
            f.close()
            print 'Thanks! Sent thomasballinger@gmail.com an email with that, or submit a pull request'

    class Cbreak(object):
        def __init__(self, stream):
            self.stream = stream
        def __enter__(self):
            self.original_stty = termios.tcgetattr(self.stream)
            tty.setcbreak(self.stream)
            class NoCbreak(object):
                def __enter__(inner_self):
                    inner_self.original_stty = termios.tcgetattr(self.stream)
                    termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)
                    print
                def __exit__(inner_self, *args):
                    termios.tcsetattr(self.stream, termios.TCSANOW, inner_self.original_stty)
            return NoCbreak
        def __exit__(self, *args):
            termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

    with Cbreak(sys.stdin) as NoCbreak:
        while True:
            try:
                chars = os.read(sys.stdin.fileno(), 1000)
                print '---'
                print repr(chars)
                if chars in CURTSIES_NAMES:
                    print CURTSIES_NAMES[chars]
                elif len(chars) == 1:
                    print 'literal'
                else:
                    print 'unknown!!!'
                    ask_what_they_pressed(chars, NoCbreak)
            except OSError:
                pass

if __name__ == '__main__':
    seq = ['\x1b', 'O', 'P']
    print seq
    print get_key(seq)
    try_keys()
