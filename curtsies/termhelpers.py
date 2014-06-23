import tty
import termios
import fcntl
import os

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

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

