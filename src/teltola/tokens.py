# Some Constants
# see rtclient protocol documentation for more details

# TODO: figure out what constants we really want to use here :P
# 500 was just chosen at random, I found the reserved
# numbers for utf-16 but coudln't find the one for utf-8 quickly :)
# chunk types
HTML_TOKEN = unichr(500)
JAVASCRIPT_TOKEN = unichr(501)
UNENCODED_TOKEN = unichr(502)
TELNET_ONLY_TOKEN = unichr(503)
# chunking modes
NO_AUTOCHUNK_TOKEN = unichr(504)
AUTOCHUNK_TOKEN = unichr(505)

# TELNET_ONLY_TOKEN is not strictly speaking part of the rtclient protocol
# as it is parsed out before being sent to the client
ENCODING_TOKENS = [HTML_TOKEN, JAVASCRIPT_TOKEN, TELNET_ONLY_TOKEN, UNENCODED_TOKEN, AUTOCHUNK_TOKEN, NO_AUTOCHUNK_TOKEN]
