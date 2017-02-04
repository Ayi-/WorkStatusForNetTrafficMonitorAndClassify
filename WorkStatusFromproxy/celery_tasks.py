# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys

import datetime
from celery import signals

reload(sys)
sys.setdefaultencoding('utf-8')



import time
import json
import logging
import requests
from celery.utils.log import get_task_logger
from sqlalchemy.orm import sessionmaker
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from urlparse import urljoin


app = Celery('tasks')
app.config_from_object('celeryconfig')
engine = create_engine("mysql://root:0000@localhost/work_status_celery?charset=utf8"
                       , encoding='utf-8', echo=False, pool_recycle=3600, poolclass=QueuePool)


Session = sessionmaker(bind=engine)
session = Session()

insert_SQL = """Insert into url (url,host,scheme,content_length,timestamp,title ) value(%s,%s,%s,%s,%s,%s)"""
search_SQL = """SELECT `id`,`url`,`host`,`scheme`,`timestamp`,`content_length`,`title` FROM work_status_celery.url WHERE `flag`=0 and `timestamp` < :time """
updateUrl_SQL = """UPDATE url SET `flag`=1 WHERE id = :id """
base_url = 'http://192.168.99.100:80'
upLoadPath = 'dashboard/api/url_data/bulkCreate'
obtainTokenPath = 'dashboard/api/obtain-token'
verityTokenPath = 'dashboard/api/verify-token'
token = ''


# or --logfile=/dev/null
# disable logging https://gist.github.com/vmihailenco/1590507
# def setup_task_logger(logger=None, **kwargs):
#     logger.propagate = 1

# signals.setup_logging.connect(lambda **kwargs: True)
# signals.after_setup_task_logger.connect(setup_task_logger)

# def setup_task_logger(logger=None, **kwargs):
#     fh = logging.FileHandler(filename='test.log')
#     logger.propagate = False
#     logger.addHandler(fh)
# signals.after_setup_task_logger.connect(setup_task_logger)

logger = get_task_logger(__name__)

filter_host=('ad.atdmt.com')
logger.info(u"初始化完成")
@app.task
def captureUrl(url, host, scheme, content_length, timestamp, title):
    if host in filter_host:
        pass
    else:
        global insert_SQL, engine
        conn = engine.connect()
        logger.info(u"保存网页->标题:%s"%(title))
        # r1 = u'[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'#用户也可以在此进行自定义过滤字符
        # tem=re.sub(r1, '', title) #过滤内容中的各种标点符号
        conn.execute(insert_SQL, (url, host, scheme.lower(), content_length, timestamp, title))
        conn.close()

def verityToken():
    """
    校验Token
    :return:
    """
    global base_url, token, verityTokenPath
    if not token:
        return False
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'authorization': token}
    urlGetToken = urljoin(base_url, verityTokenPath)
    try:
        r = requests.get(urlGetToken, headers=headers, timeout=60)
        status = r.json()['status']
        if 'ok' == status:
            token = r.json()['result']
            return True
    except Exception as e:
        return False
    
    token = ''
    return False


def getToken():
    """from
    获取Token
    :return:
    """
    global base_url, obtainTokenPath, token
    urlGetToken = urljoin(base_url, obtainTokenPath)
    user = {'user_name': 'test', 'password': 'test'}
    try:
        r = requests.post(urlGetToken, data=user, timeout=60)
        if r.ok:
            status = r.json()['status']
            if 'ok' == status:
                token = r.json()['result']
                return True
    
    except Exception as e:
        logger.critical(u"TOKEN获取失败!",exc_info=True)
        return False
    token = ''
    return False


@app.task
def upLoadUrl():
    """
    上传URL数据
    """
    # conn = engine.connect()

    if verityToken():
        pass
    else:
        if getToken():
            pass
        else:
            return

    global search_SQL, base_url, upLoadPath, updateUrl_SQL, session, token
    logger.info(u"开始上传数据")
    try:
        url = urljoin(base_url, upLoadPath)
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'authorization': token}
        nowTimestamp = time.mktime(datetime.datetime.now().timetuple())
        queryResult = session.execute(search_SQL, ({"time": nowTimestamp}))
        if queryResult.rowcount>0:
            listData = []
            listID = []
            for row in queryResult.fetchall():
                listData.append(dict(row))
                listID.append({'id': row['id']})
            response = {'urlData': json.dumps(listData)}

            r = requests.post(url, data=response, headers=headers)
            status = r.json()['status']
            result = r.json()['result']
            r.close()
            if 'ok' == status:
                # 上传成功
                start = time.clock()
                session.execute(updateUrl_SQL, listData)
                session.commit()
                session.close()
                logger.info(u"上传成功,耗时:%s ms" % ((time.clock() - start) * 1000,))
            else:
                logger.warning("%s:%s" % (u"上传失败", result,))
        else:
            logger.info(u"没有数据需要上传")
    except Exception as e:
        session.rollback()
        logger.critical(u"发生错误:%s" % (e.message))

    finally:
        session.commit()
        session.close()
        # result = conn.execute(search_SQL)
        # start = time.clock()
        # response = []
        # rows = result.fetchall()
        # for row in rows:
        #     response.append(dict(row))
        # logging.warning("%s %s ms" % ("select", (time.clock() - start) * 1000))
