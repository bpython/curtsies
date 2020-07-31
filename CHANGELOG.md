# Changelog

## [Unreleased]

## [0.3.4] - 2020-07-15
- Prevent crash when embedding in situations including the lldb debugger. Thanks Nathan Lanza!

## [0.3.3] - 2020-07-06
- Revert backslash removal, since this broke bpython in 0.3.2

## [0.3.2] - 2020-07-04
- Migrate doc generation to Python 3
- Add MyPy typing
- Remove logging level message. Thanks Jack Rybarczyk!
- Assorted fixes: Thanks Armira Nance, Etienne Richart, Evan Allgood, Nathan Lanza, and Vilhelm Prytz!

## [0.3.1] - 2020-01-03
- Add "dark" format function
- Add Input option to disable terminal start/stop. Thanks George Kettleborough!
- Fix Py3.6 compatibility. Thanks Po-Chuan Hsieh!
- Assorted fixes, thanks Jakub Wilk and Manuel Mendez!

## [0.3.0] - 2018-02-13
- Change name of "dark" color to "black"
- Drop support for Python 2.6 and 3.3
- New FmtStr method width_aware_splitlines which cuts up a FmtStr in linear time

## [0.2.12] - 2018-02-12
- Fix accidentally quadratic `width_aware_slice` behavior (fixes bpython #729)
  This bug causes bpython to hang on large output. Thanks Ben Wiederhake!
- Allow curtsies to be run on non-main threads (useful for bpython #555)
  This should allow bpython to be run in a variety of situations like Django's runserver
- Add function keys for some keyboard/terminal setups

## [0.2.11] - 2016-10-22
- Handle unsupported SGR codes (fixes bpython #657)
- Add Ctrl-Delete  for some keyboard/terminal setups
- Many doc fixes. Thanks Dan Puttick!

## [0.2.10] - 2016-10-10
- Add sequences for home and end (fixes Curtsies #78)

## [0.2.9] - 2016-09-07
- Fix #90 again
- Strip ansi escape sequences if parsing fmtstr input fails
- Prevent invalid negative cursor positions in CursorAwareWindow (fixes bpython #607)
- '\x1bOA' changed from ctrl-arrow key to arrow key (fixes bpython #621)
- Alternate codes for F1-F4 (fixes bpython #626)
