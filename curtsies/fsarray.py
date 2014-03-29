"""
Format String 2D array
2d array for compositing term-formated strings


-autoexpanding vertically
-interesting get_item behavior (renders fmtstrs)
-caching behavior eventually


>>> a = FSArray(10, 14)
>>> a.shape
(10, 14)
>>> a[1] = 'i'
>>> a[3:4, :] = ['i' * 14]
>>> a[16:17, :] = ['j' * 14]
>>> a.shape, a[16, 0]
((17, 14), ['j'])
>>> a[200, 1] = ['i']
>>> a[200, 1]
['i']
"""

import sys

from .fmtstr import fmtstr
from .fmtstr import normalize_slice
from .fmtstr import FmtStr

def slicesize(s):
    return int((s.stop - s.start) / (s.step if s.step else 1))

def fsarray(strings, *args, **kwargs):
    """fsarray(list_of_FmtStrs_or_strings, width=None) -> FSArray

    Returns a new FSArray of width of the maximum size of the provided
    strings, or width provided, and height of the number of strings provided.
    If a width is provided, raises a ValueError if any of the strings
    are of length greater than this width"""

    if 'width' in kwargs:
        width = kwargs['width']
        del kwargs['width']
        if strings and max(len(s) for s in strings) > width:
            raise ValueError("Those strings won't fit for width %d" % width)
    else:
        width = max(len(s) for s in strings) if strings else 0
    fstrings = [s if isinstance(s, FmtStr) else fmtstr(s, *args, **kwargs) for s in strings]
    arr = FSArray(len(fstrings), width, *args, **kwargs)
    rows = [fs.setslice_with_length(0, len(s), s, width) for fs, s in zip(arr.rows, fstrings)]
    arr.rows = rows
    return arr

class FSArray(object):
    """A 2D array of colored text.

    Internally represented by a list of FmtStrs of identical size."""

    #TODO add constructor that takes fmtstrs instead of dims
    def __init__(self, num_rows, num_columns, *args, **kwargs):
        self.saved_args, self.saved_kwargs = args, kwargs
        self.rows = [fmtstr('', *args, **kwargs) for _ in range(num_rows)]
        self.num_columns = num_columns

    def __getitem__(self, slicetuple):
        if isinstance(slicetuple, int):
            if slicetuple < 0:
                slicetuple = len(self.rows) - slicetuple
            if slicetuple < 0 or slicetuple >= len(self.rows):
                raise IndexError('out of bounds')
            return self.rows[slicetuple]
        if isinstance(slicetuple, slice):
            rowslice = normalize_slice(len(self.rows), slicetuple)
            return self.rows[rowslice]
        rowslice, colslice = slicetuple
        rowslice = normalize_slice(len(self.rows), rowslice)
        colslice = normalize_slice(self.num_columns, colslice)
        #TODO clean up slices
        return [fs[colslice] for fs in self.rows[rowslice]]

    def __len__(self):
        return len(self.rows)

    @property
    def shape(self):
        """tuple of (len(rows, len(num_columns)) numpy-style shape"""
        return len(self.rows), self.num_columns

    height = property(lambda self: len(self.rows))
    width = property(lambda self: self.num_columns)

    def __setitem__(self, slicetuple, value):
        if isinstance(slicetuple, slice):
            rowslice, colslice = slicetuple, slice(None)
            if isinstance(value, (bytes, unicode)):
                raise ValueError('if slice is 2D, value must be 2D')
        elif isinstance(slicetuple, int):
            normalize_slice(self.height, slicetuple)
            self.rows[slicetuple] = value
            return
        else:
            rowslice, colslice = slicetuple

        # temp shim to allow numpy arrays as values
        if value.__class__.__name__ == 'ndarray':
            value = [fmtstr(''.join(line)) for line in value]

        rowslice = normalize_slice(sys.maxsize, rowslice)
        additional_rows = max(0, rowslice.stop - len(self.rows))
        self.rows.extend([fmtstr('', *self.saved_args, **self.saved_kwargs)
                          for _ in range(additional_rows)])
        colslice = normalize_slice(self.num_columns, colslice)
        if slicesize(colslice) == 0 or slicesize(rowslice) == 0:
            return
        if slicesize(rowslice) != len(value):
            raise ValueError('row dimensions do not match: %r, %r' % (len(value), rowslice))
        self.rows = (self.rows[:rowslice.start] +
                     [fs.setslice_with_length(colslice.start, colslice.stop, v, self.num_columns) for fs, v in zip(self.rows[rowslice], value)] +
                     self.rows[rowslice.stop:])

    def dumb_display(self):
        """Prints rows, one per line"""
        for line in self.rows:
            print(line)


if __name__ == '__main__':
    a = FSArray(3, 14, bg='blue')
    a[0:2, 5:11] = fmtstr("hey", 'on_blue') + ' ' + fmtstr('yo', 'on_red'), fmtstr('qwe qw')
    a.dumb_display()

    a = fsarray(['hey', 'there'], bg='cyan')
    a.dumb_display()
