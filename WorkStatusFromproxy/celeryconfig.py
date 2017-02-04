# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import absolute_import # 这一行极为重要，不添加会导致crontab import失败
from datetime import timedelta
from celery.schedules import crontab # 周期性任务

# 用来设置celery消息通道，使用redies
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# BROKER_URL = 'redis://localhost:6379/0'
# 设置数据存储

# CELERY_RESULT_BACKEND = 'redis://localhost/0'
#CELERY_RESULT_BACKEND = "db+mysql://root:0000@localhost/work_status_celery"
CELERY_IGNORE_RESULT = True
CELERYD_HIJACK_ROOT_LOGGER = False

# 设置序列化格式
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# 设定时区
CELERY_TIMEZONE = 'Asia/Shanghai'

# 定时任务
# timedelta(seconds=30),定时30秒
CELERYBEAT_SCHEDULE  = {
    'add-every-time': {
        'task': 'celery_tasks.upLoadUrl',
        #'schedule': crontab(minute=0, hour='*'),# 每小时
        'schedule': crontab(minute='*'),# 每分钟

    },
}