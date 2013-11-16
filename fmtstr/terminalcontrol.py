"""
Terminal control sequences

see: https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes

inspired by
https://github.com/gwk/gloss/blob/master/python/gloss/io/cs.py
"""

import sys
import tty
import signal
import re
import termios
import logging

from . import events


_SIGWINCH_COUNTER = 0

QUERY_CURSOR_POSITION = "\x1b[6n"
SCROLL_DOWN = "D"
CURSOR_UP, CURSOR_DOWN, CURSOR_FORWARD, CURSOR_BACK = ["[%s" for char in 'ABCD']
ERASE_REST_OF_LINE = "[K"
ERASE_LINE = "[2K"
HIDE_CURSOR = "[?25l"
SHOW_CURSOR = "[?25h"
ERASE_REST_OF_SCREEN = "[0J"

def produce_simple_sequence(seq):
    def func(ts):
        ts.write(seq)
    return func

def produce_cursor_sequence(char):
    """Returns a method that issues a cursor control sequence."""
    def func(ts, n=1):
        if n: ts.write("[%d%s" % (n, char))
    return func

class TerminalController(object):
    """Returns terminal control functions partialed for stream returned by
    stream_getter on att lookup"""
    def __init__(self, in_stream=sys.stdin, out_stream=sys.stdout, input_mode='cbreak'):
        self.in_stream = in_stream
        self.out_stream = out_stream
        self.in_buffer = []
        self.sigwinch_counter = _SIGWINCH_COUNTER - 1
        self.last_screen_size = None
        self.queued_sigint = False
        self.queued_refresh_request = False
        if not input_mode in ['raw', 'cbreak']:
            raise ValueError("input_mode must be raw or cbreak")
        self.input_mode = input_mode

    def __enter__(self):
        def signal_handler(signum, frame):
            global _SIGWINCH_COUNTER
            _SIGWINCH_COUNTER += 1
            self.last_screen_size = None
        self.orig_sigwinch_handler = signal.getsignal(signal.SIGWINCH)
        signal.signal(signal.SIGWINCH, signal_handler)

        self.original_stty = termios.tcgetattr(self.out_stream)
        if self.input_mode == 'raw':
            tty.setraw(self.in_stream)
        else:
            assert self.input_mode == 'cbreak'
            tty.setcbreak(self.in_stream)
            self.orig_sigint_handler = signal.getsignal(signal.SIGINT)

            def sigint_handler(signum, frame):
                self.queued_sigint = True

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

    def stuff_a_refresh_request(self):
        self.queued_refresh_request = True

    def get_event(self, keynames='curses', fake_input=None):
        """Blocks and returns the next event, using curses names by default"""
        #TODO make this cooler - generator? Trie?
        chars = []
        while True:
            if self.queued_sigint:
                self.queued_sigint = False
                return events.SigIntEvent()
            if self.queued_refresh_request:
                self.queued_refresh_request = False
                return events.RefreshRequestEvent('terminal control')
            if len(chars) > 10:
                raise ValueError("Key sequence not detected at some point: %r" % ''.join(chars))
            #logging.debug('checking if instance counter (%d) is less than global (%d) ' % (self.sigwinch_counter, _SIGWINCH_COUNTER))
            if self.sigwinch_counter < _SIGWINCH_COUNTER:
                self.sigwinch_counter = _SIGWINCH_COUNTER
                self.in_buffer = chars + self.in_buffer
                return events.WindowChangeEvent(*self.get_screen_size())
            #TODO properly detect escape key! Probably via a timer, or nonblocking read?

            logging.debug('getting key for %r', chars)
            logging.debug('self.in_buffer %r', self.in_buffer)
            c = events.get_key(chars, keynames=keynames)
            if c:
                return c
            if fake_input:
                self.in_buffer.extend(list(fake_input))
                fake_input = None
            if self.in_buffer:
                chars.append(self.in_buffer.pop(0))
                continue

            prev_sigint_handler = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal.default_int_handler)
            try:
                chars.append(self.in_stream.read(1))
            except IOError:
                continue
            except KeyboardInterrupt:
                return events.SigIntEvent()
            finally:
                if prev_sigint_handler:
                    signal.signal(signal.SIGINT, prev_sigint_handler)

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
            m = re.search('(?P<extra>.*)\x1b\[(?P<row>\\d+);(?P<column>\\d+)R', resp)
            if m:
                row = int(m.groupdict()['row'])
                col = int(m.groupdict()['column'])
                self.in_buffer.extend(list(m.groupdict()['extra']))
                return (row, col)

    def set_cursor_position(self, xxx_todo_changeme):
        (row, col) = xxx_todo_changeme
        self.write("[%d;%dH" % (row, col))

    def get_screen_size(self, break_cache=False):
        #TODO generalize get_cursor_position code and use it here instead
        if self.last_screen_size and not break_cache:
            return self.last_screen_size
        orig = self.get_cursor_position()
        self.fwd(10000) # 10000 is much larger than any reasonable terminal
        self.down(10000)
        size = self.get_cursor_position()
        self.set_cursor_position(orig)
        self.last_screen_size = size
        return size

def test():
    with TerminalController() as tc:
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
            if e in events.CURSES_TABLE:
                data = "%r : %s, but called %s for curses compatibility" % (e, events.pp_event(e), events.CURSES_TABLE[e])
            else:
                data = "%r : %s" % (e, events.pp_event(e))
            tc.write(data)
            tc.scroll_down()
            tc.back(len(data))
            if e == '':
                sys.exit()

def test_cursor():
    with TerminalController() as tc:
        pos = tc.get_cursor_position()
    print(pos)

if __name__ == '__main__':
    test()

