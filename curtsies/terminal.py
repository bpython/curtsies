"""
Terminal control sequences

see: https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes

inspired by
https://github.com/gwk/gloss/blob/master/python/gloss/io/cs.py
"""

import fcntl
import logging
import os
import re
import signal
import sys
import termios
import tty

from . import events

PY3 = sys.version_info[0] >= 3

QUERY_CURSOR_POSITION = "\x1b[6n"
SCROLL_DOWN = "D"
CURSOR_UP, CURSOR_DOWN, CURSOR_FORWARD, CURSOR_BACK = ["["+char for char in 'ABCD']
ERASE_REST_OF_LINE = "[K"
ERASE_LINE = "[2K"
HIDE_CURSOR = "[?25l"
SHOW_CURSOR = "[?25h"
ERASE_REST_OF_SCREEN = "[0J"
TURN_OFF_AUTO_WRAP = "[?7l"

_SIGWINCH_COUNTER = 0

class SigwinchException(Exception):
    pass

def produce_simple_sequence(seq):
    def func(ts):
        ts.write(seq)
    return func

def produce_cursor_sequence(char):
    """Returns a method that issues a cursor control sequence."""
    def func(ts, n=1):
        if n: ts.write("[%d%s" % (n, char))
    return func

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

class Terminal(object):
    """Communicates with an ANSI-compatible terminal through in and out streams

    In the context of a Terminal, in_stream is placed in cbreak or
    raw mode, and window size change (SIGWINCH) and interrupt (SIGINT) signals
    are handled, stored for reporting by Terminal.get_event().
    """
    def __init__(self, in_stream=sys.stdin, out_stream=sys.stdout, input_mode='cbreak', paste_mode=False):
        self.in_stream = in_stream
        self.out_stream = out_stream
        self.in_buffer = []     # Chars from the input, not yet consumed by an event.
        self.sigwinch_counter = _SIGWINCH_COUNTER - 1
        self.last_screen_size = None
        self.sigint_queued = False
        self.refresh_queued = False
        if not input_mode in ['raw', 'cbreak']:
            raise ValueError("input_mode must be raw or cbreak")
        self.input_mode = input_mode
        self.paste_mode_enabled = paste_mode

    def __enter__(self):
        def sigwinch_handler(signum, frame):
            global _SIGWINCH_COUNTER
            _SIGWINCH_COUNTER += 1
            self.last_screen_size = None
        self.orig_sigwinch_handler = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, sigwinch_handler)

        self.original_stty = termios.tcgetattr(self.out_stream)
        self.turn_off_line_wrapping()
        if self.input_mode == 'raw':
            tty.setraw(self.in_stream)
        else:
            assert self.input_mode == 'cbreak'
            tty.setcbreak(self.in_stream)
            self.orig_sigint_handler = signal.getsignal(signal.SIGINT)

            def sigint_handler(signum, frame):
                self.sigint_queued = True

            signal.signal(signal.SIGINT, sigint_handler)

        return self

    def __exit__(self, type, value, traceback):
        if self.orig_sigwinch_handler:
            signal.signal(signal.SIGWINCH, self.orig_sigwinch_handler)
        if self.orig_sigint_handler:
            signal.signal(signal.SIGINT, self.orig_sigint_handler)
        termios.tcsetattr(self.out_stream, termios.TCSANOW, self.original_stty)
        #import os; os.system('stty '+self.original_stty)

    up, down, forward, back = [produce_cursor_sequence(c) for c in 'ABCD']
    fwd = forward
    query_cursor_position = produce_simple_sequence(QUERY_CURSOR_POSITION)
    scroll_down = produce_simple_sequence(SCROLL_DOWN)
    erase_rest_of_line = produce_simple_sequence(ERASE_REST_OF_LINE)
    erase_line = produce_simple_sequence(ERASE_LINE)
    hide_cursor = produce_simple_sequence(HIDE_CURSOR)
    show_cursor = produce_simple_sequence(SHOW_CURSOR)
    erase_rest_of_screen = produce_simple_sequence(ERASE_REST_OF_SCREEN)
    turn_off_line_wrapping = produce_simple_sequence(TURN_OFF_AUTO_WRAP)

    def request_refresh(self):
        self.refresh_queued = True
    stuff_a_refresh_request = request_refresh # for compatibility atm

    def nonblocking_read(self): # XXX rename?
        """returns False if no waiting character, else True and adds it to in_buffer"""
        with nonblocking(self.in_stream):
            if PY3:
                next_c = self.in_stream.read(1)
                if next_c:
                    self.in_buffer.append(next_c)
                    return True
                else:
                    return False
            else:
                try:
                    next_c = self.in_stream.read(1)
                except IOError:
                    return False
                else:
                    self.in_buffer.append(next_c)
                    return True

    def get_event(self, keynames='curses', idle=()):
        """Blocks and returns the next event, using curses names by default

        idle is a generator which will be iterated over until an event occurs

        If several keypresses have occurred, they are queued and returned one
        by one. Other events have higher priority than keypresses, and can
        pass keypresses in this queue. These event are, in descending priority:
            -a SIGWINCH has occurred
            -a SIGINT has occurred
            -a refresh has been requested (Terminal.request_refresh)
        """
        # Within this method, the pending input is chars + self.in_buffer.
        # chars is a prefix of a mapped-key's char-sequence (which might be the whole thing);
        # e.g. an arrow key is an escape sequence.
        chars = []
        paste_event = None

        while True:
            # XXX shouldn't these return-cases first put anything in chars back into self.in_buffer?
            if self.sigwinch_counter < _SIGWINCH_COUNTER:
                self.sigwinch_counter = _SIGWINCH_COUNTER
                self.in_buffer = chars + self.in_buffer
                return events.WindowChangeEvent(*self.get_screen_size())
            if self.sigint_queued:
                self.sigint_queued = False
                return events.SigIntEvent()
            if self.refresh_queued:
                self.refresh_queued = False
                return events.RefreshRequestEvent('terminal control')
            if len(chars) > 10: #debugging tool - eventually detect all key sequences!
                raise ValueError("Key sequence not detected at some point: %r" % ''.join(chars))
            logging.debug('getting key for %r', chars)
            logging.debug('self.in_buffer %r', self.in_buffer)
            if chars == ["\x1b"]:
                # This also won't work on Windows I think
                if self.in_buffer or self.nonblocking_read():
                    chars.append(self.in_buffer.pop(0))
                    continue
                else:
                    c = '\x1b'
                    chars = []
            else:
                c = events.get_key(chars, keynames=keynames)

            # c is a keyname or None for an incomplete prefix.
            # Here the pending input has two cases: either
            #   * c is None: pending is chars + self.in_buffer.
            #   * c is not None: pending is self.in_buffer.

            if c:
                if self.paste_mode_enabled:
                    # This needs to be disabled if we ever want to work with Windows
                    #TODO take the in_buffer into account here!
                    if self.in_buffer or self.nonblocking_read():
                        if not paste_event:
                            paste_event = events.PasteEvent()
                        paste_event.events.append(c)
                        chars = []
                    else:
                        if paste_event:
                            paste_event.events.append(c)
                            return paste_event
                        else:
                            return c
                else:
                    return c

            if self.in_buffer:
                chars.append(self.in_buffer.pop(0))
                continue

            for _ in idle:
                if self.nonblocking_read():
                    break
            else:
                prev_sigint_handler = signal.getsignal(signal.SIGINT)
                signal.signal(signal.SIGINT, signal.default_int_handler)
                prev_sigwinch_handler = signal.getsignal(signal.SIGWINCH)
                def loud_sigwinch_handler(signum, frame):
                    prev_sigwinch_handler(signum, frame)
                    raise SigwinchException('Stop blocking on read so we can deliver a window change!')
                signal.signal(signal.SIGWINCH, loud_sigwinch_handler)
                try:
                    chars.append(self.in_stream.read(1))
                except IOError:
                    continue
                except KeyboardInterrupt:
                    return events.SigIntEvent()
                except SigwinchException:
                    continue
                finally:
                    if prev_sigint_handler:
                        signal.signal(signal.SIGINT, prev_sigint_handler)
                    signal.signal(signal.SIGWINCH, prev_sigwinch_handler)

    def retrying_read(self):
        while True:
            try:
                return self.in_stream.read(1)
            except IOError:
                logging.debug('read interrupted, retrying')

    def write(self, msg):
        self.out_stream.write(msg)
        self.out_stream.flush()

    def get_cursor_position(self):
        """Returns the terminal (row, column) of the cursor"""
        self.query_cursor_position()
        resp = ''
        while True:
            c = self.retrying_read()
            resp += c
            m = re.search(r'(?P<extra>.*)\x1b\[(?P<row>\\d+);(?P<column>\\d+)R', resp)
            if m:
                row = int(m.groupdict()['row'])
                col = int(m.groupdict()['column'])
                self.in_buffer.extend(list(m.groupdict()['extra']))
                return (row, col)

    def set_cursor_position(self, xxx_todo_changeme):
        (row, col) = xxx_todo_changeme
        self.write("[%d;%dH" % (row, col))

    def get_screen_size(self, break_cache=False):
        #TODO use real get terminal size query
        if self.last_screen_size and not break_cache:
            return self.last_screen_size
        orig = self.get_cursor_position()
        self.fwd(10000) # 10000 is much larger than any reasonable terminal
        self.down(10000)
        size = self.get_cursor_position()
        self.set_cursor_position(orig)
        self.last_screen_size = size
        return size


def demo():
    with Terminal() as tc:
        pos = str(tc.get_cursor_position())
        tc.write(pos)
        tc.back(len(pos))
        tc.scroll_down()
        tc.write('Control-D to exit')
        tc.back(len('Control-D to exit'))
        tc.scroll_down()
        tc.write('....')
        tc.back(4)
        while True:
            e = tc.get_event(keynames=None)
            if e in events.CURSES_NAMES:
                data = "%r : %s, but called %s for curses compatibility" % (e, events.pp_event(e), events.CURSES_NAMES[e])
            else:
                data = "%r : %s" % (e, events.pp_event(e))
            tc.write(data)
            tc.scroll_down()
            tc.back(len(data))
            if e == '':
                sys.exit()

def test_cursor():
    with Terminal() as tc:
        pos = tc.get_cursor_position()
    print(pos)

if __name__ == '__main__':
    demo()

