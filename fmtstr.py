#Heavily influenced by https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py


colors = 'dark', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray'
FG_COLORS = dict(zip(colors, range(30, 38)))
BG_COLORS = dict(zip(colors, range(40, 48)))
STYLES = dict(zip(('bold', 'underline', 'blink', 'invert'), [1,4,5,7]))
FG_NUMBER_TO_COLOR = {v:k for k, v in FG_COLORS.items()}
BG_NUMBER_TO_COLOR = {v:k for k, v in BG_COLORS.items()}

# styles - functions that take the string and transform it. Chainable
# Should not change the displayable length of the string!
CLEAR = '[0m'
xforms = {
    'fg' : lambda x, v: ('[%sm' % v)+x+CLEAR,
    'bg' : lambda x, v: ('[%sm' % v)+x+CLEAR,
    'bold' : lambda x: ('[%sm' % STYLES['bold'])+x+CLEAR,
    'underline' : lambda x: ('[%sm' % STYLES['underline'])+x+CLEAR,
    'blink' : lambda x: ('[%sm' % STYLES['blink'])+x+CLEAR,
    'invert' : lambda x: ('[%sm' % STYLES['invert'])+x+CLEAR,
    }
text_xforms = {
    'upper' : lambda x: x.upper(),
    'lower' : lambda x: x.lower(),
    'title' : lambda x: x.title(),
    }

class FmtStr(object):
    """Formatting annotations on strings"""
    def __init__(self, string, *args, **kwargs):
        self.string = string
        self.atts = {}
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError("args must be strings")
            if arg.lower() in FG_COLORS:
                if 'fg' in kwargs: raise ValueError("fg specified twice")
                kwargs['fg'] = FG_COLORS[arg]
            elif arg.lower().startswith('on_') and arg[3:].lower() in BG_COLORS:
                if 'bg' in kwargs: raise ValueError("fg specified twice")
                kwargs['bg'] = BG_COLORS[arg[3:]]
            elif arg.lower() in STYLES:
                kwargs[arg] = True
            elif arg.lower() in ('upper', 'lower', 'title'):
                kwargs[arg] = True
            else:
                raise ValueError("couldn't process arg: "+repr(arg))
        for k in kwargs:
            if k not in xforms and k not in text_xforms:
                raise ValueError("Can't apply that transformation")
        if 'fg' in kwargs:
            if kwargs['fg'] in FG_COLORS:
                kwargs['fg'] = FG_COLORS[kwargs['fg']]
            if kwargs['fg'] not in FG_COLORS.values():
                raise ValueError("Bad fg value: %s", kwargs['fg'])
        if 'bg' in kwargs:
            if kwargs['bg'] in BG_COLORS:
                kwargs['bg'] = BG_COLORS[kwargs['bg']]
            print 'kwargs:', kwargs
            if kwargs['bg'] not in BG_COLORS.values():
                raise ValueError("Bad bg value: %s", kwargs['bg'])
        self.atts = kwargs

    def __len__(self):
        return len(self.string)

    def __repr__(self):
        def pp_att(att):
            if att == 'fg': return FG_NUMBER_TO_COLOR[self.atts[att]]
            elif att == 'bg': return 'on_' + BG_NUMBER_TO_COLOR[self.atts[att]]
            else: return att
        return (''.join(pp_att(att)+'(' for att in sorted(self.atts))
                + self.string + ')'*len(self.atts))

    def __str__(self):
        s = self.string
        for transform_set in [text_xforms, xforms]:
            for k, v in self.atts.items():
                if k not in transform_set: continue
                if v is True:
                    s = transform_set[k](s)
                else:
                    s = transform_set[k](s, v)
        return s

def test(*args, **kwargs):
    print '---'
    print args, kwargs
    f = FmtStr(*args, **kwargs)
    print repr(f)
    print repr(str(f))
    print f
    print '---'

if __name__ == '__main__':
    import doctest; doctest.testmod()
    #test("hello!", 'red')
    test("there", bg='red')
    test("there", 'blue', 'underline', bg=42)
