# Changelog

## [Unreleased]

## [0.2.11] - 2018-02-12
- fix accidentally quadratic `width_aware_slice` behavior (fixes bpython #729)
  This bug causes bpython to hang on large output. Thanks Ben Wiederhake!
- Allow curtsies to be run on non-main threads (useful for bpython #555)
  This should allow bpython to be run in a variety of situations like Django's runserver
- Add Ctrl-Delete and function keys for some keyboard/terminal setups
- Handle unsupported SGR codes (fixes bpython #657)

## [0.2.10] - 2016-10-10
- Add sequences for home and end (fixes Curtsies #78)

## [0.2.9] - 2016-09-07
- fix #90 again
- strip ansi escape sequences if parsing fmtstr input fails
- prevent invalid negative cursor positions in CursorAwareWindow (fixes bpython #607)
- '\x1bOA' changed from ctrl-arrow key to arrow key (fixes bpython #621)
- alternate codes for F1-F4 (fixes bpython #626)
