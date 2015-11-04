# -*- coding: UTF8 -*-
import unittest
from functools import partial

from curtsies import events

class TestChrByte(unittest.TestCase):
    def test_simple(self):
        """0-255 can be turned into bytes"""
        for i in range(256):
            s = eval('b"\\x%s"' % ('0' + hex(i)[2:])[-2:])
            self.assertEqual(s, events.chr_byte(i))

    def test_helpers(self):
        self.assertEqual(events.chr_byte(97), b'a')
        self.assertEqual(events.chr_uni(97), u'a')

class TestCurtsiesNames(unittest.TestCase):
    def spot_check(self):
        self.assertEqual(events.CURTSIES_NAMES[b'\x1b\x08'], u'<Esc+Ctrl-H>')
        self.assertEqual(events.CURTSIES_NAMES[b'\x00'],  u'<Ctrl-SPACE>')
        self.assertEqual(events.CURTSIES_NAMES[b'\xea'], u'<Meta-j>')

    def test_all_values_unicode(self):
        for seq, e in events.CURTSIES_NAMES.items():
            self.assertEqual(type(seq), bytes)

    def test_all_keys_bytes(self):
        for seq, e in events.CURTSIES_NAMES.items():
            self.assertEqual(type(e), type(u''))

class TestPPEvent(unittest.TestCase):
    def test(self):
        self.assertEqual(events.pp_event(u'a'), 'a')
