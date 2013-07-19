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

def slicesize(s):
    return int((s.stop - s.start) / (s.step if s.step else 1))

class FSArray(object):
    def __init__(self, rows, columns, *args, **kwargs):
        self.rows = [fmtstr(' '*columns, *args, **kwargs) for _ in range(rows)]
        self.columns = columns

    def __getitem__(self, slicetuple):
        if len(slicetuple) == 1:
            return self.rows[slicetuple]
        rowslice, colslice = slicetuple
        #TODO clean up slices
        return [fs[colslice] for fs in self.rows[rowslice]]

    @property
    def shape(self):
        return len(self.rows), self.columns

    def __setitem__(self, slicetuple, value):
        if len(slicetuple) == 1:
            rowslice, colslice = slicetuple, slice(None)
        else:
            rowslice, colslice = slicetuple
        assert slicesize(rowslice) == len(value)
        for fs, v in zip(self.rows, value):
            fs[colslice] = v

    def dumb_display(self):
        for line in self.rows:
            print line


if __name__ == '__main__':
    a = FSArray(10, 80, bg='blue')
    a[0:2, 5:11] = fmtstr("hey", 'on_blue') + ' ' + fmtstr('yo', 'on_red'), fmtstr('qwe qw')
    a.dumb_display()

