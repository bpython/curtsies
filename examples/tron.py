import time
import sys

from curtsies import FullscreenWindow, Input, FSArray, fmtstr, fsarray
from curtsies.fmtfuncs import (
    bold,
    yellow,
    on_blue,
    cyan,
    on_yellow,
    on_red,
    black,
)
import curtsies.events


class Cycle:
    def __init__(self, attr_dict):
        self.appearance = attr_dict["appearance"]
        self.x, self.y = attr_dict["x"], attr_dict["y"]
        self.keylist = attr_dict["keys"]
        self.dir = 0

    def move(self, grid):
        d = self.dir
        if d == 0:
            self.x += 1
        elif d == 90:
            self.y -= 1
        elif d == 180:
            self.x -= 1
        elif d == 270:
            self.y += 1

    def face(self, newdir):
        """ turn to face the given direction """
        if not (newdir % 180 == self.dir % 180):
            self.dir = newdir

    def paint(self, grid):
        """ given a grid object, adds self to the grid and returns new grid
        """
        grid[self.y, self.x] = self.appearance
        return grid


class Bot(Cycle):
    """ Dumb bot that only turns right when it's about to crash
    """

    def move(self, grid):

        a = self.getNextSquareCoords()
        if grid[a[0], a[1]] != [" "]:
            self.turnLeft()
        super().move(grid)

    def turnRight(self):
        self.dir = (self.dir - 90) % 360

    def turnLeft(self):
        self.dir = (self.dir + 90) % 360

    def getNextSquareCoords(self, n=2):
        """ Returns the x, y coords of the box n spots in front of the bot.
        """
        if self.dir == 0:
            return (self.y, self.x + n)
        elif self.dir == 90:
            return (self.y - n, self.x)
        elif self.dir == 180:
            return (self.y, self.x - n)
        else:
            return (self.y + n, self.x)


class gameboard:
    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.grid = FSArray(height, width)

        self.players = players
        self.numplayers = len(self.players)

    def draw_border(self):
        """ draw outer border """
        box = on_yellow(black(bold("!")))
        for x in range(1, self.width):
            self.grid[1, x] = box
            self.grid[self.height - 1, x] = box
        for y in range(1, self.height):
            self.grid[y, 1] = box
            self.grid[y, self.width - 1] = box

    def process_event(self, key):
        if key == " ":
            sys.exit()

        for player in self.players:
            if key in player.keylist:
                player.face(player.keylist[key])
                return False

    def tick(self):
        """ Do one frame of work. Returns the winner if there 
        is a crash
        """
        # list of players alive this frame
        temp_players = self.players[:]

        for bike in self.players:
            bike.move(self.grid)

            if self.grid[bike.y, bike.x] == [" "]:
                self.grid[bike.y, bike.x] = bike.appearance
            else:  # crashed
                temp_players.remove(bike)
                self.grid[bike.y, bike.x] = fmtstr("X", "red", "bold", "on_black")

        if len(temp_players) == 0:
            return "tie"
        elif len(temp_players) < len(self.players):
            return temp_players

    def winner_msg(self, tick):
        if len(tick) != 1:
            msg = fmtstr("it's a tie!", "red")
        else:
            winner = tick[0]
            winner_name = winner.appearance
            msg = fmtstr("winner:", "yellow")
            msg += " " + (winner_name * 5)
        return msg


class Frame(curtsies.events.ScheduledEvent):
    pass


def do_introduction(window):
    h, w = window.height, window.width

    messages = [
            "two player tron",
            fmtstr("player 1:", "on_blue", "cyan") + " wasd",
            fmtstr("player 2:", "on_red", "yellow") + " arrow keys",
        ]

    billboard = FSArray(h, w)
    msg_row = h // 2 - 2
    for msg in messages:
        billboard[
            msg_row, w // 2 - len(msg) // 2 : w // 2 + len(msg) // 2 + 1
        ] = fsarray([msg])
        msg_row += 1
    window.render_to_terminal(billboard)

    # countdown msg
    for i in range(3, 0, -1):
        billboard[msg_row, w // 2] = fmtstr(str(i), "red")
        window.render_to_terminal(billboard)
        time.sleep(1)


def mainloop(window, p2_bot=False):
    p1_attrs = {
        "appearance": on_blue(cyan("1")),
        "x": window.width // 4,
        "y": window.height // 2,
        "keys": {"w": 90, "a": 180, "s": 270, "d": 0},
    }

    p2_attrs = {
        "appearance": on_red(yellow("2")),
        "x": 3 * window.width // 4,
        "y": window.height // 2,
        "keys": {"<UP>": 90, "<LEFT>": 180, "<DOWN>": 270, "<RIGHT>": 0},
    }

    FPS = 15

    players = [Cycle(p1_attrs), Cycle(p2_attrs)]
    if p2_bot: # make p2 a bot
        players[1] = Bot(p2_attrs)

    world = gameboard(window.width, window.height, players)
    dt = 1 / FPS
    world.draw_border()
    window.render_to_terminal(world.grid)

    reactor = Input()
    schedule_next_frame = reactor.scheduled_event_trigger(Frame)
    schedule_next_frame(when=time.time())
    with reactor:
        for c in reactor:
            if isinstance(c, Frame):
                tick = world.tick()
                window.render_to_terminal(world.grid)
                if not tick:  # if no crashes
                    when = c.when + dt
                    while when < time.time():
                        when += dt
                    schedule_next_frame(when)
                else:  # if crashed
                    world.grid[0:4, 0:25] = fsarray(
                        [
                            world.winner_msg(tick),
                            "r to restart",
                            "q to quit",
                            "b to make player 2 a bot",
                        ]
                    )
                    window.render_to_terminal(world.grid)
            elif c.lower() in ["r", "q", "b"]:
                break
            else:  # common case
                world.process_event(c)
    if c.lower() == "r":
        mainloop(window, p2_bot)
    elif c.lower() == "b":
        mainloop(window, True)


def main():
    with FullscreenWindow(sys.stdout) as window:
        do_introduction(window)

        mainloop(window)


if __name__ == "__main__":
    main()