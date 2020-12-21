import unittest
from functools import partial

from curtsies.configfile_keynames import keymap
from curtsies.events import CURTSIES_NAMES


class TestKeymap(unittest.TestCase):
    def config(self, mapping, curtsies):
        curtsies_names = keymap[mapping]
        self.assertTrue(
            curtsies in CURTSIES_NAMES.values(), "%r is not a curtsies name" % curtsies
        )
        self.assertTrue(
            curtsies in curtsies_names,
            "config name %r does not contain %r, just %r"
            % (mapping, curtsies, curtsies_names),
        )

    def test_simple(self):
        self.config("M-m", "<Esc+m>")
        self.config("M-m", "<Esc+m>")
        self.config("C-m", "<Ctrl-m>")
        self.config("C-[", "<ESC>")
        self.config("C-\\", "<Ctrl-\\>")
        self.config("C-]", "<Ctrl-]>")
        self.config("C-^", "<Ctrl-6>")
        self.config("C-_", "<Ctrl-/>")  # ??? for bpython compatibility
        self.config("F1", "<F1>")
