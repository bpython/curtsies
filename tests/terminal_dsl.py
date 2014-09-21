import unittest
import re
from collections import namedtuple

TerminalState = namedtuple('TerminalState',
                           ['history', 'rendered', 'top_usable_row',
                            'scrolled', 'cursor', 'visible', 'rows', 'columns'])

def divide_term_states(s):
    """Return a list of verically divided terminal diagrams from one string

    >>> len(divide_term_states('''
    ... +-----+    +-------+   +--+
    ... |ABC  |    |ABC    |   +--+
    ... +-----+    +-------+   |@ |
    ... |BC   | -> |BC     |   +--+
    ... |abc@ |    |abc@   |
    ... |     |    |       |
    ... +-----+    +-------+
    ... '''))
    3
    """
    #TODO allow the first line to have content on it (has to be blank right now)
    lines = s.split('\n')
    if lines[0].strip():
        raise ValueError('Top line needs to be blank')
    max_length = max(len(line) for line in lines)
    spaces_by_line = [set(m.start() for m in re.finditer(r' ', line)).union(
                          set(range(len(line), max_length)))
                      for line in s.split('\n') if s.strip()]
    empty_columns = set.intersection(*spaces_by_line)
    empty_columns.add(max_length)

    sections = []
    last = 0
    for index in sorted(empty_columns):
        vertical_strip = []
        for line in s.split('\n'):
            vertical_strip.append(line[last:index])
        sections.append(vertical_strip)
        last = index
    candidates = ['\n'.join(section) for section in sections]
    diagrams = [s for s in candidates if '|' in s and '-' in s and '@' in s]
    return diagrams


def parse_term_state(s):
    """Returns TerminalState tuple given a terminal state diagram

    >>> parse_term_state('''
    ...  label
    ... +-----+
    ... |ABC  |
    ... +-----+
    ... |BC   |
    ... |abc@ |
    ... |     |
    ... +-----+
    ... ''')
    ('label', TerminalState(history=['abc'], rendered=['abc'], top_usable_row=1, scrolled=0, cursor=[1, 3], visible=['bc', 'abc'], rows=3, columns=5))
    """

    m = re.search(r'(?<=\n)\s*([+][-]+[+])\s*(?=\n)', s)
    label = ' '.join(line.strip() for line in s[:m.start()].split('\n') if line.strip())
    top_line = m.group(1)
    width = len(top_line) - 2
    assert width > 0
    lines = re.findall(r'(?<=\n)\s*([+|].*[+!|])\s*(?=\n)', s)
    for line in lines:
        if len(line) - 2 != width:
            raise ValueError("terminal diagram line not of width %d: %r" % (width + 2, line,))
        assert len(line) - 2 == width

    sections = ('before', 'history', 'visible', 'after')
    section = sections[0]
    current_display_line = -1
    maybe_for_visible = []

    history = []
    rendered = []
    visible = []
    cursor= None
    top_usable_row = 0
    scrolled = 0

    for line in lines:
        inner = line[1:-1]
        if inner == '-'*width:
            section = sections[sections.index(section) + 1]
            if section == 'after':
                break
            continue

        if section == 'visible':
            current_display_line += 1

        if '@' in inner:
            if cursor is not None:
                raise ValueError("Two cursors (@'s) in terminal diagram:\n%s" % (s,))
            cursor = [current_display_line, inner.index('@')]
            inner = inner.replace('@', ' ')

        if section == 'history':
            history.append(inner.lower().rstrip())
        elif section == 'visible':
            if inner.strip():
                visible.extend(maybe_for_visible)
                visible.append(inner.lower().rstrip())
            else:
                maybe_for_visible.append(inner.lower().rstrip())
        elif section == 'after':
            break
        elif section == 'before':
            continue

        if inner.islower():
            rendered.append(inner.rstrip())

        if inner.islower() and section == 'history':
            scrolled += 1
        elif inner.isupper() and section == 'visible':
            top_usable_row += 1

    if not section == 'after':
        raise ValueError("finish in section %s - didn't complete terminal diagram:\n%s" % (section, s))

    return (label,
            TerminalState(history=history, rendered=rendered,
                          top_usable_row=top_usable_row, scrolled=scrolled,
                          cursor=cursor, visible=visible,
                          rows=current_display_line+1, columns=width))

