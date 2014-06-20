from input import *

def main():
    with Input() as input_generator:
        print repr(input_generator.send(2))
        print repr(input_generator.send(1))
        print repr(input_generator.send(.5))
        print repr(input_generator.send(.2))
        for e in input_generator:
            print repr(e)

def sigwinch():
    import signal
    def sigwinch_handler(signum, frame):
        print 'sigwinch received'
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    main()

def sigint():
    import signal
    def sigint_handler(signum, frame):
        print 'sigint received'
    signal.signal(signal.SIGINT, sigint_handler)
    main()

def paste():
    with Input() as input_generator:
        for e in input_generator:
            print repr(e)
            time.sleep(1)

if __name__ == '__main__':
    #main()
    #testfunc()
    #sigwinch()
    #sigint()
    paste()
