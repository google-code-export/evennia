"""
ANSI related stuff.
"""
import re

class ANSITable(object):
    """
    A table of ANSI characters to use when replacing things.
    """
    ansi = {}
    ansi["beep"] = "\07"
    ansi["escape"] = "\033"
    ansi["normal"] = "\033[0m"
    
    ansi["underline"] = "\033[4m"
    ansi["hilite"] = "\033[1m"
    ansi["blink"] = "\033[5m"
    ansi["inverse"] = "\033[7m"
    ansi["inv_hilite"] = "\033[1;7m"
    ansi["inv_blink"] = "\033[7;5m"
    ansi["blink_hilite"] = "\033[1;5m"
    ansi["inv_blink_hilite"] = "\033[1;5;7m"
    
    # Foreground colors
    ansi["black"] = "\033[30m"
    ansi["red"] = "\033[31m"
    ansi["green"] = "\033[32m"
    ansi["yellow"] = "\033[33m"
    ansi["blue"] = "\033[34m"
    ansi["magenta"] = "\033[35m"
    ansi["cyan"] = "\033[36m"
    ansi["white"] = "\033[37m"
    
    # Background colors
    ansi["back_black"] = "\033[40m"
    ansi["back_red"] = "\033[41m"
    ansi["back_green"] = "\033[42m"
    ansi["back_yellow"] = "\033[43m"
    ansi["back_blue"] = "\033[44m"
    ansi["back_magenta"] = "\033[45m"
    ansi["back_cyan"] = "\033[46m"
    ansi["back_white"] = "\033[47m"
    
    # Formatting Characters
    ansi["return"] = "\r\n"
    ansi["tab"] = "\t"
    ansi["space"] = " "
    
class BaseParser(object):
    def parse_ansi(self, string, strip_ansi=False, strip_formatting=False):
        """
        Parses a string, subbing color codes as needed.
        """
        if string == None or string == '':
            return ''
        
        # Convert to string to prevent problems with lists, ints, and other types.
        string = str(string)
        
        if strip_formatting:
            char_return = ""
            char_tab = ""
            char_space = ""
        else:
            char_return = ANSITable.ansi["return"]
            char_tab = ANSITable.ansi["tab"]
            char_space = ANSITable.ansi["space"]
               
        for sub in self.ansi_subs:
            p = re.compile(sub[0], re.DOTALL)
            if strip_ansi:
                string = p.sub("", string)
            else:
                string = p.sub(sub[1], string)
    
        if strip_ansi:
            return '%s' % (string)
        else:
            return '%s%s' % (string, ANSITable.ansi["normal"])

class MuxANSIParser(BaseParser):
    def __init__(self):
        self.ansi_subs = [
            (r'%r',  ANSITable.ansi["return"]),
            (r'%t',  ANSITable.ansi["tab"]),
            (r'%b',  ANSITable.ansi["space"]),
            (r'%cf', ANSITable.ansi["blink"]),
            (r'%ci', ANSITable.ansi["inverse"]),
            (r'%ch', ANSITable.ansi["hilite"]),
            (r'%cn', ANSITable.ansi["normal"]),
            (r'%cx', ANSITable.ansi["black"]),
            (r'%cX', ANSITable.ansi["back_black"]),
            (r'%cr', ANSITable.ansi["red"]),
            (r'%cR', ANSITable.ansi["back_red"]),
            (r'%cg', ANSITable.ansi["green"]),
            (r'%cG', ANSITable.ansi["back_green"]),
            (r'%cy', ANSITable.ansi["yellow"]),
            (r'%cY', ANSITable.ansi["back_yellow"]),
            (r'%cb', ANSITable.ansi["blue"]),
            (r'%cB', ANSITable.ansi["back_blue"]),
            (r'%cm', ANSITable.ansi["magenta"]),
            (r'%cM', ANSITable.ansi["back_magenta"]),
            (r'%cc', ANSITable.ansi["cyan"]),
            (r'%cC', ANSITable.ansi["back_cyan"]),
            (r'%cw', ANSITable.ansi["white"]),
            (r'%cW', ANSITable.ansi["back_white"]),
        ]
    
def parse_ansi(string, strip_ansi=False, strip_formatting=False, parser=MuxANSIParser()):
    """
    Parses a string, subbing color codes as needed.
    """
    return parser.parse_ansi(string, strip_ansi=strip_ansi, 
                             strip_formatting=strip_formatting)