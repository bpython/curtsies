"""
>>> FmtStr("Hey there!", 'red')
red("Hey there!")

"""
#TODO text transforms don't compose correctly yet - upper() can ruin color formatting
#Heavily influenced by https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py

import functools
import itertools



colors = 'dark', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray'
FG_COLORS = dict(zip(colors, range(30, 38)))
BG_COLORS = dict(zip(colors, range(40, 48)))
STYLES = dict(zip(('bold', 'underline', 'blink', 'invert'), [1,4,5,7]))
FG_NUMBER_TO_COLOR = {v:k for k, v in FG_COLORS.items()}
BG_NUMBER_TO_COLOR = {v:k for k, v in BG_COLORS.items()}

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
        self.atts = self.parse_args(args, kwargs)

    @classmethod
    def parse_args(cls, args, kwargs):
        if 'style' in kwargs:
            args += (kwargs['style'],)
            del kwargs['style']
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError("args must be strings:" + repr(args))
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
            if kwargs['bg'] not in BG_COLORS.values():
                raise ValueError("Bad bg value: %s", kwargs['bg'])
        return kwargs

    def __add__(self, other):
        if isinstance(other, str):
            return CompositeFmtStr(self, FmtStr(other))
        elif isinstance(other, FmtStr):
            return CompositeFmtStr(self, other)

    def __radd__(self, other):
        if isinstance(other, str):
            return CompositeFmtStr(FmtStr(other), self)
        elif isinstance(other, FmtStr):
            return CompositeFmtStr(other, self)

    def __len__(self):
        return len(self.string)

    def __repr__(self):
        def pp_att(att):
            if att == 'fg': return FG_NUMBER_TO_COLOR[self.atts[att]]
            elif att == 'bg': return 'on_' + BG_NUMBER_TO_COLOR[self.atts[att]]
            else: return att
        return (''.join(
                        pp_att(att)+'('
                        for att in sorted(self.atts)) +
               ('"%s"' % self.string) + ')'*len(self.atts))

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

class CompositeFmtStr(FmtStr):
    #TODO allow any number of fmtstrs?
    def __init__(self, *fmtstrs, **kwargs):
        assert len(fmtstrs) == 2, repr(fmtstrs)
        fmtstrs = [s if isinstance(s, FmtStr) else FmtStr(s) for s in fmtstrs]
        fs1, fs2 = fmtstrs

        self.atts = self.parse_args([], kwargs)
        self.fmtstrs = fmtstrs

    def raise_attributes(self):
        for att in self.fmtstrs[0].atts:
            if all(att in fmtstr.atts and fmtstr.atts[att] == self.fmtstrs[0].atts[att]
                    for fmtstr in self.fmtstrs):
                self.atts[att] = self.fmtstrs[0].atts[att]
                for fmtstr in self.fmtstrs:
                    del fmtstr.atts[att]

    def recursive_raise(self):
        for fs in self.fmtstrs:
            if isinstance(fs, CompositeFmtStr):
                fs.recursive_raise()
        self.raise_attributes()

    def __repr__(self):
        def pp_att(att):
            if att == 'fg': return FG_NUMBER_TO_COLOR[self.atts[att]]
            elif att == 'bg': return 'on_' + BG_NUMBER_TO_COLOR[self.atts[att]]
            else: return att
        return (''.join(pp_att(att)+'('
                        for att in sorted(self.atts)) +
               '"%s"' % ' + '.join(repr(x) for x in self.fmtstrs) +
               ')'*len(self.atts))

    @property
    def string(self):
        return str(self.fmtstrs[0]) + str(self.fmtstrs[1])


# convenience functions
def fmtstr(string, *args, **kwargs):
    if isinstance(string, FmtStr):
        fmtstrs = [string] + [a for a in args if isinstance(a, FmtStr)]
        atts = FmtStr.parse_args([a for a in args if not isinstance(a, FmtStr)], kwargs)
        if len(fmtstrs) == 1:
            string.atts.update(atts)
            return string
        elif len(fmtstrs) == 2:
            return CompositeFmtStr(*fmtstrs, **atts)
        else:
            raise NotImplemented("Can't create FmtStr from more than two format strings currently")
    elif isinstance(string, str):
        return FmtStr(string, *args, **kwargs)
    else:
        raise ValueError("Bad Args")


for att in itertools.chain(FG_COLORS, ('on_'+x for x in BG_COLORS), STYLES, text_xforms):
    locals()[att] = functools.partial(fmtstr, style=att)

def test(f):
    print '---'
    print repr(f)
    print repr(str(f))
    print f
    print '---'

if __name__ == '__main__':
    import doctest; doctest.testmod()
    #test("hello!", 'red')
    test(FmtStr("there", bg='red'))
    test(FmtStr("there", 'blue', 'underline', bg=42))
    test(title('hey') + underline('there'))
    #test(green(on_blue('hey') + underline('there')))
    c = on_blue('hey') + underline('there')
    test(green(c))
