# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from celery_tasks import captureUrl
import socket
import socks
socks.setdefaultproxy(socks.SOCKS5, "localhost")
socket.socket = socks.socksocket
import win_inet_pton
from mitmproxy.script import concurrent
import logging
import time
from filter import pattern,status_code
from netlib.http import decoded
import filter

def responseheaders(context, flow):
    """
    Enables streaming for all responses.
    """
    # logging.warning(flow.request.url[-20:])
    # start = time.clock()
    # if not flow.match('!~a & ~u ".js" & ~u ".css" & ~t "text/html" & !(~t "j") & !(~t "i") & !(~t "css") & !~c 403 & !~c 404 & !~c 500'):
    # 使用if控制语句明显比match快上一个数量级

    # flow.response.stream = True
    # if flow.response.status_code in status_code:  # 正常状态码
    #     CT = flow.response.headers.get("Content-Type","")  # 获取content-type
    #     if  CT.find("j") == -1 and CT.find("i") == -1 and CT.find("css") == -1 and CT.find("text/html") != -1:
    #         # 过滤javasctipt|css|image,只通过有text/html的
    #         #if flow.match('!~a'):
    #         flow.response.stream = ""
    filter.responseheaders(context,flow)
    # logging.warning("%s %s ms\n"%(responseheaders.__name__, (time.clock() - start)*1000))

@concurrent
def response(self,flow):
    # if flow.match("""~t "text/html" & !~a """):
    #     # print flow.response.headers.get("Host","example.com")
    #     #print flow.request.scheme,flow.request.host,flow.response.headers.get("Content-Type",""),'\n'
    #     #print flow.response.headers.get("Content-Type","").split(";")
    #     url,scheme,content_typt,host,timestamp = flow.request.url,\
    #                                              flow.request.scheme,\
    #                                              flow.response.headers.get("Content-Type",""),\
    #                                              flow.request.host,\
    #                                              time.mktime(time.gmtime())


    #     try:
    #         captureUrl.apply_async(args=[url,scheme,content_typt,host,timestamp])
    #     except Exception as e:
    #         print e
    # captureUrl(flow.request.url,)

    filter.response(flow)
    # start = time.clock()
    # if flow.response.content:  # 时间消耗很小
    #     # logging.warning("%s %s ms\n"%("if content", (time.clock() - start)*1000))
    #
    #     # print flow.response.headers.get("Host","example.com")
    #     #print flow.request.scheme,flow.request.host,flow.response.headers.get("Content-Type",""),'\n'
    #     #print flow.response.headers.get("Content-Type","").split(";")
    #
    #     #print ""
    #     # start = time.clock()
    #     with decoded(flow.response):  # 时间消耗很小
    #         # logging.warning("%s %s ms"%(decoded.__name__, (time.clock() - start)*1000))
    #
    #         # start = time.clock()
    #         res = pattern.search(flow.response.content[:15])
    #         # logging.warning("%s %s ms"%("pattern ", (time.clock() - start)*1000))
    #         url,host,scheme,content_length,timestamp = flow.request.url, \
    #                                                    flow.request.host, \
    #                                                    flow.request.scheme, \
    #                                                    len(flow.response.content), \
    #                                                    time.mktime(time.gmtime())
    #         if res:
    #             try:
    #
    #                 captureUrl.apply_async(args=[url,host,scheme,content_length,timestamp])
    #             except Exception as e:
    #                 print e


