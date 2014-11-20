from __future__ import unicode_literals
"""A more realtime netcat"""
import sys
import select
import socket

from curtsies import FullscreenWindow, Input, FSArray
from curtsies.formatstring import linesplit
from curtsies.fmtfuncs import blue, red, green

class Connection(object):
    def __init__(self, sock):
        self.sock = sock
        self.received = []
    def fileno(self):
        return self.sock.fileno()
    def on_read(self):
        self.received.append(self.sock.recv(50))
    def render(self):
        return linesplit(green(''.join(s.decode('latin-1') for s in self.received)), 80) if self.received else ['']

def main(host, port):
    client = socket.socket()
    client.connect((host, port))
    client.setblocking(False)

    conn = Connection(client)
    keypresses = []

    with FullscreenWindow() as window:
        with Input() as input_generator:
            while True:
                a = FSArray(10, 80)
                in_text = ''.join(keypresses)[:80]
                a[9:10, 0:len(in_text)] = [red(in_text)]
                for i, line in zip(reversed(range(2,7)), reversed(conn.render())):
                    a[i:i+1, 0:len(line)] = [line]
                text = 'connected to %s:%d' % (host if len(host) < 50 else host[:50]+'...', port)
                a[0:1, 0:len(text)] = [blue(text)]

                window.render_to_terminal(a)
                ready_to_read, _, _ = select.select([conn, input_generator], [], [])
                for r in ready_to_read:
                    if r is conn:
                        r.on_read()
                    else:
                        e = input_generator.send(0)
                        if e == '<ESC>':
                            return
                        elif e == '<Ctrl-j>':
                            keypresses.append('\n')
                            client.send((''.join(keypresses)).encode('latin-1'))
                            keypresses = []
                        elif e == '<SPACE>':
                            keypresses.append(' ')
                        elif e in ('<DELETE>', '<BACKSPACE>'):
                            keypresses = keypresses[:-1]
                        elif e is not None:
                            keypresses.append(e)

if __name__ == '__main__':
    try:
        host, port = sys.argv[1:3]
    except ValueError:
        print('usage: python chat.py google.com 80')
        print('(if you use this example, try typing')
        print('GET /')
        print('and then hitting enter)')
    else:
        main(host, int(port))
