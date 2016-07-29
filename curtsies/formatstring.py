from __future__ import unicode_literals
r"""Colored strings that behave mostly like strings

>>> s = fmtstr("Hey there!", 'red')
>>> s
red('Hey there!')
>>> s[4:7]
red('the')
>>> red_on_blue = fmtstr('hello', 'red', 'on_blue')
>>> blue_on_red = fmtstr('there', fg='blue', bg='red')
>>> green = fmtstr('!', 'green')
>>> full = red_on_blue + ' ' + blue_on_red + green
>>> full
on_blue(red('hello'))+' '+on_red(blue('there'))+green('!')
>>> str(full)
'\x1b[31m\x1b[44mhello\x1b[49m\x1b[39m \x1b[34m\x1b[41mthere\x1b[49m\x1b[39m\x1b[32m!\x1b[39m'
>>> fmtstr(', ').join(['a', fmtstr('b'), fmtstr('c', 'blue')])
'a'+', '+'b'+', '+blue('c')
>>> fmtstr(u'hello', u'red', bold=False)
red('hello')
"""
#TODO add a way to composite text without losing original formatting information

import itertools
import re
import sys
import wcwidth

from .escseqparse import parse, remove_ansi
from .termformatconstants import (FG_COLORS, BG_COLORS, STYLES,
                                  FG_NUMBER_TO_COLOR, BG_NUMBER_TO_COLOR,
                                  RESET_ALL, RESET_BG, RESET_FG,
                                  seq)

PY3 = sys.version_info[0] >= 3

if PY3:
    unicode = str

xforms = {
    'fg' :        lambda s, v: '%s%s%s' % (seq(v), s, seq(RESET_FG)),
    'bg' :        lambda s, v: seq(v)+s+seq(RESET_BG),
    'bold' :      lambda s: seq(STYLES['bold'])     +s+seq(RESET_ALL),
    'underline' : lambda s: seq(STYLES['underline'])+s+seq(RESET_ALL),
    'blink' :     lambda s: seq(STYLES['blink'])    +s+seq(RESET_ALL),
    'invert' :    lambda s: seq(STYLES['invert'])   +s+seq(RESET_ALL),
}


class FrozenDict(dict):
    """Immutable dictionary class"""
    def __setitem__(self, key, value):
        raise Exception("Cannot change value.")
    def update(self, dictlike):
        raise Exception("Cannot change value.")

    def extend(self, dictlike):
        return FrozenDict(itertools.chain(self.items(), dictlike.items()))

    def remove(self, *keys):
        return FrozenDict((k, v) for k, v in self.items() if k not in keys)


class Chunk(object):
    """A string with a single set of formatting attributes

    Subject to change, not part of the API"""
    def __init__(self, string, atts=()):
        if not isinstance(string, unicode):
            raise ValueError("unicode string required, got %r" % string)
        self._s = string
        self._atts = FrozenDict(atts)

    s = property(lambda self: self._s)  # resist changes to s and atts
    atts = property(lambda self: self._atts,
                    None, None,
                    "Attributes, e.g. {'fg': 34, 'bold': True} where 34 is the escape code for ...")

    def __len__(self):
        return len(self._s)

    @property
    def width(self):
        width = wcwidth.wcswidth(self._s)
        if len(self._s) > 0 and width < 1:
            raise ValueError("Can't calculate width of string %r" % self._s)
        return width

    #TODO cache this
    @property
    def color_str(self):
        "Return an escape-coded string to write to the terminal."
        s = self.s
        for k, v in sorted(self.atts.items()):
            # (self.atts sorted for the sake of always acting the same.)
            assert k in xforms, "XXX Do we actually get cases like this?"
            if v is False:
                continue
            elif v is True:
                s = xforms[k](s)
            else:
                s = xforms[k](s, v)
        return s

    def __unicode__(self):
        value = self.color_str
        if isinstance(value, bytes):
            return value.decode('utf8', 'replace')
        return value

    def __eq__(self, other):
        return self.s == other.s and self.atts == other.atts
    # TODO: corresponding hash method

    if PY3:
        __str__ = __unicode__
    else:
        def __str__(self):
            return unicode(self).encode('utf8')

    def __repr__(self):
        def pp_att(att):
            if att == 'fg': return FG_NUMBER_TO_COLOR[self.atts[att]]
            elif att == 'bg': return 'on_' + BG_NUMBER_TO_COLOR[self.atts[att]]
            else: return att
        atts_out = dict((k, v) for (k, v) in self.atts.items() if v)
        return (''.join(pp_att(att)+'(' for att in sorted(atts_out))
                + (repr(self.s) if PY3 else repr(self.s)[1:]) + ')'*len(atts_out))


