'''
tictactoe.py
created by Armira Nance
'''

import random
import time
from curtsies import window

from curtsies.fmtfuncs import blink, blue, bold, dark, green, magenta, on_blue, on_cyan, red, yellow, cyan
from curtsies.formatstring import fmtstr
from curtsies import FullscreenWindow, fsarray, FSArray, Input

# globals
board = {1 : "1", 2 : "2", 3 : "3", 4 : "4", 5 : "5", 6 : "6", 7 : "7", 8 : "8", 9 : "9"}
window = None


def emptyBoard(): 
    '''
    This method creates an empty board for us to view what it looks like before gameplay
    '''
    print("\n \nThe board works as follows, with the bottom left square \nrepresenting 1 and the top right square representing 9.")
    print("\nIn order to place your X or O on a spot, enter the number \nthat corresponds to the square you'd like to place it in.")
    print("\nEnjoy the game and notify Armira Nance if anything doesn't work properly.")
    print(cyan("     |     |     "))
    print(yellow("  7  |  8  |  9  "))
    print(cyan("_____|_____|_____"))
    print(cyan("     |     |     "))
    print(yellow("  4  |  5  |  6  "))
    print(cyan("_____|_____|_____"))
    print(cyan("     |     |     "))
    print(yellow("  1  |  2  |  3  "))
    print(cyan("     |     |     "))



def game_board(message=''): 
    '''
    This function prints out the game board as well as changes that occur with game play
    '''
    boardArray = fsarray([
        yellow("     |     |     "), 
        yellow("     |     |     "),
        yellow("_____|_____|_____"),
        yellow("     |     |     "),
        yellow("     |     |     "),
        yellow("_____|_____|_____"),
        yellow("     |     |     "),
        yellow("     |     |     "),
        yellow("     |     |     ")
    ])    

    boardArray[1, 2] = board[7]
    boardArray[1, 8] = board[8]
    boardArray[1, 14] = board[9]

    boardArray[4, 2] = board[4]
    boardArray[4, 8] = board[5]
    boardArray[4, 14] = board[6]

    boardArray[7, 2] = board[1]
    boardArray[7, 8] = board[2]
    boardArray[7, 14] = board[3]

    wholeScreenArray = FSArray(30, 80)
    wholeScreenArray[2:boardArray.height + 2, 0:boardArray.width] = boardArray
    wholeScreenArray[boardArray.height + 4: boardArray.height + 5, 0:len(message)] = [message]

    window.render_to_terminal(wholeScreenArray)

def get_key():
    with Input(keynames='curtsies') as input_generator:
        keypress = next(input_generator)
        return keypress

def xo():
    '''
    xo(window) allows the player to choose between x or o as their gameplay signature
    '''
    print("Welcome to the classic game of...*drumroll*...tic tac toe!")
    game_board(yellow('Would you like to play as X or O? '))
    signature = get_key() # takes input from user
    signature = signature.upper() # allows player to enter a lowercase x or o without penalty

    while (signature.upper() != 'X' and signature.upper() != 'O'): # continues to prompt user until the input is acceptable
        game_board(red("That's not an appropriate term. X or O? "))
        signature = get_key() # prompts user and updates variable

    return signature.upper() # returns upper case version of X or O for use in game


def winner(player):
    '''
    winner() is a function that checks for winners diagonally, vertically, and horizontally
    '''

    combinations = [(3, 5, 7), (1, 5, 9), (3, 6, 9), (2, 5, 8), (1, 4, 7), (7, 8, 9), (4, 5, 6), (1, 2, 3)]

    for x, y, z in combinations:
        if (board[x] == board[y] == board[z] and board[x] != " "):
            if board[x] == player:
                game_board(blink(green("The winner is " + board[x]))) # prints an updated version of the board for the player's reference
                return True
            else:
                game_board(blink(red("The winner is " + board[x]))) # prints an updated version of the board for the player's reference
                return False


def gameplay():
    '''
    Returns True if the player won and False if the computer wins; returns DRAW for draw game
    '''

    emptyBoard()

    moves = 0 # keeps track of the number of moves between the computer and the player
    player = xo() # gets the X or O from the player

    if (player == 'X'): # sets the computer to either X or O depending on player's character
        computer = 'O'
    else:
        computer = 'X'

    player = magenta(player)
    computer = cyan(computer)

    while(moves <= 9): # loops through gameplay until all the squares are filled

        game_board(blue("Choose a spot and input the corresponding number: "))
        position = get_key() # allows player to decide where they'd like to place their signature

        while (position.isdigit() == False or not (int(position) >= 1 and int(position) <= 9) or (board[int(position)] == player or board[int(position)] == computer)): # prompts user until valid input is produced
            game_board(red("You must enter a numbered and unoccupied spot. Try again: "))
            position = get_key()

        position = int(position) # makes position an int rather than a string

        board[position] = player # finally...it marks the spot where the player wants to make their move
        moves += 1 # increments the number of moves

        # this is here and below for a reason, LEAVE IT THERE!
        if (moves >= 5): # starts checking for a winner once any player has had three moves or more
            result = winner(player)

            if (result == True):
                return result # ends game if there is a winner
            elif (result == False):
                return result

        i = random.choice(list(board)) # the computer finds a random place to play

        while (board[i] == player or board[i] == computer): # refreshes the computer's random play if the square isn't available
            if (moves < 9):
                i = random.choice(list(board))
            else:
                game_board(bold(magenta(on_cyan("Draw game!")))) # condition for if there's a "cat"/draw game
                return 'DRAW'

        time.sleep(.5)
        board[i] = computer # marks the computer's play
        moves += 1 # increments moves

        game_board() # prints an updated version of the board for the player's reference

        if (moves >= 5): # starts checking for a winner once any player has had three moves or more
            result = winner(player)

            if (result == True):
                return result # ends game if there is a winner
            elif (result == False):
                return result



def main():
    global window
    with FullscreenWindow() as window:
        result = gameplay()
        time.sleep(5)

    if result == True:
        print(blink(magenta("You won the game!")))
    elif result == 'DRAW':
        print(blink(cyan("Draw game!")))
    else:
        print(blink(blue("You lost the game!")))

if __name__ == "__main__":
    main()
