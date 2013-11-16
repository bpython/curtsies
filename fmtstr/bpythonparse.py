from bpython import formatter # just to check at import time that it's there
from .termformatconstants import FG_COLORS, BG_COLORS, colors
from .fmtstr import fmtstr, FmtStr

from functools import partial

import re


cnames = dict(list(zip('krgybmcwd', colors + ('default',))))

def func_for_letter(l, default='k'):
    if l == 'd':
        l = default
    return partial(fmtstr, fg=cnames[l.lower()], bold=(l.lower() != l))

def color_for_letter(l, default='k'):
    if l == 'd':
        l = default
    return cnames[l.lower()]

def parse(s):
    r"""
    >>> parse('\x01y\x03print\x04')
    yellow('print')
    >>> parse('\x01y\x03print\x04\x01c\x03 \x04\x01g\x031\x04\x01c\x03 \x04\x01Y\x03+\x04\x01c\x03 \x04\x01g\x032\x04')
    yellow('print')+cyan(' ')+green('1')+cyan(' ')+bold(yellow('+'))+cyan(' ')+green('2')
    """
    rest = s
    stuff = []
    while True:
        if not rest:
            break
        d, rest = peel_off_string(rest)
        stuff.append(d)
    return (sum([fs_from_match(d) for d in stuff[1:]], fs_from_match(stuff[0]))
            if len(stuff) > 0
            else FmtStr())

def fs_from_match(d):
    atts = {}
    if d['fg']:

        # this isn't according to spec as I understand it
        if d['fg'] != d['fg'].lower():
            d['bold'] = True
        #TODO figure out why boldness isn't based on presence of \x02

        color = cnames[d['fg'].lower()]
        if color != 'default':
            atts['fg'] = FG_COLORS[color]
    if d['bg']:
        if d['bg'] == 'I':
            color = colors[(colors.index(color) + (len(colors) // 2)) % len(colors)] # hack for finding the "inverse"
        else:
            color = cnames[d['bg'].lower()]
        if color != 'default':
            atts['bg'] = BG_COLORS[color]
    if d['bold']:
        atts['bold'] = True
    return fmtstr(d['string'], **atts)

def peel_off_string(s):
    r"""
    >>> r = peel_off_string('\x01RI\x03]\x04asdf')
    >>> r == ({'bg': 'I', 'string': ']', 'fg': 'R', 'colormarker': '\x01RI', 'bold': ''}, 'asdf')
    True
    """
    p = r"""(?P<colormarker>\x01
                (?P<fg>[krgybmcwdKRGYBMCWD]?)
                (?P<bg>[krgybmcwdKRGYBMCWDI]?)?)
            (?P<bold>\x02?)
            \x03
            (?P<string>[^\x04]*)
            \x04
            (?P<rest>.*)
            """
    m = re.match(p, s, re.X | re.DOTALL)
    assert m, repr(s)
    d = m.groupdict()
    rest = d['rest']
    del d['rest']
    return d, rest

def string_to_fmtstr(x):
    from pygments import format
    from bpython.formatter import BPythonFormatter
    from bpython._py3compat import PythonLexer
    from bpython.config import Struct, loadini, default_config_path
    config = Struct()
    loadini(config, default_config_path())
    return parse(format(PythonLexer().get_tokens(x), BPythonFormatter(config.color_scheme)))

def test():
    from pygments import format
    from bpython.formatter import BPythonFormatter
    from bpython._py3compat import PythonLexer
    from bpython.config import Struct, loadini, default_config_path
    config = Struct()
    loadini(config, default_config_path())

    all_tokens = list(PythonLexer().get_tokens('print 1 + 2'))
    formatted_line = format(all_tokens, BPythonFormatter(config.color_scheme))
    print((repr(formatted_line)))
    fs = parse(formatted_line)
    print((repr(fs)))
    print(fs)

    string_to_fmtstr('asdf')

if __name__ == '__main__':
    import doctest; doctest.testmod()
    test()
