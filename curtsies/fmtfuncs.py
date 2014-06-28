from functools import partial as _partial
from itertools import chain as _chain
from .termformatconstants import FG_COLORS, BG_COLORS, STYLES
from .formatstring import fmtstr

for att in _chain(FG_COLORS, ('on_'+x for x in BG_COLORS), STYLES):
    locals()[att] = _partial(fmtstr, style=att)
plain = _partial(fmtstr)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    print((blue('adf')))
    print((blue(on_red('ad'))))
    print((blue('asdf') + on_red('adsf')))
    print(((blue('asdf') + on_red('adsf'))[3:7]))
    f = blue('hey there') + on_red(' Tom!')
    print(f)
    f[1:3] = 'ot'
    print((repr(f)))
    print(f)
    f = on_blue(red('stuff'))
    print((repr(f)))
    print((repr(str(f))))
    print(f)
    print(((f + '!')[0:6] + '?'))
