"""All the key sequences"""
# If you add a binding, add something about your setup
# if you can figure out why it's different

# Special names are for multi-character keys, or key names
# that would be hard to write in a config file

#TODO add PAD keys hack as in bpython.cli

CURTSIES_NAMES = dict([
  (b' ',          u'<SPACE>'),
  (b'\x1b ',      u'<Esc+SPACE>'),
  (b'\t',         u'<TAB>'),
  (b'\x1b[Z',     u'<Shift-TAB>'),
  (b'\x1b[A',     u'<UP>'),
  (b'\x1b[B',     u'<DOWN>'),
  (b'\x1b[C',     u'<RIGHT>'),
  (b'\x1b[D',     u'<LEFT>'),
  (b'\x1bOA',     u'<Ctrl-UP>'),
  (b'\x1bOB',     u'<Ctrl-DOWN>'),
  (b'\x1bOC',     u'<Ctrl-RIGHT>'),
  (b'\x1bOD',     u'<Ctrl-LEFT>'),

  (b'\x1b[1;5A',  u'<Ctrl-UP>'),
  (b'\x1b[1;5B',  u'<Ctrl-DOWN>'),
  (b'\x1b[1;5C',  u'<Ctrl-RIGHT>'), # reported by myint
  (b'\x1b[1;5D',  u'<Ctrl-LEFT>'),  # reported by myint

  (b'\x1b[5A',    u'<Ctrl-UP>'),    # not sure about these, someone wanted them for bpython
  (b'\x1b[5B',    u'<Ctrl-DOWN>'),
  (b'\x1b[5C',    u'<Ctrl-RIGHT>'),
  (b'\x1b[5D',    u'<Ctrl-LEFT>'),

  (b'\x1b[1;9A',  u'<Esc+UP>'),
  (b'\x1b[1;9B',  u'<Esc+DOWN>'),
  (b'\x1b[1;9C',  u'<Esc+RIGHT>'),
  (b'\x1b[1;9D',  u'<Esc+LEFT>'),

  (b'\x1b[1;10A', u'<Esc+Shift-LEFT>'),
  (b'\x1b[1;10B', u'<Esc+Shift-LEFT>'),
  (b'\x1b[1;10C', u'<Esc+Shift-LEFT>'),
  (b'\x1b[1;10D', u'<Esc+Shift-LEFT>'),

  (b'\x1bOP',     u'<F1>'),
  (b'\x1bOQ',     u'<F2>'),
  (b'\x1bOR',     u'<F3>'),
  (b'\x1bOS',     u'<F4>'),
  (b'\x1b[15~',   u'<F5>'),
  (b'\x1b[17~',   u'<F6>'),
  (b'\x1b[18~',   u'<F7>'),
  (b'\x1b[19~',   u'<F8>'),
  (b'\x1b[20~',   u'<F9>'),
  (b'\x1b[21~',   u'<F10>'),
  (b'\x1b[23~',   u'<F11>'),
  (b'\x1b[24~',   u'<F12>'),
  (b'\x00',       u'<Ctrl-SPACE>'),
  (b'\x1c',       u'<Ctrl-\\>'),
  (b'\x1d',       u'<Ctrl-]>'),
  (b'\x1e',       u'<Ctrl-6>'),
  (b'\x1f',       u'<Ctrl-/>'),
  (b'\x7f',       u'<BACKSPACE>'),    # for some folks this is ctrl-backspace apparently
  (b'\x1b\x7f',   u'<Esc+BACKSPACE>'),
  (b'\xff',       u'<Meta-BACKSPACE>'),
  (b'\x1b\x1b[A', u'<Esc+UP>'),    # uncertain about these four
  (b'\x1b\x1b[B', u'<Esc+DOWN>'),
  (b'\x1b\x1b[C', u'<Esc+RIGHT>'),
  (b'\x1b\x1b[D', u'<Esc+LEFT>'),
  (b'\x1b',       u'<ESC>'),
  (b'\x1b[1~',    u'<HOME>'),
  (b'\x1b[2~',    u'<PADENTER>'),  #TODO untested
  (b'\x1b[3~',    u'<PADDELETE>'), #TODO check this name
  (b'\x1b[4~',    u'<END>'),
  (b'\x1b[5~',    u'<PAGEUP>'),
  (b'\x1b[6~',    u'<PAGEDOWN>'),
  (b'\x1b\x1b[5~',u'<Esc+PAGEUP>'),
  (b'\x1b\x1b[6~',u'<Esc+PAGEDOWN>'),

  (b'\x1b[H',     u'<HOME>'),    # reported by amorozov in bpython #490
  (b'\x1b[F',     u'<END>'),     # reported by amorozov in bpython #490
  ])
