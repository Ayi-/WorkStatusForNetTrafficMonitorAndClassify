# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import platform

import os
# print platform.uname()
# print platform.platform()
# print platform.architecture()
import subprocess
import multiprocessing
FNULL = open(os.devnull, 'w')

def runMitmproxy():
    command = 'mitmdump -s filter.py  -p 18080 -q'
    subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)


def runMitmproxyWithSocks5():
    command_proxy_socks5 = 'mitmdump -s proxy2Socks5.py -p 18081 -q'
    subprocess.call(command_proxy_socks5, stdout=FNULL, stderr=subprocess.STDOUT)


def runMitmproxy2Socks5():
    command_socks5 = 'mitmdump -s filter.py -p 18082 -q -U https://127.0.0.1:18081 '
    subprocess.call(command_socks5, stdout=FNULL, stderr=subprocess.STDOUT)


def runCelery():
    command_celery='celery -A celery_tasks worker -l info --logfile="celery.log" '
    subprocess.call(command_celery, shell=True)


def runCeleryBeat():
    command_celery='celery beat -A celery_tasks'
    subprocess.call(command_celery, shell=True)

if __name__ == '__main__':
    systemName = platform.system()
    if systemName.lower()=="windows":


        celeryBeatPid = os.path.join(os.getcwd(), 'celerybeat.pid')
        if (os.path.exists(celeryBeatPid)):
            os.remove(celeryBeatPid)
        # os.system("mitmdump -p 8080 -s filter.py -q")
        # !(~a)过滤所有css js image等 --stream size将流直接转发到客户端

        # os.system(cmd1)

        # from subprocess import check_output
        # check_output("mitmdump -p 8080 -s filter.py ", shell=True)
        multiprocessing.Process(target=runCelery).start()
        multiprocessing.Process(target=runCeleryBeat).start()
        multiprocessing.Process(target=runMitmproxy).start()
        # command_socks5 = "mitmdump -p 8081 -q -s filterWithSocks5.py --stream 3m !(~a) --upstream-trusted-cadir .mitmproxy --add-upstream-certs-to-client-chain --cert-forward"
        # subprocess.call(command_socks5, shell=True)
        multiprocessing.Process(target=runMitmproxyWithSocks5).start()
        multiprocessing.Process(target=runMitmproxy2Socks5).start()


    # os.system("mitmdump -p 8081 -q -s filterWithSocks5.py --stream 3m !(~a) --upstream-trusted-cadir .mitmproxy --add-upstream-certs-to-client-chain --cert-forward")


