"""Mapping of config file names of keys to curtsies names

In the style of bpython config files and keymap"""

SPECIALS = {
        'C-[': u'<ESC>',
        'C-^': u'<Ctrl-6>',
        'C-_': u'<Ctrl-/>',
        }

#TODO make a precalculated version of this
class KeyMap(object):
    """Maps config file key syntax to Curtsies names"""
    def __getitem__(self, key):
        if not key: # Unbound key
            return ()
        elif key in SPECIALS:
            return (SPECIALS[key],)
        elif key[1:] and key[:2] == 'C-':
            return (u'<Ctrl-%s>' % key[2:],)
        elif key[1:] and key[:2] == 'M-':
            return (u'<Esc+%s>' % key[2:], u'<Meta-%s>' % key[2:],)
        elif key[0] == 'F' and key[1:].isdigit():
            return (u'<F%d>' % int(key[1:]),)
        else:
            raise KeyError('Configured keymap (%s)' % key +
                           ' does not exist in bpython.keys')

keymap = KeyMap()
