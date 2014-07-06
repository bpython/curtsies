import unittest
from mock import Mock
from curtsies import events
import select

from curtsies.input import Input, getpreferredencoding

class TestInput(unittest.TestCase):
    def test_create(self):
        inp = Input()

    def test_iter(self):
        inp = Input()
        inp.send = Mock()
        inp.send.return_value = None
        for i, e in zip(range(3), inp):
            self.assertEqual(e, None)
        self.assertEqual(inp.send.call_count, 3)

    def test_mocks(self):
        events.a = 10
        self.assertTrue(True)

    def test_mocks2(self):
        self.assertEqual(events.a, 10)

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
        self.assertEqual(inp.nonblocking_read(), 0)

    def test_send_paste(self):
        inp = Input()
        inp.unprocessed_bytes = []
        inp.wait_for_read_ready_or_timeout = Mock()
        inp.wait_for_read_ready_or_timeout.return_value = (True, None)
        inp.nonblocking_read = Mock()
        n = inp.paste_threshold + 1

        first_time = [True]
        def side_effect():
            if first_time:
                inp.unprocessed_bytes.extend(b'a'*n)
                first_time.pop()
                return n
            else:
                return None
        inp.nonblocking_read.side_effect = side_effect

        r = inp.send(0)
        self.assertIsInstance(r, events.PasteEvent)
        self.assertEqual(r.events, [u'a'] * n)
