import sys

from curtsies import CursorAwareWindow, input, fmtstr

class FakeBpythonRepl(object):
    def __init__(self, get_rows_cols):
        self.scrolled = 0
        self.num_lines_output = 1
        self._get_rows_cols = get_rows_cols

    def add_line(self):
        self.num_lines_output += 1

    def paint(self):
        a = []
        for row in range(self.num_lines_output)[self.scrolled:]:
            line = '-'.join(str(row) for _ in range(self.columns))[:self.columns]
            a.append(line)
        return a

    rows    = property(lambda self: self._get_rows_cols()[0])
    columns = property(lambda self: self._get_rows_cols()[1])


def main():
    w = CursorAwareWindow(sys.stdout, sys.stdin,
                          keep_last_line=True, hide_cursor=False)
    with input.Input() as inp:
        with w:
            repl = FakeBpythonRepl(w.get_term_hw)
            for e in inp:
                if e == 'a':
                    repl.add_line()
                else:
                    repl.scrolled += w.render_to_terminal(repl.paint())

if __name__ == '__main__':
    main()
