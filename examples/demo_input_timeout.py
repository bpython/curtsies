from curtsies.input import *

def main():
    with Input() as input_generator:
        print(repr(input_generator.send(2)))
        print(repr(input_generator.send(1)))
        print(repr(input_generator.send(.5)))
        print(repr(input_generator.send(.2)))
        for e in input_generator:
            print(repr(e))
if __name__ == '__main__':
    main()
