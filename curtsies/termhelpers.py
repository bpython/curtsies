import tty
import termios
import fcntl
import os

class Nonblocking(object):
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
        tty.setcbreak(self.stream, termios.TCSANOW)
        return Termmode(self.stream, self.original_stty)
    def __exit__(self, *args):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class Termmode(object):
    def __init__(self, stream, attrs):
        self.stream = stream
        self.attrs = attrs
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        termios.tcsetattr(self.stream, termios.TCSANOW, self.attrs)
    def __exit__(self, *args):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)
