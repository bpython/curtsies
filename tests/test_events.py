import unittest
from functools import partial

from curtsies import events

class TestChrByte(unittest.TestCase):
    def test_simple(self):
        """0-255 can be turned into bytes"""
        for i in range(256):
            print i
            s = eval('"\\x%s"' % ('0' + hex(i)[2:])[-2:])
            self.assertEqual(s, events.chr_byte(i))

class TestCurtsiesNames(unittest.TestCase):
    def spot_check(self):
        self.assertEqual(events.CURTSIES_NAMES[b'\x1b\x08'], u'<Esc+Ctrl-H>')
        self.assertEqual(events.CURTSIES_NAMES[b'\x00'],  u'<Ctrl-SPACE>')
        self.assertEqual(events.CURTSIES_NAMES[b'\xea'], u'<Meta-j>')

    def test_all_values_unicode(self):
        for seq, e in events.CURTSIES_NAMES.iteritems():
            self.assertIsInstance(seq, bytes)

    def test_all_keys_bytes(self):
        for seq, e in events.CURTSIES_NAMES.iteritems():
            self.assertIsInstance(e, type(u''))

class TestDecodable(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(events.decodable(b'd', 'utf-8'))
        self.assertFalse(events.decodable(b'\xfe', 'utf-8')) # 254 is off limits

class TestGetKey(unittest.TestCase):
    def test_utf8_full(self):
        get_utf_full = partial(events.get_key, encoding='utf-8', keynames='plain', full=True)
        self.assertEqual(get_utf_full(b'hello'), u'hello')
        self.assertEqual(get_utf_full(b'\x1b['), u'\x1b[')
        with self.assertRaises(UnicodeDecodeError):
            get_utf_full('\xfe')
        with self.assertRaises(ValueError):
            get_utf_full(u'a')

    def test_utf8(self):
        get_utf = partial(events.get_key, encoding='utf-8', keynames='plain', full=False)
        self.assertEqual(get_utf(b'hello'), u'hello')
        self.assertEqual(get_utf(b'\x1b['), None)
        with self.assertRaises(UnicodeDecodeError):
            get_utf(b'\xfe')
        with self.assertRaises(ValueError):
            get_utf(u'a')

class TestPPEvent(unittest.TestCase):
    def test(self):
        self.assertEqual(events.pp_event(u'a'), 'a')
