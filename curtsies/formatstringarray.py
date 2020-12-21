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
import logging

from .formatstring import fmtstr
from .formatstring import normalize_slice
from .formatstring import FmtStr

from typing import (
    Any,
    Union,
    Text,
    List,
    Sequence,
    overload,
    Tuple,
    cast,
    no_type_check,
)

actualize = str
logger = logging.getLogger(__name__)

# TODO check that strings used in arrays don't have tabs or spaces in them!


def slicesize(s):
    # type: (slice) -> int
    return int((s.stop - s.start) / (s.step if s.step else 1))


def fsarray(strings, *args, **kwargs):
    # type: (List[Union[FmtStr, Text]], *Any, **Any) -> FSArray
    """fsarray(list_of_FmtStrs_or_strings, width=None) -> FSArray

    Returns a new FSArray of width of the maximum size of the provided
    strings, or width provided, and height of the number of strings provided.
    If a width is provided, raises a ValueError if any of the strings
    are of length greater than this width"""

    strings = list(strings)
    if "width" in kwargs:
        width = kwargs["width"]
        del kwargs["width"]
        if strings and any(len(s) > width for s in strings):
            raise ValueError(f"Those strings won't fit for width {width}")
    else:
        width = max(len(s) for s in strings) if strings else 0
    fstrings = [
        s if isinstance(s, FmtStr) else fmtstr(s, *args, **kwargs) for s in strings
    ]
    arr = FSArray(len(fstrings), width, *args, **kwargs)
    rows = [
        fs.setslice_with_length(0, len(s), s, width)
        for fs, s in zip(arr.rows, fstrings)
    ]
    arr.rows = rows
    return arr


