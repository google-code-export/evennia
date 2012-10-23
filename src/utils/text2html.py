
"""
ANSI -> html converter

Credit for original idea and implementation
goes to Muhammad Alkarouri and his
snippet #577349 on http://code.activestate.com.

(extensively modified by Griatch 2010)
"""

import re
import cgi
from src.utils import ansi

class TextToHTMLparser(object):
    """
    This class describes a parser for converting from ansi to html.
    """

    tabstop = 4
    # mapping html color name <-> ansi code.
    # note that \[ is used here since they go into regexes.
    colorcodes = [('white', '\033\[1m\033\[37m'),
                  ('cyan', '\033\[1m\033\[36m'),
                  ('blue', '\033\[1m\033\[34m'),
                  ('red', '\033\[1m\033\[31m'),
                  ('magenta', '\033\[1m\033\[35m'),
                  ('lime', '\033\[1m\033\[32m'),
                  ('yellow', '\033\[1m\033\[33m'),
                  ('gray', '\033\[37m'),
                  ('teal', '\033\[36m'),
                  ('navy', '\033\[34m'),
                  ('maroon', '\033\[31m'),
                  ('purple', '\033\[35m'),
                  ('green', '\033\[32m'),
                  ('olive', '\033\[33m')]
    normalcode = '\033\[0m'
    bold = '\033\[1m'
    underline = '\033\[4m'
    codestop = "|".join(co[1] for co in colorcodes + [("", normalcode), ("", bold), ("", underline), ("", "$")])

    re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)', re.S|re.M|re.I)

    def re_color(self, text):
        """Replace ansi colors with html color class names.
        Let the client choose how it will display colors, if it wishes to."""
        for colorname, code in self.colorcodes:
            regexp = "(?:%s)(.*?)(?=%s)" % (code, self.codestop)
            text = re.sub(regexp, r'''<span class="%s">\1</span>''' % colorname, text)
        return re.sub(self.normalcode, "", text)

    def re_bold(self, text):
        "Clean out superfluous hilights rather than set <strong>to make it match the look of telnet."
        #"Replace ansi hilight with strong text element."
        #regexp = "(?:%s)(.*?)(?=%s)" % (self.bold, self.codestop)
        #return re.sub(regexp, r'<strong>\1</strong>', text)
        return re.sub(self.bold, "", text)

    def re_underline(self, text):
        "Replace ansi underline with html underline class name."
        regexp = "(?:%s)(.*?)(?=%s)" % (self.underline, self.codestop)
        return re.sub(regexp, r'<span class="underline">\1</span>', text)

    def remove_bells(self, text):
        "Remove ansi specials"
        return text.replace('\07', '')

    def remove_backspaces(self, text):
        "Removes special escape sequences"
        backspace_or_eol = r'(.\010)|(\033\[K)'
        n = 1
        while n > 0:
            text, n = re.subn(backspace_or_eol, '', text, 1)
        return text

    def convert_linebreaks(self, text):
        "Extra method for cleaning linebreaks"
        return text.replace(r'\n', r'<br>')

    def convert_urls(self, text):
        "Replace urls (http://...) by valid HTML"
        regexp = r"((ftp|www|http)(\W+\S+[^).,:;?\]\}(\<span\>) \r\n$]+))"
        # -> added target to output prevent the web browser from attempting to
        # change pages (and losing our webclient session).
        return re.sub(regexp, r'<a href="\1" target="_blank">\1</a>', text)

    def do_sub(self, m):
        "Helper method to be passed to re.sub."
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space'] == '\t':
            return ' '*self.tabstop
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;'*self.tabstop)
            t = t.replace(' ', '&nbsp;')
            return t

    def parse(self, text):
        """
        Main access function, converts a text containing
        ansi codes into html statements.
        """

        # parse everything to ansi first
        text = ansi.parse_ansi(text)

        # convert all ansi to html
        result = re.sub(self.re_string, self.do_sub, text)
        result = self.re_color(result)
        result = self.re_bold(result)
        result = self.re_underline(result)
        result = self.remove_bells(result)
        result = self.convert_linebreaks(result)
        result = self.remove_backspaces(result)
        result = self.convert_urls(result)
        # clean out eventual ansi that was missed
        result = ansi.parse_ansi(result, strip_ansi=True)

        return result

HTML_PARSER = TextToHTMLparser()

#
# Access function
#

def parse_html(string, parser=HTML_PARSER):
    """
    Parses a string, replace ansi markup with html
    """
    return parser.parse(string)
