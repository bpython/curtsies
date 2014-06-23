def simple_fullscreen():
    logging.basicConfig(filename='display.log',level=logging.DEBUG)
    from termhelpers import Cbreak
    print 'this should be just off-screen'
    w = FullscreenWindow(sys.stdout)
    rows, columns = w.t.height, w.t.width
    with w:
        a = [fmtstr((('.row%r.' % (row,)) * rows)[:columns]) for row in range(rows)]
        w.render_to_terminal(a)

if __name__ == '__main__':
    simple_fullscreen()
