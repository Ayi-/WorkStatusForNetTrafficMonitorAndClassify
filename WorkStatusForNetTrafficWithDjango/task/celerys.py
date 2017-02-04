#!/usr/bin/env python
# coding=utf-8
import datetime
import json
import logging
import logging.config
import sys, os
from celery import Celery,platforms,Task


import jieba
import jieba.analyse
import MySQLdb
import numpy
from sklearn import metrics
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from celery.signals import celeryd_init

if sys.version_info <= (2, 12):
    reload(sys)
    sys.setdefaultencoding('utf-8')

platforms.C_FORCE_ROOT = True  
app = Celery('tasks')

# 测试用
# 测试导入celery 任务
# import os, sys
# lib_path = os.path.abspath(os.path.join('..', 'task'))
# sys.path.append(lib_path)
# from tasks import *

# 修改结巴分词源码
# change by https://github.com/cavonchen/jieba/commit/8161ba62e59e0f7a3a2151be11db036f3cbaa20a
# and https://github.com/cavonchen/jieba/commit/4d999636e9a31d32b3ed56c1cb371ac604656452
# >>> jieba/__init__.py
# \u4E00-\u9FD5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
# \r\n|\s : whitespace characters. Will not be handled.
# - re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._]+)", re.U)
# + # \u4E00-\u9FD5a-zA-Z0-9+#&\._ : words and whitespace characters and ':' and '-'. Will be handled with re_han
# + re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._\-\: ]+)", re.U)
# # re_han_default = re.compile("(([\u4E00-\u9FD5a-zA-Z0-9+#&\
# ._[^\s\-\:]])+([\-\:\s]([\u4E00-\u9FD5a-zA-Z0-9+#&\._[^\s\-\:]]+)?))", re.U)
#
# >>> jieba/analyse/tfldf.py
# 15:+ re_useridf = re.compile('^(.+?) (\d+|\d+\.+\d+)?$', re.U)
# 52:- word, freq = line.strip().split(' ')
#    + word, freq = re_useridf.match(line).groups()
#    + if freq is not None:
#    +     freq = freq.strip()


# >>> cur = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
# >>> result = cur.execute("select * from dashboard_urldata")
# >>> result= cur.fetchone()

