from src.utils.ansi import ANSIParser
from cgi import escape
from src.teltola.tokens import *


def manual(txt):
   return "%%xm%s%%xa" % txt
def html(txt):
   return "%%xh%s%%xu" % txt
def telnet_only(txt):
   return "%%xt%s%%xu" % txt
def a(txt, cmd=False, raw_url = False, js=False, rtonly=False):
    if not raw_url:
        if js:
            onclick = js
        else:
            if not cmd:
                cmd = txt
            onclick = "server.handle('sendInput', '%s')" % cmd
        if rtonly:
            
            return html("<a onclick=\"%s; return false\" href=\"#\">%s</a>" % (onclick, txt))
        else:
            return "%s%s%s" % (html("<a onclick=\"%s; return false\" href=\"#\">" % onclick), txt, html("</a>"))
    else:
        return "%s%s%s" % (html("<a href='%s'>" % cmd), txt, html("</a>"))

# everyone sees the txt, but only html users see the tag
# if an alt is supplied a touple can be applied for tags
# seen only by telnet clients
def tag(tag, txt, extra=False, rtonly=False, alt=False):
    if extra:
        extra = " %s" % extra
    else:
        extra = ""
    if rtonly:
        return html("<%s%s>%s</%s>" % (tag,extra,qesc(txt),tag))
    else:
        if not alt:
            return "%s%s%s" % (html("<%s%s>" % (tag,extra)), txt, html("</%s>" % tag))
        else:
            return "%s%s%s%s%s" % (telnet_only(alt[0]),html("<%s%s>" % (tag,extra)), txt, html("</%s>" % tag), telnet_only(alt[1]))

# everyone sees telnet_tag text but only telnet users see the tags
def telnet_tag(txt, pre, post=""):
    return "%s%s%s" % (telnet_only(pre),txt,telnet_only(post))

def qesc(txt):
   return escape(txt, quote=True)

def strip_for_telnet_client(txt):
    """
    Parse the rtclient envelope and send only those chunks marked as unencoded telnet.
    """
    b = ""
    recording = True
    for c in txt:
	if c == HTML_TOKEN or c == JAVASCRIPT_TOKEN:
	    recording = False
	elif c == UNENCODED_TOKEN:
	    recording = True
	elif c == AUTOCHUNK_TOKEN or c == NO_AUTOCHUNK_TOKEN or c == TELNET_ONLY_TOKEN:
	    pass
	elif recording:
	    b += c
    return b

def strip_for_teltola_client(txt):
    """
    Parse the rtclient envelope and send everything except the telnet-only control
    character a chunk. Note that unlike the telnet client, we do pass on the control
    characters here since teltola needs to know what state it is changing to, whereas
    the telnet client always stays in the unencode text state.
    """
    b = ""
    recording = True
    for c in txt:
	if c == HTML_TOKEN or c == JAVASCRIPT_TOKEN or c == UNENCODED_TOKEN:
	    recording = True
	if c == TELNET_ONLY_TOKEN:
	    recording = False
	elif recording:
	    b += c
    return b

def expurgate(txt):
    """ Remove all objectionable content from player-sent strings. Note that
        this is only half the battle. You need to prevent manufactured strings
        from being created (most commonly via %xh or via concat() string ops
        that might be exposed to users
     """
    return u"".join(filter(lambda uchr: uchr not in ENCODING_TOKENS,txt ))

def hr():
    return "%xh<hr />%xt\n" + ("-" * 70) + "%xu"

def h2(txt):
    return tag("h2", txt, alt=("\n\r" + "-"*70 + "\n\r  {g","{n\n" + "-"*70))
