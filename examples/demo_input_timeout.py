from curtsies.input import *

def main():
    """
    Reads and returns user input; after 2 seconds, 1 second, .5 second 
    and .2 second, respectively, an event -- user input -- is printed, 
    or "None" is printed if no user input is received.
    """
    with Input() as input_generator:
        print(repr(input_generator.send(2)))
        print(repr(input_generator.send(1)))
        print(repr(input_generator.send(.5)))
        print(repr(input_generator.send(.2)))
        for e in input_generator:
            print(repr(e))
            if e == '<ESC>':
                break
if __name__ == '__main__':
    main()
