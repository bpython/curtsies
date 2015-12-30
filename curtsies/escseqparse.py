r"""
Parses ascii escape sequences into marked up strings

>>> r = peel_off_esc_code('Amore')
>>> r == ('', {'csi': '\x1b', 'command': 'A', 'seq': '\x1bA'}, 'more')
True
>>> r = peel_off_esc_code('[2Astuff')
>>> r == ('', {'csi': '\x1b[', 'seq': '\x1b[2A', 'intermed': '', 'private': '', 'command': 'A', 'numbers': [2]}, 'stuff')
True
"""

from .termformatconstants import (FG_NUMBER_TO_COLOR, BG_NUMBER_TO_COLOR,
                                  NUMBER_TO_STYLE, RESET_ALL, RESET_FG,
                                  RESET_BG, STYLES)
import re


def parse(s):
    r"""
    >>> parse(">>> []")
    ['>>> []']
    >>> #parse("\x1b[33m[\x1b[39m\x1b[33m]\x1b[39m\x1b[33m[\x1b[39m\x1b[33m]\x1b[39m\x1b[33m[\x1b[39m\x1b[33m]\x1b[39m\x1b[33m[\x1b[39m")
    """
    stuff = []
    rest = s
    while True:
        front, token, rest = peel_off_esc_code(rest)
        if front:
            stuff.append(front)
        if token:
            try:
                tok = token_type(token)
                if tok:
                    stuff.append(tok)
            except ValueError:
                raise ValueError("Can't parse escape sequence: %r %r %r %r" % (s, repr(front), token, repr(rest)))
        if not rest:
            break
    return stuff


def peel_off_esc_code(s):
    r"""Returns processed text, the next token, and unprocessed text

    >>> front, d, rest = peel_off_esc_code('some[2Astuff')
    >>> front, rest
    ('some', 'stuff')
    >>> d == {'numbers': [2], 'command': 'A', 'intermed': '', 'private': '', 'csi': '\x1b[', 'seq': '\x1b[2A'}
    True
    """
    p = r"""(?P<front>.*?)
            (?P<seq>
                (?P<csi>
                    (?:[]\[)
                    |
                    ["""+'\x9b' + r"""])
                (?P<private>)
                (?P<numbers>
                    (?:\d+;)*
                    (?:\d+)?)
                (?P<intermed>""" + '[\x20-\x2f]*)' + r"""
                (?P<command>""" + '[\x40-\x7e]))' + r"""
            (?P<rest>.*)"""
    m1 = re.match(p, s, re.VERBOSE)  # multibyte esc seq
    m2 = re.match('(?P<front>.*?)(?P<seq>(?P<csi>)(?P<command>[\x40-\x5f]))(?P<rest>.*)', s)  # 2 byte escape sequence
    if m1 and m2:
        m = m1 if len(m1.groupdict()['front']) <= len(m2.groupdict()['front']) else m2
        # choose the match which has less processed text in order to get the
        # first escape sequence
    elif m1: m = m1
    elif m2: m = m2
    else: m = None

    if m:
        d = m.groupdict()
        del d['front']
        del d['rest']
        if 'numbers' in d and d['numbers'].split(';'):
            d['numbers'] = [int(x) for x in d['numbers'].split(';')]

        return m.groupdict()['front'], d, m.groupdict()['rest']
    else:
        return s, None, ''

def token_type(info):
    """
    """
    if info['command'] == 'm':
        value, = info['numbers']
        if value in FG_NUMBER_TO_COLOR: return {'fg':FG_NUMBER_TO_COLOR[value]}
        if value in BG_NUMBER_TO_COLOR: return {'bg':BG_NUMBER_TO_COLOR[value]}
        if value in NUMBER_TO_STYLE: return {NUMBER_TO_STYLE[value]:True}
        if value == RESET_ALL: return dict(dict((k, None) for k in STYLES), **{'fg':None, 'bg':None})
        if value == RESET_FG: return {'fg':None}
        if value == RESET_BG: return {'bg':None}

    elif info['command'] == 'H':  # fix for bpython #76
        return {}

    raise ValueError("Can't parse escape seq %r" % info)

if __name__ == '__main__':
    import doctest; doctest.testmod()
    #print(peel_off_esc_code('[2Astuff'))
    #print(peel_off_esc_code('Amore'))
    print((repr(parse('[31mstuff is the best[32myay'))))

