from curtsies.input import *

def paste():
    with Input() as input_generator:
        print("If more than %d chars read in same read a paste event is generated" % input_generator.paste_threshold)
        for e in input_generator:
            print(repr(e))
            time.sleep(1)

if __name__ == '__main__':
    paste()
