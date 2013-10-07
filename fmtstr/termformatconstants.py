"""Constants for terminal formatting"""

colors = 'dark', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray'
FG_COLORS = dict(list(zip(colors, list(range(30, 38)))))
BG_COLORS = dict(list(zip(colors, list(range(40, 48)))))
STYLES = dict(list(zip(('bold', 'dark', 'underline', 'blink', 'invert'), [1,2,4,5,7])))
FG_NUMBER_TO_COLOR = dict(zip(FG_COLORS.values(), FG_COLORS.keys()))
BG_NUMBER_TO_COLOR = dict(zip(BG_COLORS.values(), BG_COLORS.keys()))
NUMBER_TO_STYLE = dict(zip(STYLES.values(), STYLES.keys()))
RESET_ALL = 0
RESET_FG = 39
RESET_BG = 49

def seq(num):
    return '[%sm' % num

