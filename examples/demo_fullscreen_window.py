import sys
import signal
import logging

from curtsies import input, fmtstr, FullscreenWindow, CursorAwareWindow, Cbreak
from curtsies import events

from demo_window import array_size_test

if __name__ == '__main__':
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    array_size_test(FullscreenWindow(sys.stdout))
