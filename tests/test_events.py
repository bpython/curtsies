import unittest
from functools import partial

from curtsies import events


class TestChrByte(unittest.TestCase):
    def test_simple(self):
        """0-255 can be turned into bytes"""
        for i in range(256):
            s = eval('b"\\x%s"' % ("0" + hex(i)[2:])[-2:])
            self.assertEqual(s, events.chr_byte(i))

    def test_helpers(self):
        self.assertEqual(events.chr_byte(97), b"a")
        self.assertEqual(events.chr_uni(97), "a")


class TestCurtsiesNames(unittest.TestCase):
    def spot_check(self):
        self.assertEqual(events.CURTSIES_NAMES[b"\x1b\x08"], "<Esc+Ctrl-H>")
        self.assertEqual(events.CURTSIES_NAMES[b"\x00"], "<Ctrl-SPACE>")
        self.assertEqual(events.CURTSIES_NAMES[b"\xea"], "<Meta-j>")

    def test_all_values_unicode(self):
        for seq, e in events.CURTSIES_NAMES.items():
            self.assertEqual(type(seq), bytes)

    def test_all_keys_bytes(self):
        for seq, e in events.CURTSIES_NAMES.items():
            self.assertEqual(type(e), str)


class TestDecodable(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(events.decodable(b"d", "utf-8"))
        self.assertFalse(events.decodable(b"\xfe", "utf-8"))  # 254 is off limits


class TestGetKey(unittest.TestCase):
    def test_utf8_full(self):
        get_utf_full = partial(
            events.get_key, encoding="utf-8", keynames="curtsies", full=True
        )
        self.assertEqual(get_utf_full([b"h"]), "h")
        self.assertEqual(get_utf_full([b"\x1b", b"["]), "<Esc+[>")
        self.assertRaises(UnicodeDecodeError, get_utf_full, [b"\xfe\xfe"])
        self.assertRaises(ValueError, get_utf_full, "a")

    def test_utf8(self):
        get_utf = partial(
            events.get_key, encoding="utf-8", keynames="curtsies", full=False
        )
        self.assertEqual(get_utf([b"h"]), "h")
        self.assertEqual(get_utf([b"\x1b", b"["]), None)
        self.assertEqual(get_utf([b"\xe2"]), None)
        self.assertRaises(ValueError, get_utf, "a")

    def test_multibyte_utf8(self):
        get_utf = partial(
            events.get_key, encoding="utf-8", keynames="curtsies", full=False
        )
        self.assertEqual(get_utf([b"\xc3"]), None)
        self.assertEqual(get_utf([b"\xe2"]), None)
        self.assertEqual(get_utf([b"\xe2"], full=True), "<Meta-b>")
        self.assertEqual(get_utf([b"\xc3", b"\x9f"]), "ß")
        self.assertEqual(get_utf([b"\xe2"]), None)
        self.assertEqual(get_utf([b"\xe2", b"\x88"]), None)
        self.assertEqual(get_utf([b"\xe2", b"\x88", b"\x82"]), "∂")

    def test_sequences_without_names(self):
        get_utf = partial(
            events.get_key, encoding="utf-8", keynames="curtsies", full=False
        )
        self.assertEqual(get_utf([b"\xc3"], full=True), "<Meta-C>")
        self.assertEqual(get_utf([b"\xc3"], full=True, keynames="curses"), "xC3")

    def test_key_names(self):
        "Every key sequence with a Curses name should have a Curtsies name too."
        self.assertTrue(
            set(events.CURTSIES_NAMES).issuperset(set(events.CURSES_NAMES)),
            set(events.CURSES_NAMES) - set(events.CURTSIES_NAMES),
        )


class TestGetKeyAscii(unittest.TestCase):
    def test_full(self):
        get_ascii_full = partial(
            events.get_key, encoding="ascii", keynames="curtsies", full=True
        )
        self.assertEqual(get_ascii_full([b"a"]), "a")
        self.assertEqual(get_ascii_full([b"\xe1"]), "<Meta-a>")
        self.assertEqual(get_ascii_full([b"\xe1"], keynames="curses"), "xE1")

    def test_simple(self):
        get_ascii_full = partial(events.get_key, encoding="ascii", keynames="curtsies")
        self.assertEqual(get_ascii_full([b"a"]), "a")
        self.assertEqual(get_ascii_full([b"\xe1"]), "<Meta-a>")
        self.assertEqual(get_ascii_full([b"\xe1"], keynames="curses"), "xE1")


class TestUnknownEncoding(unittest.TestCase):
    def test_simple(self):
        get_utf16 = partial(events.get_key, encoding="utf16", keynames="curtsies")
        self.assertEqual(get_utf16([b"a"]), None)
        self.assertEqual(get_utf16([b"a"], full=True), None)
        self.assertEqual(get_utf16([b"\xe1"]), None)
        self.assertEqual(get_utf16([b"\xe1"], full=True), "<Meta-a>")


class TestSpecialKeys(unittest.TestCase):
    def test_simple(self):
        seq = [b"\x1b", b"[", b"1", b";", b"9", b"C"]
        self.assertEqual(
            [events.get_key(seq[:i], encoding="utf8") for i in range(1, len(seq) + 1)],
            [None, None, None, None, None, "<Esc+RIGHT>"],
        )


class TestPPEvent(unittest.TestCase):
    def test(self):
        self.assertEqual(events.pp_event("a"), "a")
