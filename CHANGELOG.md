# Changelog

## [0.2.9] - 2016-09-07
- fix #90 again
- strip ansi escape sequences if parsing fmtstr input fails
- prevent invalid negative cursor positions in CursorAwareWindow (fixes bpython #607)
- '\x1bOA' changed from ctrl-arrow key to arrow key (fixes bpython #621)
- alternate codes for F1-F4 (fixes bpython #626)
