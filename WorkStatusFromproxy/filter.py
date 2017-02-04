# -*- coding: utf-8 -*-
import HTMLParser
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from mitmproxy.script import concurrent
import logging
import time
import datetime
from celery_tasks import captureUrl
from netlib.http import decoded
import re
pattern = re.compile(r'<!DOCTYPE html',re.I)
patternTitle = re.compile(r'<title>([\s\S\n\r]*?)</title>',re.I)
format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s'
logging.basicConfig(filename='mitmproxyFilter.log',format=format)




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
status_code=[200,301,302,304]
def responseheaders(context, flow):
    """
    Enables streaming for all responses.
    """
    # logging.warning(flow.request.url[-20:])
    # start = time.clock()
    # if not flow.match('!~a & ~u ".js" & ~u ".css" & ~t "text/html" & !(~t "j") & !(~t "i") & !(~t "css") & !~c 403 & !~c 404 & !~c 500'):
    # 使用if控制语句明显比match快上一个数量级
    flow.response.stream = True
    if flow.response.status_code in status_code:  # 正常状态码
        CT = flow.response.headers.get("Content-Type","")  # 获取content-type
        if  CT.find("j") == -1 and CT.find("i") == -1 and CT.find("css") == -1 and CT.find("text/html") != -1:
            # 过滤javasctipt|css|image,只通过有text/html的
            #if flow.match('!~a'):
            flow.response.stream = ""
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
    # start = time.clock()
    if flow.response.content:  # 时间消耗很小
        # logging.warning("%s %s ms\n"%("if content", (time.clock() - start)*1000))

        # print flow.response.headers.get("Host","example.com")
        #print flow.request.scheme,flow.request.host,flow.response.headers.get("Content-Type",""),'\n'
        #print flow.response.headers.get("Content-Type","").split(";")
        
        #print ""
        # start = time.clock()
        with decoded(flow.response):  # 时间消耗很小
            # logging.warning("%s %s ms"%(decoded.__name__, (time.clock() - start)*1000))
            res = pattern.search(flow.response.content[:25])
            resTitle = patternTitle.search(flow.response.content)

            if res and resTitle and resTitle.groups()[0].strip():
                resTitle = resTitle.groups()[0].strip()
                try:
                    resTitle = resTitle.decode('utf-8')
                except Exception as e:
                    resTitle = resTitle.decode('gbk')


                resTitle = HTMLParser.HTMLParser().unescape(resTitle)
                # resTitle = resTitle.decode('utf-8','ignore')
                try:
                    url, host, scheme, content_length, timestamp = flow.request.url, \
                                                                   flow.request.headers.get('Host', ''), \
                                                                   flow.request.scheme, \
                                                                   len(flow.response.content), \
                                                                   int(time.mktime(datetime.datetime.now().timetuple()))
                    if not host:
                        host = flow.request.host
                    start = time.clock()

                    # title = HTMLParser.HTMLParser().unescape(resTitle.groups()[0].decode('utf-8'))

                    # logging.warning("%s %s ms --> %s" % ("pattern ", (time.clock() - start) * 1000, title))


                    captureUrl.apply_async(args=[url,host,scheme,content_length,timestamp,resTitle])
                except Exception as e:
                    logging.critical(u"错误:%s" % (e))


           