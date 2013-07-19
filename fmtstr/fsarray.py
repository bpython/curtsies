"""
Format String 2D array
2d array for compositing term-formated strings


-autoexpanding vertically
-interesting get_item behavior (renders fmtstrs)
-caching behavior eventually


#>>> a = FSArray(10, 14)
#>>> a.shape
#(10, 14)
#>>> a[1] = 'i'
#>>> a[3:4, :] = 'i' * 14
#>>> a[16:17, :] = 'j' * 14
#>>> a.shape, a[16, 0]
#((17, 14), 'j')
#>>> a[200, 1] = 'i'
#>>> a[200, 1]
#'i'
#>>> a[3:4, 3:5] = 'ii'

>>> a = FSArray(5, 10)
>>> a.rows[0] = []
"""


from fmtstr import fmtstr
from fmtstr import normalize_slice

def slicesize(s):
    return int((s.stop - s.start) / (s.step if s.step else 1))

class FSArray(object):
    #TODO add constructor that takes fmtstrs instead of dims
    def __init__(self, rows, columns, *args, **kwargs):
        self.saved_args, self.saved_kwargs = args, kwargs
        self.rows = [fmtstr(' '*columns, *args, **kwargs) for _ in range(rows)]
        self.columns = columns

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
        colslice = normalize_slice(self.columns, colslice)
        #TODO clean up slices
        return [fs[colslice] for fs in self.rows[rowslice]]

    def __len__(self):
        return len(self.rows)

    @property
    def shape(self):
        return len(self.rows), self.columns

    def __setitem__(self, slicetuple, value):
        if isinstance(slicetuple, slice):
            rowslice, colslice = slicetuple, slice(None)
        else:
            rowslice, colslice = slicetuple

        # temp shim
        if value.__class__.__name__ == 'ndarray':
            value = [fmtstr(''.join(line)) for line in value]

        rowslice = normalize_slice(len(self.rows), rowslice)
        additional_rows = max(0, rowslice.stop - len(self.rows))
        self.rows.extend([fmtstr(' '*self.columns, *self.saved_args, **self.saved_kwargs)
                          for _ in range(additional_rows)])
        colslice = normalize_slice(self.columns, colslice)
        assert slicesize(rowslice) == len(value)
        for fs, v in zip(self.rows[rowslice], value):
            fs[colslice] = v

    def dumb_display(self):
        for line in self.rows:
            print line


if __name__ == '__main__':
    a = FSArray(10, 80, bg='blue')
    a[0:2, 5:11] = fmtstr("hey", 'on_blue') + ' ' + fmtstr('yo', 'on_red'), fmtstr('qwe qw')
    a.dumb_display()
