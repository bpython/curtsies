import tty
import termios
import fcntl
import os

from typing import IO, Type, List, Union, Optional
from types import TracebackType

_Attr = List[Union[int, List[bytes]]]


class Nonblocking:
    """
    A context manager for making an input stream nonblocking.
    """

    def __init__(self, stream):
        # type: (IO) -> None
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        # type: () -> None
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, type=None, value=None, traceback=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]) -> None
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


class Cbreak:
    def __init__(self, stream):
        # type: (IO) -> None
        self.stream = stream

    def __enter__(self):
        # type: () -> Termmode
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream, termios.TCSANOW)
        return Termmode(self.stream, self.original_stty)

    def __exit__(self, type=None, value=None, traceback=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]) -> None
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)


class Termmode:
    def __init__(self, stream, attrs):
        # type: (IO, _Attr) -> None
        self.stream = stream
        self.attrs = attrs

    def __enter__(self):
        # type: () -> None
        self.original_stty = termios.tcgetattr(self.stream)
        termios.tcsetattr(self.stream, termios.TCSANOW, self.attrs)

    def __exit__(self, type=None, value=None, traceback=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]) -> None
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)