class TestTerminalResizing(object):
    """Mixin for testing """
    def assertResizeMatches(self, diagram):
        term_states = divide_term_states(diagram)
        label1, initial = parse_term_state(term_states[0])
        label2, final = parse_term_state(term_states[1])
        #TODO when testing different terminals, use labels to identify

        self.prepare_terminal(initial.rows, initial.columns, initial.history,
                              initial.visible, initial.cursor)
        self.resize(final.rows, final.columns)
        requested_cursor_row = final.cursor[0] - final.top_usable_row
        self.render(final.rendered, requested_cursor_row)
        self.check_output()

    def prepare_terminal(self, rows, columns, history, visible, cursor):
        """Set self.terminal to have these properties"""
        raise NotImplementedError

    def render(self, array):
        raise NotImplementedError

    def resize(self, rows, columns):
        raise NotImplementedError

    def check_output(self, history, scrolled, ): #TODO: need to add more things
        """Checks that output matches final terminal"""
        raise NotImplementedError


class test_parse_term_state(unittest.TestCase):
    pass

# Test just for resizing

#Parsing the diagrams:
# prepopulate history
# put cursor on right line
# detect window changes and make them
# make app output exactly what is shown (build array)
# determine top usable line and scrolled from initial diagram
# detect repl.scrolled from repl lines in history

"""
+---------+         +----------+
|GEOrgiann+         |georgiann |
|a        !         |a         |
|         !         |          |
+---------+   -->   +----------+
|hello    |         |hello     |
|bpython  |         |bpython   |
|*********|         |**********|
|*        |         |****@     |
|****@    |         |          |
|         |         |          |
+---------+         +----------+
"""

decrease_height_with_space_at_bottom_and_cursor_at_end = """
#---------#         #---------#   #---------#
|georgiann+         |georgiann|   |georgiann|
|a        |         |a        |   |a        |
|         |         |         |   |         |
#---------#   -->   #---------#   |hello    |
|hello    |         |hello    |   #---------#
|bpython  |         |bpython  |   |bpython  |
|*********|         |*********|   |*********|
|*        |         |*        |   |*        |
|****@    |         |****@    |   |****@    |
|         |         #---------#   |         |
#---------#                       #---------#
"""
decrease_width_with_space_at_bottom_and_cursor_at_end = """

                                     reflow
                       xterm       +--------+
+---------+         +--------+     |georgian+
|georgiann+         |georgian|     |na      |
|a        !         |a       |     |        |
|         !         |        |     |hello   |
+---------+   -->   +--------+     +--------+
|hello    |         |hello   |     |bpython |
|bpython  |         |bpython |     |********|
|*********|         |********|     |*       |
|*        |         |*       |     |****@   |
|****@    |         |****@   |     |        |
|         |         |        |     |        |
+---------+         +--------+     +--------+
"""
decrease_width_with_cursor_not_at_end = """

                                     reflow
                       xterm       +--------+
+---------+         +--------+     |georgian+
|georgiann+         |georgian|     |na      |
|a        !         |a       |     |        |
|         !         |        |     |hello   |
|stuff    !         |stuff   |
+---------+   -->   +--------+     +--------+
|******   |         |******  |     |bpython |
|*******  |         |******* |     |*       |
|*********|         |********|     |****@   |
|*        |         |*       |     |********|
|****@    |         |****@   |     |        |
|*********|         |********|     |        |
+---------+         +--------+     +--------+
"""
decrease_height_with_cursor_not_at_bottom = """

                       xterm         reflow
+---------+         +---------+    +---------+
|GEORGIANN+         |GEORGIANN|    |GEORGIANN+
|A        !         |A        |    |A        !
|         !         |         |    |         !
|STUFF    !         |STUFF    |    |STUFF    !
+---------+   -->   |abcdef   |    |abcdef   |
|abcdef   |         #---------#    +---------+
|ghijklm  |         |ghijklm  |    |ghijklm  |
|nopqrstuv|         |nopqrstuv|    |nopqrstuv|
|w        |         |w        |    |w        | should break history in this case
|xyza@    |         |xyza@    |    |xyza@    |
|bcdefghij|         |bcdefghij|    |bcdefghij|
+---------+         +---------+    +---------+
"""
# @ is cursor
# * is content in application (not our job to reflow)
# + means this is a continued line
# . means a space character (spaced are empty)
# capital letters mean history
# lowercase letters are in the app's control
# 

# what the app does: render its lines based on initial top usable and scrolled

# should eventually test xterm, gnome-terminal, iterm, terminal.app, tmux

#terminal questions:
# * does xterm have a difference between spaces and nothing?
# * does xterm do cursor at bottom scroll up differently?
# * can xterm ever have a clear space at bottom but history

# in reflowing terminals, when window narrows and causes wrap
# to send things off the top, we need to know behavior of those leaving lines

# for reflowing terminals, we're going to need every single width and height along the way to a change
# (changing window size and changing it back in a fluid motion still causes changes



# We also need to test that when FakeBpython asked for display of 

