# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
This example builds on mitmproxy's base proxying infrastructure to
implement functionality similar to the "sticky cookies" option.

Heads Up: In the majority of cases, you want to use inline scripts.
"""
import socket
import socks

socks.set_default_proxy(socks.SOCKS5, "localhost")
socket.socket = socks.socksocket
import win_inet_pton
import os
from mitmproxy import controller, proxy
from mitmproxy.proxy.server import ProxyServer


class StickyMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()
    def handle_responseheaders(self, flow):
        """
        Enables streaming for all responses.
        """
        flow.response.stream = True
        flow.reply()
    # def handle_request(self, flow):
        # print "request-----"
        # print flow.request.url
        # print flow.request.content
        # print "request ============="
        # hid = (flow.request.host, flow.request.port)
        # if "cookie" in flow.request.headers:
        #     self.stickyhosts[hid] = flow.request.headers.get_all("cookie")
        # elif hid in self.stickyhosts:
        #     flow.request.headers.set_all("cookie", self.stickyhosts[hid])
        # flow.reply()

    # def handle_response(self, flow):
        # print flow.request.url
        # # print flow.request.headers.get("Accept", "unknown Accept")
        # print flow.response.headers.get("content-type", "unknown content type")
        # print '\n'
        # hid = (flow.request.host, flow.request.port)
        # if "set-cookie" in flow.response.headers:
        #     self.stickyhosts[hid] = flow.response.headers.get_all("set-cookie")
        # flow.reply()


config = proxy.ProxyConfig(port=8080)
server = ProxyServer(config)
m = StickyMaster(server)
m.run()