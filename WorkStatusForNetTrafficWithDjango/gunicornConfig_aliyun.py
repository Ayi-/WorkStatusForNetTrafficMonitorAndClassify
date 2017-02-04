#!/usr/bin/env python
# coding=utf-8
"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count

def max_workers():    
    return cpu_count()
# gunicorn -c gunicornConfig_aliyun.py WorkStatusForNetTrafficWithDjango.wsgi_pro:application &


#bind = '0.0.0.0:8007'
bind='unix:/tmp/gunicorn_wsfntwd.sock'
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()
reload=True

pythonpath="/home/ae/.pyenv/versions/2.7.10/envs/WorkStatusForNetTrafficWithDjango"
chdir="/home/ae/project/WorkStatusForNetTrafficWithDjango/WorkStatusForNetTrafficWithDjango"