class FmtStr(object):
    """ A string whose substrings carry attributes (which may be different from one to the next).  """
    def __init__(self, *components):
        # These assertions below could be useful for debugging, but slow things down considerably
        #assert all([len(x) > 0 for x in components])
        #self.basefmtstrs = [x for x in components if len(x) > 0]
        self.basefmtstrs = list(components)

        # caching these leads tom a significant speedup
        self._str = None
        self._unicode = None
        self._len = None
        self._s = None
        self._width = None

    @classmethod
    def from_str(cls, s):
        r"""
        Return a FmtStr representing input.

        The str() of a FmtStr is guaranteed to produced the same FmtStr.
        Other input with escape sequences may not be preserved.

        >>> fmtstr("|"+fmtstr("hey", fg='red', bg='blue')+"|")
        '|'+on_blue(red('hey'))+'|'
        >>> fmtstr('|\x1b[31m\x1b[44mhey\x1b[49m\x1b[39m|')
        '|'+on_blue(red('hey'))+'|'
        """

        if '\x1b[' in s:
            try:
                tokens_and_strings = parse(s)
            except ValueError:
                return FmtStr(Chunk(remove_ansi(s)))
            else:
                bases = []
                cur_fmt = {}
                for x in tokens_and_strings:
                    if isinstance(x, dict):
                        cur_fmt.update(x)
                    elif isinstance(x, (bytes, unicode)):
                        atts = parse_args('', dict((k, v)
                                          for k, v in cur_fmt.items()
                                          if v is not None))
                        bases.append(Chunk(x, atts=atts))
                    else:
                        raise Exception("logic error")
                return FmtStr(*bases)
        else:
            return FmtStr(Chunk(s))

    def copy_with_new_str(self, new_str):
        """Copies the current FmtStr's attributes while changing its string."""
        # What to do when there are multiple Chunks with conflicting atts?
        old_atts = dict((att, value) for bfs in self.basefmtstrs
                    for (att, value) in bfs.atts.items())
        return FmtStr(Chunk(new_str, old_atts))

    def setitem(self, startindex, fs):
        """Shim for easily converting old __setitem__ calls"""
        return self.setslice_with_length(startindex, startindex+1, fs, len(self))

    def setslice_with_length(self, startindex, endindex, fs, length):
        """Shim for easily converting old __setitem__ calls"""
        if len(self) < startindex:
            fs = ' '*(startindex - len(self)) + fs
        if len(self) > endindex:
            fs = fs + ' '*(endindex - startindex - len(fs))
            assert len(fs) == endindex - startindex, (len(fs), startindex, endindex)
        result = self.splice(fs, startindex, endindex)
        assert len(result) <= length
        return result

    def splice(self, new_str, start, end=None):
        """Returns a new FmtStr with the input string spliced into the
        the original FmtStr at start and end.
        If end is provided, new_str will replace the substring self.s[start:end-1].
        """
        if len(new_str) == 0:
            return self
        new_fs = new_str if isinstance(new_str, FmtStr) else fmtstr(new_str)
        assert len(new_fs.basefmtstrs) > 0, (new_fs.basefmtstrs, new_fs)
        new_components = []
        inserted = False
        if end is None:
            end = start
        tail = None

        for bfs, bfs_start, bfs_end in zip(self.basefmtstrs,
                                           self.divides[:-1],
                                           self.divides[1:]):
            if end == bfs_start == 0:
                new_components.extend(new_fs.basefmtstrs)
                new_components.append(bfs)
                inserted = True

            elif bfs_start <= start < bfs_end:
                divide = start - bfs_start
                head = Chunk(bfs.s[:divide], atts=bfs.atts)
                tail = Chunk(bfs.s[end - bfs_start:], atts=bfs.atts)
                new_components.extend([head] + new_fs.basefmtstrs)
                inserted = True

                if bfs_start < end < bfs_end:
                    tail = Chunk(bfs.s[end - bfs_start:], atts=bfs.atts)
                    new_components.append(tail)

            elif bfs_start < end < bfs_end:
                divide = start - bfs_start
                tail = Chunk(bfs.s[end - bfs_start:], atts=bfs.atts)
                new_components.append(tail)

            elif bfs_start >= end or bfs_end <= start:
                new_components.append(bfs)

        if not inserted:
            new_components.extend(new_fs.basefmtstrs)
            inserted = True

        return FmtStr(*[s for s in new_components if s.s])

    def append(self, string):
        return self.splice(string, len(self.s))

    def copy_with_new_atts(self, **attributes):
        """Returns a new FmtStr with the same content but new formatting"""
        return FmtStr(*[Chunk(bfs.s, bfs.atts.extend(attributes))
                        for bfs in self.basefmtstrs])

    def join(self, iterable):
        """Joins an iterable yielding strings or FmtStrs with self as separator"""
        before = []
        basefmtstrs = []
        for i, s in enumerate(iterable):
            basefmtstrs.extend(before)
            before = self.basefmtstrs
            if isinstance(s, FmtStr):
                basefmtstrs.extend(s.basefmtstrs)
            elif isinstance(s, (bytes, unicode)):
                basefmtstrs.extend(fmtstr(s).basefmtstrs) #TODO just make a basefmtstr directly
            else:
                raise TypeError("expected str or FmtStr, %r found" % type(s))
        return FmtStr(*basefmtstrs)

    # TODO make this split work like str.split
    def split(self, sep=None, maxsplit=None, regex=False):
        """Split based on seperator, optionally using a regex

        Capture groups are ignored in regex, the whole pattern is matched
        and used to split the original FmtStr."""
        if maxsplit is not None:
            raise NotImplementedError('no maxsplit yet')
        s = self.s
        if sep is None:
            sep = r'\s+'
        elif not regex:
            sep = re.escape(sep)
        matches = list(re.finditer(sep, s))
        return [self[start:end] for start, end in zip(
            [0] + [m.end() for m in matches],
            [m.start() for m in matches] + [len(s)])]

    # proxying to the string via __getattr__ is insufficient
    # because we shouldn't drop foreground or formatting info
    def ljust(self, width, fillchar=None):
        """S.ljust(width[, fillchar]) -> string

        If a fillchar is provided, less formatting information will be preserved
        """
        if fillchar is not None:
            return fmtstr(self.s.ljust(width, fillchar), **self.shared_atts)
        to_add = ' ' * (width - len(self.s))
        shared = self.shared_atts
        if 'bg' in shared:
            return self + fmtstr(to_add, bg=shared[str('bg')]) if to_add else self
        else:
            uniform = self.new_with_atts_removed('bg')
            return uniform + fmtstr(to_add, **self.shared_atts) if to_add else uniform

    def rjust(self, width, fillchar=None):
        """S.rjust(width[, fillchar]) -> string

        If a fillchar is provided, less formatting information will be preserved
        """
        if fillchar is not None:
            return fmtstr(self.s.rjust(width, fillchar), **self.shared_atts)
        to_add = ' ' * (width - len(self.s))
        shared = self.shared_atts
        if 'bg' in shared:
            return fmtstr(to_add, bg=shared[str('bg')]) + self if to_add else self
        else:
            uniform = self.new_with_atts_removed('bg')
            return fmtstr(to_add, **self.shared_atts) + uniform if to_add else uniform

    def __unicode__(self):
        if self._unicode is not None:
            return self._unicode
        self._unicode = ''.join(unicode(fs) for fs in self.basefmtstrs)
        return self._unicode

    if PY3:
        __str__ = __unicode__
    else:
        def __str__(self):
            if self._str is not None:
                return self._str
            self._str = str('').join(str(fs) for fs in self.basefmtstrs)
            return self._str

    def __len__(self):
        if self._len is not None:
            return self._len
        self._len = sum(len(fs) for fs in self.basefmtstrs)
        return self._len

    @property
    def width(self):
        """The number of columns it would take to display this string"""
        if self._width is not None:
            return self._width
        self._width = sum(fs.width for fs in self.basefmtstrs)
        return self._width

    def width_at_offset(self, n):
        """Returns the horizontal position of character n of the string"""
        #TODO make more efficient?
        width = wcwidth.wcswidth(self.s[:n])
        assert width != -1
        return width


    def __repr__(self):
        return '+'.join(repr(fs) for fs in self.basefmtstrs)

    def __eq__(self, other):
        if isinstance(other, (unicode, bytes, FmtStr)):
            return str(self) == str(other)
        return False
    # TODO corresponding hash method

    def __add__(self, other):
        if isinstance(other, FmtStr):
            return FmtStr(*(self.basefmtstrs + other.basefmtstrs))
        elif isinstance(other, (bytes, unicode)):
            return FmtStr(*(self.basefmtstrs + [Chunk(other)]))
        else:
            raise TypeError('Can\'t add %r and %r' % (self, other))

    def __radd__(self, other):
        if isinstance(other, FmtStr):
            return FmtStr(*(x for x in (other.basefmtstrs + self.basefmtstrs)))
        elif isinstance(other, (bytes, unicode)):
            return FmtStr(*(x for x in ([Chunk(other)] + self.basefmtstrs)))
        else:
            raise TypeError('Can\'t add those')

    def __mul__(self, other):
        if isinstance(other, int):
            return sum([self for _ in range(other)], FmtStr())
        raise TypeError('Can\'t mulitply those')
    #TODO ensure emtpy FmtStr isn't a problem

    @property
    def shared_atts(self):
        """Gets atts shared among all nonzero length component Chunk"""
        #TODO cache this, could get ugly for large FmtStrs
        atts = {}
        first = self.basefmtstrs[0]
        for att in sorted(first.atts):
            #TODO how to write this without the '???'?
            if all(fs.atts.get(att, '???') == first.atts[att] for fs in self.basefmtstrs if len(fs) > 0):
                atts[att] = first.atts[att]
        return atts

    def new_with_atts_removed(self, *attributes):
        """Returns a new FmtStr with the same content but some attributes removed"""
        return FmtStr(*[Chunk(bfs.s, bfs.atts.remove(*attributes))
                        for bfs in self.basefmtstrs])

    def __getattr__(self, att):
        # thanks to @aerenchyma/@jczett
        if not hasattr(self.s, att):
            raise AttributeError("No attribute %r" % (att,))
        def func_help(*args, **kwargs):
             result = getattr(self.s, att)(*args, **kwargs)
             if isinstance(result, (bytes, unicode)):
                 return fmtstr(result, **self.shared_atts)
             elif isinstance(result, list):
                 return [fmtstr(x, **self.shared_atts) for x in result]
             else:
                 return result
        return func_help

    @property
    def divides(self):
        """List of indices of divisions between the constituent basefmtstrs"""
        acc = [0]
        for s in self.basefmtstrs:
            acc.append(acc[-1] + len(s))
        return acc

    @property
    def s(self):
        if self._s is not None:
            return self._s
        self._s = "".join(fs.s for fs in self.basefmtstrs)
        return self._s

    def __getitem__(self, index):
        index = normalize_slice(len(self), index)
        counter = 0
        parts = []
        for chunk in self.basefmtstrs:
            if index.start < counter + len(chunk) and index.stop > counter:
                start = max(0, index.start - counter)
                end = min(index.stop - counter, len(chunk))
                if end - start == len(chunk):
                    parts.append(chunk)
                else:
                    s_part = chunk.s[max(0, index.start - counter): index.stop - counter]
                    parts.append(Chunk(s_part, chunk.atts))
            counter += len(chunk)
            if index.stop < counter:
                break
        return FmtStr(*parts) if parts else fmtstr('')

    def width_aware_slice(self, index):
        """Slice based on the number of columns it would take to display the substring"""
        if wcwidth.wcswidth(self.s) == -1:
            raise ValueError('bad values for width aware slicing')
        index = normalize_slice(self.width, index)
        counter = 0
        parts = []
        for chunk in self.basefmtstrs:
            if index.start < counter + chunk.width and index.stop > counter:
                start = max(0, index.start - counter)
                end = min(index.stop - counter, chunk.width)
                if end - start == chunk.width:
                    parts.append(chunk)
                else:
                    s_part = width_aware_slice(chunk.s, max(0, index.start - counter), index.stop - counter)
                    parts.append(Chunk(s_part, chunk.atts))
            counter += chunk.width
            if index.stop < counter:
                break
        return FmtStr(*parts) if parts else fmtstr('')

    def _getitem_normalized(self, index):
        """Builds the more compact fmtstrs by using fromstr( of the control sequences)"""
        index = normalize_slice(len(self), index)
        counter = 0
        output = ''
        for fs in self.basefmtstrs:
            if index.start < counter + len(fs) and index.stop > counter:
                s_part = fs.s[max(0, index.start - counter):index.stop - counter]
                piece = Chunk(s_part, fs.atts).color_str
                output += piece
            counter += len(fs)
            if index.stop < counter:
                break
        return fmtstr(output)

    def __setitem__(self, index, value):
        raise Exception("No!")

    def copy(self):
        return FmtStr(*self.basefmtstrs)


