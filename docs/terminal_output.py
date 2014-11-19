# -*- coding: utf-8 -*-
"""Sphinx directive for ansi-formatted output

sphinxcontrib-ansi seems to be the right thing to use, but it's
missing sequences. It does the right thing and remove color when
output format isn't html. This just always outputs raw html.  """
import re
import sys
from textwrap import dedent

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from sphinx.util.compat import Directive
from docutils import nodes
import pexpect
from ansi2html import Ansi2HTMLConverter

class python_terminal_block(nodes.literal_block):
    pass

def htmlize(ansi):
    conv = Ansi2HTMLConverter(inline=True, dark_bg=True)
    return conv.convert(ansi, full=False)

class ANSIHTMLParser(object):
    def __call__(self, app, doctree, docname):
        handler = self._format_it
        if app.builder.name not in ['html', 'readthedocs']:
            # strip all color codes in non-html output
            handler = self._strip_color_from_block_content
        for ansi_block in doctree.traverse(python_terminal_block):
            handler(ansi_block)

    def _strip_color_from_block_content(self, block):
        content = re.sub('\x1b\\[([^m]+)m', '', block.rawsource)
        literal_node = nodes.literal_block(content, content)
        block.replace_self(literal_node)

    def _format_it(self, block):
        source = block.rawsource
        content = htmlize(source)
        formatted = "<pre>%s</pre>" % (content,)
        raw_node = nodes.raw(formatted, formatted, format='html')
        block.replace_self(raw_node)


def default_colors_to_resets(s):
    """Hack to make sphinxcontrib.ansi recognized sequences"""
    return s.replace('[39m', '[0m').replace('[49m', '[0m')

def run_lines(lines):
    child = pexpect.spawn(sys.executable + ' -i')
    out = StringIO()
    child.logfile_read = out
    #TODO make this detect `...` when it shouldn't be there, forgot a )
    for line in lines:
        child.expect(['>>> ', '... '])
        child.sendline(line)
    child.sendeof()
    child.read()
    out.seek(0)
    output = out.read()
    return output[output.index('>>>'):output.rindex('>>>')]

def get_lines(multiline_string):
    lines = dedent(multiline_string).split('\n')
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines

class PythonTerminalDirective(Directive):
    """Execute the specified python code and insert the output into the document"""
    has_content = True

    def run(self):
        text = default_colors_to_resets(run_lines(get_lines('\n'.join(self.content))))
        return [python_terminal_block(text.decode('utf8'), text.decode('utf8'))]

def setup(app):
    app.add_directive('python_terminal_session', PythonTerminalDirective)
    app.connect('doctree-resolved', ANSIHTMLParser())

if __name__ == '__main__':
    print htmlize(run_lines(get_lines("""
        from curtsies.fmtfuncs import blue
        blue('hello')
        print blue('hello')
        """)))

