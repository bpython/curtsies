import os
import signal
import sys
import threading
import time
import unittest
from mock import Mock

try:
    from unittest import skip, skipUnless
except ImportError:

    def skip(f):
        return lambda self: None

    def skipUnless(condition, reason):
        if condition:
            return lambda x: x
        else:
            return lambda x: None

from curtsies import events
from curtsies.input import Input


class CustomEvent(events.Event):
    pass


class CustomScheduledEvent(events.ScheduledEvent):
    pass


@skipUnless(sys.stdin.isatty(), "stdin must be a tty")
class TestInput(unittest.TestCase):
    def test_create(self):
        Input()

    def test_iter(self):
        inp = Input()
        inp.send = Mock()
        inp.send.return_value = None
        for i, e in zip(range(3), inp):
            self.assertEqual(e, None)
        self.assertEqual(inp.send.call_count, 3)

    def test_send(self):
        inp = Input()
        inp.unprocessed_bytes = [b'a']
        self.assertEqual(inp.send('nonsensical value'), u'a')

    def test_send_nonblocking_no_event(self):
        inp = Input()
        inp.unprocessed_bytes = []
        self.assertEqual(inp.send(0), None)

    def test_nonblocking_read(self):
        inp = Input()
        self.assertEqual(inp._nonblocking_read(), 0)

    def test_send_paste(self):
        inp = Input()
        inp.unprocessed_bytes = []
        inp._wait_for_read_ready_or_timeout = Mock()
        inp._wait_for_read_ready_or_timeout.return_value = (True, None)
        inp._nonblocking_read = Mock()
        n = inp.paste_threshold + 1

        first_time = [True]

        def side_effect():
            if first_time:
                inp.unprocessed_bytes.extend([b'a']*n)
                first_time.pop()
                return n
            else:
                return None
        inp._nonblocking_read.side_effect = side_effect

        r = inp.send(0)
        self.assertEqual(type(r), events.PasteEvent)
        self.assertEqual(r.events, [u'a'] * n)

    def test_event_trigger(self):
        inp = Input()
        f = inp.event_trigger(CustomEvent)
        self.assertEqual(inp.send(0), None)
        f()
        self.assertEqual(type(inp.send(0)), CustomEvent)
        self.assertEqual(inp.send(0), None)

    def test_schedule_event_trigger(self):
        inp = Input()
        f = inp.scheduled_event_trigger(CustomScheduledEvent)
        self.assertEqual(inp.send(0), None)
        f(when=time.time())
        self.assertEqual(type(inp.send(0)), CustomScheduledEvent)
        self.assertEqual(inp.send(0), None)
        f(when=time.time()+0.01)
        self.assertEqual(inp.send(0), None)
        time.sleep(0.01)
        self.assertEqual(type(inp.send(0)), CustomScheduledEvent)
        self.assertEqual(inp.send(0), None)

    def test_schedule_event_trigger_blocking(self):
        inp = Input()
        f = inp.scheduled_event_trigger(CustomScheduledEvent)
        f(when=time.time()+0.05)
        self.assertEqual(type(next(inp)), CustomScheduledEvent)

    def test_threadsafe_event_trigger(self):
        inp = Input()
        f = inp.threadsafe_event_trigger(CustomEvent)
        def check_event():
            self.assertEqual(type(inp.send(1)), CustomEvent)
            self.assertEqual(inp.send(0), None)

        t = threading.Thread(target=check_event)
        t.start()
        f()
        t.join()

    def test_interrupting_sigint(self):
        inp = Input(sigint_event=True)

        def send_sigint():
            os.kill(os.getpid(), signal.SIGINT)

        with inp:
            t = threading.Thread(target=send_sigint)
            t.start()
            self.assertEqual(type(inp.send(1)), events.SigIntEvent)
            self.assertEqual(inp.send(0), None)
            t.join()
