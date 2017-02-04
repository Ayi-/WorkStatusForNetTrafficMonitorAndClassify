#!/usr/bin/env python
# coding=utf-8
"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count

def max_workers():    
    return cpu_count()


bind = '0.0.0.0:8081'
#bind='unix:/tmp/gunicorn_wsfntwd.sock'
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()
reload=True

pythonpath="/home/aiiyi/.pyenv/versions/wsfnt/bin/python"
chdir="/home/code/WorkStatusForNetTrafficWithDjango"

