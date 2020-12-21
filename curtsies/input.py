import locale
import os
import signal
import select
import sys
import termios
import threading
import time
import tty

import logging

logger = logging.getLogger(__name__)


from .termhelpers import Nonblocking
from . import events

from typing import Callable, Type, TextIO, Optional, List, Union, Text, cast, Tuple, Any
from types import TracebackType, FrameType

READ_SIZE = 1024
assert READ_SIZE >= events.MAX_KEYPRESS_SIZE
# if a keypress could require more bytes than we read to be identified,
# the paste logic that reads more data as needed might not work.


def is_main_thread():
    # type: () -> bool
    return threading.current_thread() == threading.main_thread()


class ReplacedSigIntHandler:
    def __init__(self, handler):
        # type: (Callable) -> None
        self.handler = handler

    def __enter__(self):
        # type: () -> None
        self.orig_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.handler)

    def __exit__(self, type=None, value=None, traceback=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]) -> None
        signal.signal(signal.SIGINT, self.orig_sigint_handler)


class Input:
    """Keypress and control event generator"""

    def __init__(
        self,
        in_stream=None,
        keynames="curtsies",
        paste_threshold=events.MAX_KEYPRESS_SIZE + 1,
        sigint_event=False,
        signint_callback_provider=None,
        disable_terminal_start_stop=False,
    ):
        # type: (TextIO, str, int, bool, None, bool) -> None
        """Returns an Input instance.

        Args:
            in_stream (file): Defaults to sys.__stdin__
            keynames (string): How keypresses should be named - one of
              'curtsies', 'curses', or 'plain'.
            paste_threshold (int): How many bytes must be read in one
              os.read on the in_stream to trigger the keypresses they
              represent to be combined into a single paste event
            sigint_event (bool): Whether SIGINT signals from the OS
              should be intercepted and returned as SigIntEvent objects
            disable_terminal_start_stop (bool): If True, disable terminal
              start/stop using Ctrl-s/Ctrl-q, thus enabling these keys
              to be read as input by curtsies
        """
        if in_stream is None:
            in_stream = sys.__stdin__
        self.in_stream = in_stream
        self.unprocessed_bytes = (
            []
        )  # type: List[bytes]  # leftover from stdin, unprocessed yet
        self.keynames = keynames
        self.paste_threshold = paste_threshold
        self.sigint_event = sigint_event
        self.disable_terminal_start_stop = disable_terminal_start_stop
        self.sigints = []  # type: List[events.SigIntEvent]

        self.readers = []  # type: List[int]
        self.queued_interrupting_events = []  # type: List[Union[events.Event, Text]]
        self.queued_events = []  # type: List[events.Event]
        self.queued_scheduled_events = (
            []
        )  # type: List[Tuple[float, events.ScheduledEvent]]

    # prospective: this could be useful for an external select loop
    def fileno(self):
        # type: () -> int
        return self.in_stream.fileno()

    def __enter__(self):
        # type: () -> Input
        self.original_stty = termios.tcgetattr(self.in_stream)
        tty.setcbreak(self.in_stream, termios.TCSANOW)

        if self.disable_terminal_start_stop:
            attrs = termios.tcgetattr(self.in_stream)
            tty_cc = cast(List[Union[bytes, int]], attrs[-1])
            tty_cc[termios.VSTOP] = 0  # Ctrl-s
            tty_cc[termios.VSTART] = 0  # Ctrl-q
            termios.tcsetattr(self.in_stream, termios.TCSANOW, attrs)

        if sys.platform == "darwin":
            attrs = termios.tcgetattr(self.in_stream)
            VDSUSP = termios.VSUSP + 1
            tty_cc = cast(List[Union[bytes, int]], attrs[-1])
            tty_cc[VDSUSP] = 0
            termios.tcsetattr(self.in_stream, termios.TCSANOW, attrs)

        if self.sigint_event and is_main_thread():
            self.orig_sigint_handler = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self.sigint_handler)
        return self

    def __exit__(self, type=None, value=None, traceback=None):
        # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]) -> None
        if (
            self.sigint_event
            and is_main_thread()
            and self.orig_sigint_handler is not None
        ):
            signal.signal(signal.SIGINT, self.orig_sigint_handler)
        termios.tcsetattr(self.in_stream, termios.TCSANOW, self.original_stty)

    def sigint_handler(self, signum, frame):
        # type: (Union[signal.Signals, int], FrameType) -> None
        self.sigints.append(events.SigIntEvent())

    def __iter__(self):
        # type: () -> Input
        return self

    def __next__(self):
        # type: () -> Union[None, Text, events.Event]
        return self.send(None)

    def unget_bytes(self, string):
        # type: (bytes) -> None
        """Adds bytes to be internal buffer to be read

        This method is for reporting bytes from an in_stream read
        not initiated by this Input object"""

        self.unprocessed_bytes.extend(string[i : i + 1] for i in range(len(string)))

    def _wait_for_read_ready_or_timeout(self, timeout):
        # type: (Union[float, int, None]) -> Tuple[bool, Optional[Union[events.Event, Text]]]
        """Returns tuple of whether stdin is ready to read and an event.

        If an event is returned, that event is more pressing than reading
        bytes on stdin to create a keyboard input event.
        If stdin is ready, either there are bytes to read or a SIGTSTP
        triggered by dsusp has been received"""
        remaining_timeout = timeout
        t0 = time.time()
        while True:
            try:
                (rs, _, _) = select.select(
                    [self.in_stream.fileno()] + self.readers, [], [], remaining_timeout
                )
                if not rs:
                    return False, None
                r = rs[0]  # if there's more than one, get it in the next loop
                if r == self.in_stream.fileno():
                    return True, None
                else:
                    os.read(r, 1024)
                    if self.queued_interrupting_events:
                        return False, self.queued_interrupting_events.pop(0)
                    elif remaining_timeout is not None:
                        remaining_timeout = max(0, t0 + remaining_timeout - time.time())
                        continue
                    else:
                        continue

            except OSError:
                if self.sigints:
                    return False, self.sigints.pop()
                if remaining_timeout is not None:
                    remaining_timeout = max(remaining_timeout - (time.time() - t0), 0)

    def send(self, timeout=None):
        # type: (Union[float, int, None]) -> Union[None, Text, events.Event]
        """Returns an event or None if no events occur before timeout."""
        if self.sigint_event and is_main_thread():
            with ReplacedSigIntHandler(self.sigint_handler):
                return self._send(timeout)
        else:
            return self._send(timeout)

    def _send(self, timeout):
        # type: (Union[float, int, None]) -> Union[None, Text, events.Event]
        def find_key():
            # type: () -> Optional[Text]
            """Returns keypress identified by adding unprocessed bytes or None"""
            current_bytes = []
            while self.unprocessed_bytes:
                current_bytes.append(self.unprocessed_bytes.pop(0))
                e = events.get_key(
                    current_bytes,
                    getpreferredencoding(),
                    keynames=self.keynames,
                    full=len(self.unprocessed_bytes) == 0,
                )
                if e is not None:
                    current_bytes = []
                    return e
            if current_bytes:  # incomplete keys shouldn't happen
                raise ValueError("Couldn't identify key sequence: %r" % current_bytes)
            return None

        if self.sigints:
            return self.sigints.pop()
        if self.queued_events:
            return self.queued_events.pop(0)
        if self.queued_interrupting_events:
            return self.queued_interrupting_events.pop(0)

        if self.queued_scheduled_events:
            self.queued_scheduled_events.sort()  # TODO use a data structure that inserts sorted
            when, _ = self.queued_scheduled_events[0]
            if when < time.time():
                logger.debug(
                    "popping an event! %r %r",
                    self.queued_scheduled_events[0],
                    self.queued_scheduled_events[1:],
                )
                return self.queued_scheduled_events.pop(0)[1]
            else:
                time_until_check = min(
                    max(0, when - time.time()),
                    timeout if timeout is not None else sys.maxsize,
                )  # type: Union[float, int, None]
        else:
            time_until_check = timeout

        # try to find an already pressed key from prev input
        e = find_key()
        if e is not None:
            return e

        stdin_ready_for_read, event = self._wait_for_read_ready_or_timeout(
            time_until_check
        )
        if event:
            return event
        if (
            self.queued_scheduled_events and when < time.time()
        ):  # when should always be defined
            # because queued_scheduled_events should not be modified during this time
            logger.debug(
                "popping an event! %r %r",
                self.queued_scheduled_events[0],
                self.queued_scheduled_events[1:],
            )
            return self.queued_scheduled_events.pop(0)[1]
        if not stdin_ready_for_read:
            return None

        num_bytes = self._nonblocking_read()
        if num_bytes == 0:
            # thought stdin was ready, but not bytes to read is triggered
            # when SIGTSTP was send by dsusp
            return None

        if self.paste_threshold is not None and num_bytes > self.paste_threshold:
            paste = events.PasteEvent()
            while True:
                if len(self.unprocessed_bytes) < events.MAX_KEYPRESS_SIZE:
                    self._nonblocking_read()  # may need to read to get the rest of a keypress
                e = find_key()
                if e is None:
                    return paste
                else:
                    paste.events.append(e)
        else:
            e = find_key()
            assert e is not None
            return e

    def _nonblocking_read(self):
        # type: () -> int
        """Returns the number of characters read and adds them to self.unprocessed_bytes"""
        with Nonblocking(self.in_stream):
            try:
                data = os.read(self.in_stream.fileno(), READ_SIZE)
            except BlockingIOError:
                return 0
            if data:
                self.unprocessed_bytes.extend(data[i : i + 1] for i in range(len(data)))
                return len(data)
            else:
                return 0

    def event_trigger(self, event_type):
        # type: (Type[events.Event]) -> Callable
        """Returns a callback that creates events.

        Returned callback function will add an event of type event_type
        to a queue which will be checked the next time an event is requested."""

        def callback(**kwargs):
            # type: (**Any) -> None
            self.queued_events.append(event_type(**kwargs))  # type: ignore

        return callback

    def scheduled_event_trigger(self, event_type):
        # type: (Type[events.ScheduledEvent]) -> Callable
        """Returns a callback that schedules events for the future.

        Returned callback function will add an event of type event_type
        to a queue which will be checked the next time an event is requested."""

        def callback(when):
            # type: (float) -> None
            self.queued_scheduled_events.append((when, event_type(when=when)))

        return callback

    def threadsafe_event_trigger(self, event_type):
        # type: (Type[events.Event]) -> Callable
        """Returns a callback to creates events, interrupting current event requests.

        Returned callback function will create an event of type event_type
        which will interrupt an event request if one
        is concurrently occuring, otherwise adding the event to a queue
        that will be checked on the next event request."""
        readfd, writefd = os.pipe()
        self.readers.append(readfd)

        def callback(**kwargs):
            # type: (**Any) -> None
            # TODO use a threadsafe queue for this
            self.queued_interrupting_events.append(event_type(**kwargs))  # type: ignore
            logger.debug(
                "added event to events list %r", self.queued_interrupting_events
            )
            os.write(writefd, b"interrupting event!")

        return callback


def getpreferredencoding():
    # type: () -> str
    return locale.getpreferredencoding() or sys.getdefaultencoding()


def main():
    # type: () -> None
    with Input() as input_generator:
        print(repr(input_generator.send(2)))
        print(repr(input_generator.send(1)))
        print(repr(input_generator.send(0.5)))
        print(repr(input_generator.send(0.2)))
        for e in input_generator:
            print(repr(e))


if __name__ == "__main__":
    main()
