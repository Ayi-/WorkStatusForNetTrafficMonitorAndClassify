# -*- coding: utf-8 -*-
import sys

from mitmproxy.script import concurrent

reload(sys)
sys.setdefaultencoding('utf-8')
import socket
import socks
socks.setdefaultproxy(socks.SOCKS5, "localhost")
socket.socket = socks.socksocket
import win_inet_pton


# def responseheaders(context, flow):
#     """
#     Enables streaming for all responses.
#     """
#     flow.response.stream = True
# def proxy_address(flow):
#     # Poor man's loadbalancing: route every second domain through the alternative proxy.
#     # if hash(flow.request.host) % 2 == 1:
#     #     return ("localhost", 8082)
#     # else:
#         return ("127.0.0.1", 1080)

# @concurrent
# def request(context,flow):
    # print "request-----"

    # print "request ============="

    # if flow.request.method == "CONNECT":
    #     # If the decision is done by domain, one could also modify the server address here.
    #     # We do it after CONNECT here to have the request data available as well.
    #     return
    # address = proxy_address(flow)
    # if flow.live:
    #     flow.live.change_upstream_proxy_server(address)




