from curtsies import input
from curtsies.fmtstr import fmtstr
from curtsies import events
from curtsies.window import FullscreenWindow, CursorAwareWindow
import sys
import signal
import logging
from curtsies.termhelpers import Cbreak

from demo_window import array_size_test

if __name__ == '__main__':
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    array_size_test(FullscreenWindow(sys.stdout))
