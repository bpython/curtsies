"""Terminal-formatted strings"""
__version__='0.2.10'

from .window import FullscreenWindow, CursorAwareWindow
from .input import Input
from .termhelpers import Nonblocking, Cbreak, Termmode
from .formatstring import FmtStr, fmtstr
from .formatstringarray import FSArray, fsarray

