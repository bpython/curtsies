"""All the key sequences"""
# If you add a binding, add something about your setup
# if you can figure out why it's different

# Special names are for multi-character keys, or key names
# that would be hard to write in a config file

#TODO add PAD keys hack as in bpython.cli

import io
import os

try:
    import curses
    has_curses = True
except ImportError:
    has_curses = False


class KeyInfo(object):
    def __init__(self, fallback, name, capname=None):
        self.name = name
        self.fallback = fallback
        self.capname = capname

    def seq(self):
        cursesseq = None
        if has_curses and self.capname is not None:
            cursesseq = curses.tigetstr(self.capname)
        if cursesseq is not None:
            return cursesseq
        else:
            return self.fallback


KEYS = (
    KeyInfo(b' ',          u'<SPACE>'),
    KeyInfo(b'\x1b ',      u'<Esc+SPACE>'),
    KeyInfo(b'\t',         u'<TAB>', ),
    KeyInfo(b'\x1b[Z',     u'<Shift-TAB>'),
    KeyInfo(b'\x1b[A',     u'<UP>',               'kcuu1'),
    KeyInfo(b'\x1b[B',     u'<DOWN>',             'kcud1'),
    KeyInfo(b'\x1b[C',     u'<RIGHT>',            'kcuf1'),
    KeyInfo(b'\x1b[D',     u'<LEFT>',             'kcub1'),
    KeyInfo(b'\x1bOA',     u'<Ctrl-UP>'),
    KeyInfo(b'\x1bOB',     u'<Ctrl-DOWN>'),
    KeyInfo(b'\x1bOC',     u'<Ctrl-RIGHT>'),
    KeyInfo(b'\x1bOD',     u'<Ctrl-LEFT>'),

    KeyInfo(b'\x1b[1;5A',  u'<Ctrl-UP>'),
    KeyInfo(b'\x1b[1;5B',  u'<Ctrl-DOWN>'),
    KeyInfo(b'\x1b[1;5C',  u'<Ctrl-RIGHT>'), # reported by myint
    KeyInfo(b'\x1b[1;5D',  u'<Ctrl-LEFT>'),  # reported by myint

    KeyInfo(b'\x1b[5A',    u'<Ctrl-UP>'),    # not sure about these, someone wanted them for bpython
    KeyInfo(b'\x1b[5B',    u'<Ctrl-DOWN>'),
    KeyInfo(b'\x1b[5C',    u'<Ctrl-RIGHT>'),
    KeyInfo(b'\x1b[5D',    u'<Ctrl-LEFT>'),

    KeyInfo(b'\x1b[1;9A',  u'<Esc+UP>'),
    KeyInfo(b'\x1b[1;9B',  u'<Esc+DOWN>'),
    KeyInfo(b'\x1b[1;9C',  u'<Esc+RIGHT>'),
    KeyInfo(b'\x1b[1;9D',  u'<Esc+LEFT>'),

    KeyInfo(b'\x1b[1;10A', u'<Esc+Shift-UP>'),
    KeyInfo(b'\x1b[1;10B', u'<Esc+Shift-DOWN>'),
    KeyInfo(b'\x1b[1;10C', u'<Esc+Shift-RIGHT>'),
    KeyInfo(b'\x1b[1;10D', u'<Esc+Shift-LEFT>'),

    KeyInfo(b'\x1bOP',     u'<F1>',               'kf1'),
    KeyInfo(b'\x1bOQ',     u'<F2>',               'kf2'),
    KeyInfo(b'\x1bOR',     u'<F3>',               'kf3'),
    KeyInfo(b'\x1bOS',     u'<F4>',               'kf4'),
    KeyInfo(b'\x1b[15~',   u'<F5>',               'kf5'),
    KeyInfo(b'\x1b[17~',   u'<F6>',               'kf6'),
    KeyInfo(b'\x1b[18~',   u'<F7>',               'kf7'),
    KeyInfo(b'\x1b[19~',   u'<F8>',               'kf8'),
    KeyInfo(b'\x1b[20~',   u'<F9>',               'kf9'),
    KeyInfo(b'\x1b[21~',   u'<F10>',              'kf10'),
    KeyInfo(b'\x1b[23~',   u'<F11>',              'kf11'),
    KeyInfo(b'\x1b[24~',   u'<F12>',              'kf12'),
    KeyInfo(b'\x00',       u'<Ctrl-SPACE>'),
    KeyInfo(b'\x1c',       u'<Ctrl-\\>'),
    KeyInfo(b'\x1d',       u'<Ctrl-]>'),
    KeyInfo(b'\x1e',       u'<Ctrl-6>'),
    KeyInfo(b'\x1f',       u'<Ctrl-/>'),
    KeyInfo(b'\x7f',       u'<BACKSPACE>',        'kbs'),    # for some folks this is ctrl-backspace apparently
    KeyInfo(b'\x1b\x7f',   u'<Esc+BACKSPACE>'),
    KeyInfo(b'\xff',       u'<Meta-BACKSPACE>'),
    KeyInfo(b'\x1b\x1b[A', u'<Esc+UP>'),    # uncertain about these four
    KeyInfo(b'\x1b\x1b[B', u'<Esc+DOWN>'),
    KeyInfo(b'\x1b\x1b[C', u'<Esc+RIGHT>'),
    KeyInfo(b'\x1b\x1b[D', u'<Esc+LEFT>'),
    KeyInfo(b'\x1b',       u'<ESC>'),
    KeyInfo(b'\x1b[1~',    u'<HOME>',             'khome'),
    KeyInfo(b'\x1b[2~',    u'<PADENTER>'),  #TODO untested
    KeyInfo(b'\x1b[3~',    u'<PADDELETE>'), #TODO check this name
    KeyInfo(b'\x1b[4~',    u'<END>',              'kend'),
    KeyInfo(b'\x1b[5~',    u'<PAGEUP>',           'kpp'),
    KeyInfo(b'\x1b[6~',    u'<PAGEDOWN>',         'knp'),
    KeyInfo(b'\x1b\x1b[5~',u'<Esc+PAGEUP>'),
    KeyInfo(b'\x1b\x1b[6~',u'<Esc+PAGEDOWN>'),
)


def get_curtsies_names():
    if has_curses:
        with io.open(os.devnull) as null:
            curses.setupterm(fd=null.fileno())

    return dict((key.seq(), key.name) for key in KEYS)
