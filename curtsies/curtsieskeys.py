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
  (b'\x1bOA',     u'<UP>'),         # in issue 92 its shown these should be normal arrows,
  (b'\x1bOB',     u'<DOWN>'),       # not ctrl-arrows as we previously had them.
  (b'\x1bOC',     u'<RIGHT>'),
  (b'\x1bOD',     u'<LEFT>'),

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

  (b'\x1b[1;10A', u'<Esc+Shift-UP>'),
  (b'\x1b[1;10B', u'<Esc+Shift-DOWN>'),
  (b'\x1b[1;10C', u'<Esc+Shift-RIGHT>'),
  (b'\x1b[1;10D', u'<Esc+Shift-LEFT>'),

  (b'\x1bOP',     u'<F1>'),
  (b'\x1bOQ',     u'<F2>'),
  (b'\x1bOR',     u'<F3>'),
  (b'\x1bOS',     u'<F4>'),

  # see bpython #626
  (b'\x1b[11~',   u'<F1>'),
  (b'\x1b[12~',   u'<F2>'),
  (b'\x1b[13~',   u'<F3>'),
  (b'\x1b[14~',   u'<F4>'),

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
  (b'\x1b[4~',    u'<END>'),
  (b'\x1b\x1b[5~',u'<Esc+PAGEUP>'),
  (b'\x1b\x1b[6~',u'<Esc+PAGEDOWN>'),

  (b'\x1b[H',     u'<HOME>'),    # reported by amorozov in bpython #490
  (b'\x1b[F',     u'<END>'),     # reported by amorozov in bpython #490

  (b'\x1bOH',     u'<HOME>'),    # reported by mixmastamyk in curtsies #78
  (b'\x1bOF',     u'<END>'),     # reported by mixmastamyk in curtsies #78

  # not fixing for back compat.
  # (b"\x1b[1~", u'<FIND>'),       # find

  (b"\x1b[2~", u'<INSERT>'),       # insert (0)
  (b"\x1b[3~", u'<DELETE>'),       # delete (.), "Execute"

  # not fixing for back compat.
  # (b"\x1b[4~", u'<SELECT>'),       # select

  (b"\x1b[5~", u'<PAGEUP>'),       # pgup   (9)
  (b"\x1b[6~", u'<PAGEDOWN>'),     # pgdown (3)
  (b"\x1b[7~", u'<HOME>'),         # home
  (b"\x1b[8~", u'<END>'),          # end
  (b"\x1b[OA", u'<UP>'),           # up     (8)
  (b"\x1b[OB", u'<DOWN>'),         # down   (2)
  (b"\x1b[OC", u'<RIGHT>'),        # right  (6)
  (b"\x1b[OD", u'<LEFT>'),         # left   (4)
  (b"\x1b[OF", u'<END>'),          # end    (1)
  (b"\x1b[OH", u'<HOME>'),         # home   (7)

  ])
