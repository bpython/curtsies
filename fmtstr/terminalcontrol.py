"""
Terminal control sequences

see: https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes

inspired by
https://github.com/gwk/gloss/blob/master/python/gloss/io/cs.py
"""

import os
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
    def __init__(self, in_stream=sys.stdin, out_stream=sys.stdout):
        self.in_stream = in_stream
        self.out_stream = out_stream
        self.in_buffer = []
        self.sigwinch_counter = _SIGWINCH_COUNTER - 1
        self.last_screen_size = None

    def __enter__(self):
        def signal_handler(signum, frame):
            global _SIGWINCH_COUNTER
            _SIGWINCH_COUNTER += 1
            self.last_screen_size = None
        signal.signal(signal.SIGWINCH, signal_handler)

        self.original_stty = termios.tcgetattr(self.out_stream)
        tty.setraw(self.in_stream)
        return self

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGWINCH, lambda: None)
        termios.tcsetattr(self.out_stream, termios.TCSANOW, self.original_stty)
        #os.system('stty '+self.original_stty)

    up, down, forward, back = [produce_cursor_sequence(c) for c in 'ABCD']
    fwd = forward
    query_cursor_position = produce_simple_sequence(QUERY_CURSOR_POSITION)
    scroll_down = produce_simple_sequence(SCROLL_DOWN)
    erase_rest_of_line = produce_simple_sequence(ERASE_REST_OF_LINE)
    erase_line = produce_simple_sequence(ERASE_LINE)
    hide_cursor = produce_simple_sequence(HIDE_CURSOR)
    show_cursor = produce_simple_sequence(SHOW_CURSOR)
    erase_rest_of_screen = produce_simple_sequence(ERASE_REST_OF_SCREEN)

    def get_event_curses(self):
        """get event, with keypress events translated to their curses equivalent"""
        e = self.get_event()
        if e in CURSES_TABLE:
            return CURSES_TABLE[e]
        return e

    def get_event(self, use_curses_aliases=True, fake_input=None):
        """Blocks and returns the next event"""
        #TODO make this cooler - generator? Trie?
        chars = []
        while True:
            #logging.debug('checking if instance counter (%d) is less than global (%d) ' % (self.sigwinch_counter, _SIGWINCH_COUNTER))
            if self.sigwinch_counter < _SIGWINCH_COUNTER:
                self.sigwinch_counter = _SIGWINCH_COUNTER
                self.in_buffer = chars + self.in_buffer
                return events.WindowChangeEvent(*self.get_screen_size())
            #TODO properly detect escape key! Probably via a timer, or nonblocking read?

            if ((chars and chars[0] != '\x1b') or
            (len(chars) == 2 and chars[1] not in ['[', 'O', '\x1b']) or
            (len(chars) == 4 and chars[1] == '\x1b' and chars[2] == '[') or
            (len(chars) > 2 and chars[1] in ['[', 'O'] and chars[-1] not in tuple('1234567890;'))):
                return ''.join(chars) if not use_curses_aliases else CURSES_TABLE.get(''.join(chars), ''.join(chars))
            if fake_input:
                self.in_buffer.extend(list(fake_input))
            if self.in_buffer:
                chars.append(self.in_buffer.pop(0))
                continue
            try:
                chars.append(self.in_stream.read(1))
            except IOError:
                continue

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
        tc.write('asdf')
        tc.back(4)
        tc.scroll_down()
        tc.write('asdf')
        tc.back(4)
        while True:
            e = tc.get_event()
            tc.write(repr(e))
            tc.scroll_down()
            tc.back(len(repr(e)))
            if e == '':
                sys.exit()

def test_cursor():
    with TerminalController() as tc:
        pos = tc.get_cursor_position()
    print(pos)

if __name__ == '__main__':
    test()

