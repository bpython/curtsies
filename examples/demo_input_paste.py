from curtsies.input import *

def paste():
    """
    Returns user input, delayed by one second, as a string; creates a paste event for 
    strings longer than the paste threshold and returns a list of the characters in 
    the string separated by commas.
    """
    with Input() as input_generator:
        print("If more than %d chars read in same read a paste event is generated" % input_generator.paste_threshold)
        for e in input_generator:
            print(repr(e))

            if e == '<ESC>':
                break

            time.sleep(1)

if __name__ == '__main__':
    paste()
