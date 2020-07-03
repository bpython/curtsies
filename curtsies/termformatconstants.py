"""Constants for terminal formatting"""

from typing import Mapping

# fmt: off
colors = 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray'
FG_COLORS = dict(list(zip(colors, list(range(30, 38)))))  # type: Mapping[str, int]
BG_COLORS = dict(list(zip(colors, list(range(40, 48)))))  # type: Mapping[str, int]
STYLES = dict(list(zip(('bold', 'dark', 'underline', 'blink', 'invert'), [1,2,4,5,7])))  # type: Mapping[str, int]
FG_NUMBER_TO_COLOR = dict(zip(FG_COLORS.values(), FG_COLORS.keys()))  # type: Mapping[int, str]
BG_NUMBER_TO_COLOR = dict(zip(BG_COLORS.values(), BG_COLORS.keys()))  # type: Mapping[int, str]
NUMBER_TO_STYLE = dict(zip(STYLES.values(), STYLES.keys()))
RESET_ALL = 0
RESET_FG = 39
RESET_BG = 49
# fmt: on


def seq(num):
    # type: (int) -> str
    return "[%sm" % num