def interval_overlap(a, b, x, y):
    """Returns by how much two intervals overlap

    assumed that a <= b and x <= y"""
    if b <= x or a >= y:
        return 0
    elif x <= a <= y:
        return min(b, y) - a
    elif x <= b <= y:
        return b - max(a, x)
    elif a >= x and b <= y:
        return b - a
    else:
        assert False


def width_aware_slice(s, start, end, replacement_char=u' '):
    divides = [wcwidth.wcswidth(s, i) for i in range(len(s)+1)]

    new_chunk_chars = []
    for char, char_start, char_end in zip(s, divides[:-1], divides[1:]):
        if char_start >= start and char_end <= end:
            new_chunk_chars.append(char)
        else:
            new_chunk_chars.extend(replacement_char * interval_overlap(char_start, char_end, start, end))

    return ''.join(new_chunk_chars)


def linesplit(string, columns):
    """Returns a list of lines, split on the last possible space of each line.

    Split spaces will be removed. Whitespaces will be normalized to one space.
    Spaces will be the color of the first whitespace character of the
    normalized whitespace.
    If a word extends beyond the line, wrap it anyway.

    >>> linesplit(fmtstr(" home    is where the heart-eating mummy is", 'blue'), 10)
    [blue('home')+blue(' ')+blue('is'), blue('where')+blue(' ')+blue('the'), blue('heart-eati'), blue('ng')+blue(' ')+blue('mummy'), blue('is')]
    """
    if not isinstance(string, FmtStr):
        string = fmtstr(string)

    string_s = string.s
    matches = list(re.finditer(r'\s+', string_s))
    spaces = [string[m.start():m.end()] for m in matches if m.start() != 0 and m.end() != len(string_s)]
    words = [string[start:end] for start, end in zip(
            [0] + [m.end() for m in matches],
            [m.start() for m in matches] + [len(string_s)]) if start != end]

    word_to_lines = lambda word: [word[columns*i:columns*(i+1)] for i in range((len(word) - 1) // columns + 1)]

    lines = word_to_lines(words[0])
    for word, space in zip(words[1:], spaces):
        if len(lines[-1]) + len(word) < columns:
            lines[-1] += fmtstr(' ', **space.shared_atts)
            lines[-1] += word
        else:
            lines.extend(word_to_lines(word))
    return lines

def normalize_slice(length, index):
    "Fill in the Nones in a slice."
    is_int = False
    if isinstance(index, int):
        is_int = True
        index = slice(index, index+1)
    if index.start is None:
        index = slice(0, index.stop, index.step)
    if index.stop is None:
        index = slice(index.start, length, index.step)
    if index.start < -1:         # XXX why must this be -1?
        index = slice(length - index.start, index.stop, index.step)
    if index.stop < -1:          # XXX why must this be -1?
        index = slice(index.start, length - index.stop, index.step)
    if index.step is not None:
        raise NotImplementedError("You can't use steps with slicing yet")
    if is_int:
        if index.start < 0 or index.start > length:
            raise IndexError("index out of bounds: %r for length %s" % (index, length))
    return index

def parse_args(args, kwargs):
    """Returns a kwargs dictionary by turning args into kwargs"""
    if 'style' in kwargs:
        args += (kwargs['style'],)
        del kwargs['style']
    for arg in args:
        if not isinstance(arg, (bytes, unicode)):
            raise ValueError("args must be strings:" + repr(args))
        if arg.lower() in FG_COLORS:
            if 'fg' in kwargs: raise ValueError("fg specified twice")
            kwargs['fg'] = FG_COLORS[arg]
        elif arg.lower().startswith('on_') and arg[3:].lower() in BG_COLORS:
            if 'bg' in kwargs: raise ValueError("fg specified twice")
            kwargs['bg'] = BG_COLORS[arg[3:]]
        elif arg.lower() in STYLES:
            kwargs[arg] = True
        else:
            raise ValueError("couldn't process arg: "+repr(arg))
    for k in kwargs:
        if k not in ['fg', 'bg'] + list(STYLES.keys()):
            raise ValueError("Can't apply that transformation")
    if 'fg' in kwargs:
        if kwargs['fg'] in FG_COLORS:
            kwargs['fg'] = FG_COLORS[kwargs['fg']]
        if kwargs['fg'] not in list(FG_COLORS.values()):
            raise ValueError("Bad fg value: %r" % kwargs['fg'])
    if 'bg' in kwargs:
        if kwargs['bg'] in BG_COLORS:
            kwargs['bg'] = BG_COLORS[kwargs['bg']]
        if kwargs['bg'] not in list(BG_COLORS.values()):
            raise ValueError("Bad bg value: %r" % kwargs['bg'])
    return kwargs

def fmtstr(string, *args, **kwargs):
    """
    Convenience function for creating a FmtStr

    >>> fmtstr('asdf', 'blue', 'on_red', 'bold')
    on_red(bold(blue('asdf')))
    >>> fmtstr('blarg', fg='blue', bg='red', bold=True)
    on_red(bold(blue('blarg')))
    """
    atts = parse_args(args, kwargs)
    if isinstance(string, FmtStr):
        pass
    elif isinstance(string, (bytes, unicode)):
        string = FmtStr.from_str(string)
    else:
        raise ValueError("Bad Args: %r (of type %s), %r, %r" % (string, type(string), args, kwargs))
    return string.copy_with_new_atts(**atts)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    #f = FmtStr.from_str(str(fmtstr('tom', 'blue')))
    #print((repr(f)))
    #f = fmtstr('stuff', fg='blue', bold=True)
    #print((repr(f)))

