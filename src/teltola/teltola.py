# teltola.py
# a simple telnet engine

import os, random, time

from nevow import inevow, loaders, livepage
from nevow.livepage import set, assign, append, js, document, eol

from twisted.internet import protocol, reactor
from twisted.internet.protocol import ClientCreator
from django.conf import settings

from src.teltola.session import RTFakeSessionProtocol

class Teltola(livepage.LivePage):
    addSlash = True
    docFactory = loaders.xmlfile(os.path.join(settings.SRC_DIR, "teltola", 'bootstrap.html'))

    def __init__(self):
        self.myClients = {}
        livepage.LivePage.__init__(self)
    def goingLive(self, ctx, client):
        request = inevow.IRequest(ctx)
        self.myClients[client] = RTFakeSessionProtocol(client, (request.client.host, request.client.port))
        self.myClients[client].connectionMade()
    def handle_sendInput(self, ctx, inputLine):
        sender = livepage.IClientHandle(ctx)
        #self.myClients[sender].write(inputLine + "\n")
        self.myClients[sender].execute_cmd(inputLine)
        return sender.send([js.focusInput()])