def setup_logging(default_path='logging_setting.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging('/home/code/task/logging_setting.json')


def getConn():
    """获取MySQL连接
    """
    conn = MySQLdb.connect(host="192.168.3.27", port=3306, user="root", passwd="0000", db="work_status_django",
                               use_unicode=True, charset="utf8")
    return conn


class BaseTaskWithDB(Task):
    """with http://www.prschmid.com/2013/04/using-sqlalchemy-with-celery-tasks.html
    and https://groups.google.com/forum/#!topic/celery-users/kBHq73y1YME
    """
    abstract = True
    _db = None

    @property
    def db(self):
        
        if self._db is not None:
            return self._db
        self._db = MySQLdb.connect(host="192.168.3.27", port=3306, user="root", passwd="0000", db="work_status_django",
                               use_unicode=True, charset="utf8")
        return self._db

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Clean up database after the task is finished.
        """
        if self._db is not None:
            self._db.commit()
            self._db.close()
        self._db = None

def loadJiebaDictionary():
    """
    加载结巴分词词库
    :return:
    """
    dictPath = "/home/code/task/dict.txt.small"
    jieba.set_dictionary(dictPath)
    jieba.initialize()  # 手动初始化（可选）

@celeryd_init.connect
def configure_workers(sender=None, conf=None, **kwargs):
    """
    初始化celery
    :param sender:
    :param conf:
    :param kwargs:
    :return:
    """
    app.config_from_object('celery_config')
    logger = logging.getLogger(__name__)
    logger.info("init jieba custom dict")
    loadJiebaDictionary()





# disable logging https://gist.github.com/vmihailenco/1590507
# def setup_task_logger(logger=None, **kwargs):
#     logger.propagate = 1

# signals.setup_logging.connect(lambda **kwargs: True)
# signals.after_setup_task_logger.connect(setup_task_logger)



# 测试用
# 测试导入celery 任务
# import os, sys
# lib_path = os.path.abspath(os.path.join('..', 'task'))
# sys.path.append(lib_path)
# from tasks import *

# 修改结巴分词源码
# change by https://github.com/cavonchen/jieba/commit/8161ba62e59e0f7a3a2151be11db036f3cbaa20a
# and https://github.com/cavonchen/jieba/commit/4d999636e9a31d32b3ed56c1cb371ac604656452
# >>> jieba/__init__.py
# \u4E00-\u9FD5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
# \r\n|\s : whitespace characters. Will not be handled.
# - re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._]+)", re.U)
# + # \u4E00-\u9FD5a-zA-Z0-9+#&\._ : words and whitespace characters and ':' and '-'. Will be handled with re_han
# + re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._\-\: ]+)", re.U)
# # re_han_default = re.compile("(([\u4E00-\u9FD5a-zA-Z0-9+#&\
# ._[^\s\-\:]])+([\-\:\s]([\u4E00-\u9FD5a-zA-Z0-9+#&\._[^\s\-\:]]+)?))", re.U)
#
# >>> jieba/analyse/tfldf.py
# 15:+ re_useridf = re.compile('^(.+?) (\d+|\d+\.+\d+)?$', re.U)
# 52:- word, freq = line.strip().split(' ')
#    + word, freq = re_useridf.match(line).groups()
#    + if freq is not None:
#    +     freq = freq.strip()


# 　SQL语句
queryUrlTitleColSQL = """select `id`,`title`,status from `dashboard_urldata` WHERE `status`=0 """
queryTitleClassificationLibSQL = """select `id`,`title`,`title_key` from `dashboard_titleclassificationlib`"""
queryNewTitleClassificationLibSQL = """select `id`,`title`,`title_key` from `dashboard_titleclassificationlib` WHERE `title_key`='' OR `title_key` is NULL """
updateTitleClassificationLibTitleKeySQL = """UPDATE `work_status_django`.`dashboard_titleclassificationlib` SET `title_key`=%(title_key)s WHERE id = %(id)s"""



# conn=None
# def getConn():
#     """
#     获取数据库连接
#     :return:
#     """
    
#     global conn
#     logger = logging.getLogger(__name__)
#     # 初始化数据库
#     try:
#         conn.ping(True)
#         logger.info(u"Ping database")
#     except:
#         conn = MySQLdb.connect(host="192.168.3.27", port=3306, user="root", passwd="0000", db="work_status_django",
#                                use_unicode=True, charset="utf8")
#         logger.info(u"conn database")
#     return conn

# 自定义任务
@app.task(base=BaseTaskWithDB)
def updateTitleKey(full=False):
    """
    更新标题分类库里面的标题关键字
    :full:是否完全更新，包括已经分词完成的标题
    :return:
    """
    
    global queryTitleClassificationLibSQL, queryNewTitleClassificationLibSQL, updateTitleClassificationLibTitleKeySQL
    
    logger = logging.getLogger(__name__)
    logger.info("start updateTitleKey")
    self = updateTitleKey
    conn = self.db
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    try:
        if full:  # 查询所有记录
            res = cursor.execute(queryTitleClassificationLibSQL)
        else:  # 查询空白纪录
            res = cursor.execute(queryNewTitleClassificationLibSQL)
        if res > 0:
            # res = cursor.fetchall()  # id,title,title_key
            result = []
            for row in cursor:
                title_key = jieba.analyse.extract_tags(row['title'], topK=20)
                title_key = ','.join(title_key)
                if row['title_key'] != title_key:
                    row['title_key'] = title_key
                    result.append(row)

            # for index, item in enumerate(res):
            #     title_key = jieba.analyse.extract_tags(item['title'], topK=20)
            #     title_key = ','.join(title_key)
            #     if res[index]['title_key'] != title_key:
            #         res[index]['title_key'] = title_key
            #     else:
            #         res.pop(index)
            if len(result) > 0:
                cursor.executemany(updateTitleClassificationLibTitleKeySQL, result)

    except Exception as e:
        logger.critical("error:%s" % e)
        conn.rollback()
    finally:
        conn.commit()
        cursor.close()

def loadMysqlTrainData():
    """
    获取词库中的训练数据
    :return:
    """
    
    train_words = []
    train_tags = []

    conn = getConn()
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    queryTitleClassificationLibTitleKeySQL = """select `id`,`category`,`title` from `dashboard_titleclassificationlib` WHERE `title_key` !='' OR `title_key` is not NULL """
    res = cursor.execute(queryTitleClassificationLibTitleKeySQL)
    if res > 0:
        for row in cursor:
            train_words.append(row['title'])
            train_tags.append(row['category'])
    cursor.close()
    conn.commit()
    conn.close()
    
    return train_words, train_tags

def loadMysqlTestData():
    """
    获取待分类数据
    :return:
    """
    test_words = []
    test_tags = []
    test_id = []
    conn = getConn()
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    queryUrlDataSQL = """SELECT `id`,`title` FROM work_status_django.dashboard_urldata WHERE `status`=0;"""
    res = cursor.execute(queryUrlDataSQL)    
    if res > 0:
        for row in cursor:
            test_words.append(row['title'])
            test_id.append(row['id'])
    cursor.close()
    conn.commit()
    conn.close()
    return test_words, test_tags, test_id


# 创建分词器，用于构建特征向量时切分文本
comma_tokenizer = lambda x: jieba.analyse.extract_tags(x, topK=20)
UpdateUrlDataCategorySQL = """UPDATE work_status_django.dashboard_urldata SET `status`=1,`category`=%s,`accuracy`=%s WHERE id =%s;"""


@app.task(base=BaseTaskWithDB)
def naiveBayesMultinomialNB():
    
    global comma_tokenizer, UpdateUrlDataCategorySQL
    logger = logging.getLogger(__name__)
    logger.info(u"启动<naiveBayesMultinomialNB>任务")
    # 构建特征向量
    v = HashingVectorizer(tokenizer=comma_tokenizer, n_features=30000, non_negative=True)
    # 文本-> 矩阵向量转化
    train_words, train_tags = loadMysqlTrainData()
    to_pred_words, to_pred_tags, to_pred_ids = loadMysqlTestData()
    logger.info(u"分类数量：%d",len(to_pred_ids))
    if len(to_pred_ids) > 0:
        # 将训练数据75%:25%，另外一部分用于测试
        filesize = int(0.75 * len(train_words))
        train_data_ = [item for item in train_words[:filesize]]
        train_target_ = [item for item in train_tags[:filesize]]
        test_data_ = [item for item in train_words[filesize:]]
        test_target_ = [item for item in train_tags[filesize:]]
        # 文本-> 矩阵向量转化
        full_train_data = v.fit_transform(train_words)
        train_data = v.fit_transform(train_data_)
        test_data = v.fit_transform(test_data_)
        to_pred_data = v.fit_transform(to_pred_words)
        # 构建分类器MultinomialNB（多项式模型贝叶斯分类器）
        clf = MultinomialNB(alpha=0.01)
        # 训练部分数据
        clf.fit(train_data, numpy.asarray(train_target_))
        pred = clf.predict(test_data)
        accuracy = round(metrics.accuracy_score(test_target_, pred), 3)  # 准确率
        # 训练所有训练数据
        clf.fit(full_train_data, numpy.asarray(train_tags))
        pred = clf.predict(to_pred_data)  # 预测
        length = len(pred)
        accuracyList = [accuracy] * length
        result = zip(pred, accuracyList, to_pred_ids)
        
        conn = naiveBayesMultinomialNB.db
        try:
            with conn as cursor:
                cursor.executemany(UpdateUrlDataCategorySQL, result)
                logger.info(u"naiveBayesMultinomialNB任务完成")
        except Exception as e:
            logger.critical("error:%s" % e)
        
        
    else:
        logger.info(u"naiveBayesMultinomialNB任务完成[没有可进行分类的记录]")
