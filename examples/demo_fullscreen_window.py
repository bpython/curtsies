import sys
import signal
import logging

from curtsies import input, fmtstr, FullscreenWindow, CursorAwareWindow, Cbreak
from curtsies import events

from demo_window import array_size_test
"""
Reads input from user and prints an entire screen, one line less than a full screen, 
or one line more than the full screen
"""

if __name__ == '__main__':
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    array_size_test(FullscreenWindow(sys.stdout))