class FSArray(Sequence):
    """A 2D array of colored text.

    Internally represented by a list of FmtStrs of identical size."""

    # TODO add constructor that takes fmtstrs instead of dims
    def __init__(self, num_rows, num_columns, *args, **kwargs):
        # type: (int, int, *Any, **Any) -> None
        self.saved_args, self.saved_kwargs = args, kwargs
        self.rows = [
            fmtstr("", *args, **kwargs) for _ in range(num_rows)
        ]  # type: List[FmtStr]
        self.num_columns = num_columns

    @overload
    def __getitem__(self, slicetuple):
        # type: (int) -> FmtStr
        pass

    @overload
    def __getitem__(self, slicetuple):
        # type: (slice) -> List[FmtStr]
        pass

    @overload
    def __getitem__(self, slicetuple):
        # type: (Tuple[Union[slice, int], Union[slice, int]]) -> List[FmtStr]
        pass

    def __getitem__(self, slicetuple):
        # type: (Union[int, slice, Tuple[Union[int, slice], Union[int, slice]]]) -> Union[FmtStr, List[FmtStr]]
        if isinstance(slicetuple, int):
            if slicetuple < 0:
                slicetuple = len(self.rows) - slicetuple
            if slicetuple < 0 or slicetuple >= len(self.rows):
                raise IndexError("out of bounds")
            return self.rows[slicetuple]
        if isinstance(slicetuple, slice):
            rowslice = normalize_slice(len(self.rows), slicetuple)
            return self.rows[rowslice]
        (
            row_slice_or_int,
            col_slice_or_int,
        ) = slicetuple  # type: Tuple[Union[int, slice], Union[int, slice]]
        rowslice = normalize_slice(len(self.rows), row_slice_or_int)
        colslice = normalize_slice(self.num_columns, col_slice_or_int)
        # TODO clean up slices
        return [fs[colslice] for fs in self.rows[rowslice]]

    def __len__(self):
        # type: () -> int
        return len(self.rows)

    @property
    def shape(self):
        # type: () -> Tuple[int, int]
        """Tuple of (len(rows, len(num_columns)) numpy-style shape"""
        return len(self.rows), self.num_columns

    @property
    def height(self):
        # type: () -> int
        """The number of rows"""
        return len(self.rows)

    @property
    def width(self):
        # type: () -> int
        """The number of columns"""
        return self.num_columns

    # TODO rework this next major version bump
    @no_type_check
    def __setitem__(self, slicetuple, value):
        """Place a FSArray in a FSArray"""
        logger.debug("slice: %r", slicetuple)
        if isinstance(slicetuple, slice):
            rowslice, colslice = slicetuple, slice(None)
            if isinstance(value, (bytes, str)):
                raise ValueError(
                    "if slice is 2D, value must be 2D as in of list type []"
                )
        elif isinstance(slicetuple, int):
            normalize_slice(self.height, slicetuple)
            self.rows[slicetuple] = value
            return
        else:
            rowslice, colslice = slicetuple

        # temp shim to allow numpy arrays as values
        if value.__class__.__name__ == "ndarray":
            value = [fmtstr("".join(line)) for line in value]

        rowslice = normalize_slice(sys.maxsize, rowslice)
        additional_rows = max(0, rowslice.stop - len(self.rows))
        self.rows.extend(
            [
                fmtstr("", *self.saved_args, **self.saved_kwargs)
                for _ in range(additional_rows)
            ]
        )
        logger.debug("num columns: %r", self.num_columns)
        logger.debug("colslice: %r", colslice)
        colslice = normalize_slice(self.num_columns, colslice)
        if slicesize(colslice) == 0 or slicesize(rowslice) == 0:
            return
        if slicesize(colslice) > 1 and isinstance(value, str):
            raise ValueError(
                """You cannot replace a multi column slice with a 
                string please use a list [] with strings for the 
                contents of each row"""
            )
        if slicesize(rowslice) != len(value):
            area = slicesize(rowslice) * slicesize(colslice)
            val_len = sum(len(i) for i in value)
            grid_value = [fmtstr(" ", bg="cyan") * slicesize(colslice)] * slicesize(
                rowslice
            )
            grid_fsarray = (
                self.rows[: rowslice.start]
                + [
                    fs.setslice_with_length(
                        colslice.start, colslice.stop, v, self.num_columns
                    )
                    for fs, v in zip(self.rows[rowslice], grid_value)
                ]
                + self.rows[rowslice.stop :]
            )
            msg = "You are trying to fit this value {} into the region {}: {}".format(
                fmtstr("".join(value), bg="cyan"),
                fmtstr("").join(grid_value),
                "\n ".join(grid_fsarray[x] for x in range(len(self.rows))),
            )
            raise ValueError(
                """Error you are trying to replace a region of {} rows by {}
                columns for and area of {} with a value of len {}. The value
                used to replace the region must equal the area of the region
                replace.
                {}""".format(
                    rowslice.stop - rowslice.start,
                    colslice.stop - colslice.start,
                    area,
                    val_len,
                    msg,
                )
            )
        self.rows = (
            self.rows[: rowslice.start]
            + [
                fs.setslice_with_length(
                    colslice.start, colslice.stop, v, self.num_columns
                )
                for fs, v in zip(self.rows[rowslice], value)
            ]
            + self.rows[rowslice.stop :]
        )

    def dumb_display(self):
        # type: () -> None
        """Prints each row followed by a newline without regard for the terminal window size"""
        for line in self.rows:
            print(line)

    @classmethod
    def diff(cls, a, b, ignore_formatting=False):
        # type: (FSArray, FSArray, bool) -> Text
        """Returns two FSArrays with differences underlined"""

        def underline(x):
            # type: (Text) -> Text
            return f"\x1b[4m{x}\x1b[0m"

        def blink(x):
            # type: (Text) -> Text
            return f"\x1b[5m{x}\x1b[0m"

        a_rows = []
        b_rows = []
        max_width = max([len(row) for row in a] + [len(row) for row in b])
        a_lengths = []
        b_lengths = []
        for a_row, b_row in zip(a, b):
            a_lengths.append(len(a_row))
            b_lengths.append(len(b_row))
            extra_a = "`" * (max_width - len(a_row))
            extra_b = "`" * (max_width - len(b_row))
            a_line = ""
            b_line = ""
            for a_char, b_char in zip(a_row + extra_a, b_row + extra_b):
                if ignore_formatting:
                    a_char_for_eval = a_char.s if isinstance(a_char, FmtStr) else a_char
                    b_char_for_eval = b_char.s if isinstance(b_char, FmtStr) else b_char
                else:
                    a_char_for_eval = a_char
                    b_char_for_eval = b_char
                if a_char_for_eval == b_char_for_eval:
                    a_line += actualize(a_char)
                    b_line += actualize(b_char)
                else:
                    a_line += underline(blink(actualize(a_char)))
                    b_line += underline(blink(actualize(b_char)))
            a_rows.append(a_line)
            b_rows.append(b_line)
        hdiff = "\n".join(
            a_line + " %3d | %3d " % (a_len, b_len) + b_line
            for a_line, b_line, a_len, b_len in zip(
                a_rows, b_rows, a_lengths, b_lengths
            )
        )
        return hdiff


def simple_format(x):
    # type: (Union[FSArray, List[FmtStr]]) -> Text
    return "\n".join(actualize(l) for l in x)


if __name__ == "__main__":
    a = FSArray(3, 14, bg="blue")
    a[0:2, 5:11] = cast(
        Tuple[FmtStr, ...],
        (fmtstr("hey", "on_blue") + " " + fmtstr("yo", "on_red"), fmtstr("qwe qw")),
    )
    a.dumb_display()

    a = fsarray(["hey", "there"], bg="cyan")
    a.dumb_display()
    print(FSArray.diff(a, fsarray(["hey", "there "]), ignore_formatting=True))
