# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import unittest

from hypothesis import given
from hypothesis.strategies import text

from curtsies.formatstring import fmtstr


if sys.version_info[0] == 2:
    str = unicode


class TestFmtStrRendering(unittest.TestCase):
    @given(text())
    def test_parse_roundtrip(self, s):
        f = fmtstr(s)
        self.assertEqual(f, fmtstr(str(f)))

    @given(text())
    def test_parse_roundtrip_as_string(self, s):
        f = fmtstr(s)
        self.assertEqual(str(f), str(fmtstr(str(f))))

