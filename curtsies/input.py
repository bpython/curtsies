"""
New terminal
"""

import fcntl
import os
import signal
import select
import sys
import termios
import time
import tty

from .events import get_key

PY3 = sys.version_info[0] >= 3

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

class timeout(object):
    def __init__(self, stream, timeout):
        """Set stream to timeout after timeout tenths of a second"""
        self.stream = stream
        self.fd = self.stream.fileno()
        if timeout < 0 or timeout > 255:
            raise ValueError("Timeout must be from 0 to 255 inclusive")
        self.timeout = timeout

    def __enter__(self):
        self.orig_term = termios.tcgetattr(self.fd)
        new_term = self.orig_term[:]
        new_term[3] &= ~termios.ICANON
        new_term[6][termios.VTIME] = self.timeout
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, new_term)

    def __exit__(self, *args):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.orig_term)

class Input(object):
    def __init__(self, in_stream=sys.stdin, keynames='curtsies'):
        self.in_stream = in_stream
        self.unprocessed_bytes = [] # leftover from stdin, unprocessed yet
        self.keynames = keynames

    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.in_stream)
        tty.setcbreak(self.in_stream)
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.in_stream, termios.TCSANOW, self.original_stty)

    def __iter__(self):
        return self

    def next(self):
        return self.send(None)

    def send(self, timeout=None):
        """Returns a key or None if no key pressed"""

        def find_key():
            """Returns the keypress identified by adding unprocessed bytes, or None"""
            current_bytes = []
            while self.unprocessed_bytes:
                current_bytes.append(self.unprocessed_bytes.pop(0))
                e = get_key(current_bytes, keynames=self.keynames, full=len(self.unprocessed_bytes)==0)
                if e is not None:
                    self.current_bytes = []
                    return e
            if current_bytes: # incomplete keys shouldn't happen
                raise ValueError("Couldn't identify key sequence: %r" % self.current_bytes)

        # try to find an already pressed key from prev input
        e = find_key()
        if e is not None:
            return e

        #if self.nonblocking_read():
        #    e = find_key()
        #    assert e is not None
        #    return e
        # I've prev seen some problems with select - would checking the above first help?

        #TODO use a stdin read with a timeout instead?: http://stackoverflow.com/a/2918103/398212

        def wait_for_timout():
            remaining_timeout = timeout
            t0 = time.time()
            while True:
                try:
                    (rs, _, _) = select.select([self.in_stream.fileno()], [], [], remaining_timeout)
                    return rs
                except select.error:
                    if remaining_timeout is not None:
                        remaining_timeout = max(timeout - (time.time() - t0), 0)

        rs = wait_for_timout()
        if not rs:
            return None
        assert self.nonblocking_read()
        e = find_key()
        assert e is not None
        return e

    def nonblocking_read(self):
        """returns False if no waiting character, else True and adds it to self.unprocessed_bytes"""
        with nonblocking(self.in_stream):
            if PY3:
                data = os.read(self.in_stream.fileno(), 1024)
                if data:
                    self.unprocessed_bytes.extend(data)
                    return True
                else:
                    return False
            else:
                try:
                    data = os.read(self.in_stream.fileno(), 1024)
                except OSError:
                    return False
                else:
                    print 'received bytes: %r' % data
                    self.unprocessed_bytes.extend(data)
                    return True

def main():
    #import blessings
    #t = blessings.Terminal()
    with Input() as input_generator:
        print repr(input_generator.send(2))
        print repr(input_generator.send(1))
        print repr(input_generator.send(.5))
        print repr(input_generator.send(.2))
        for e in input_generator:
            print repr(e)

def testfunc():
    with timeout(sys.stdin, 10):
        print repr(os.read(sys.stdin.fileno(), 1024))

def sigwinch():
    import signal
    def winch_handler(signum, frame):
        print 'sigwinch received'
    signal.signal(signal.SIGWINCH, winch_handler)
    with Input() as input_generator:
        print repr(input_generator.send(2))
        print repr(input_generator.send(1))
        print repr(input_generator.send(.5))
        print repr(input_generator.send(.2))
        for e in input_generator:
            print repr(e)


if __name__ == '__main__':
    #main()
    #testfunc()
    sigwinch()
