"""Terminal-formatted strings"""
__version__='0.1.23'

from .window import FullscreenWindow, CursorAwareWindow
from .input import Input
from .termhelpers import Nonblocking, Cbreak, Termmode
from .formatstring import FmtStr, fmtstr
from .formatstringarray import FSArray, fsarray

