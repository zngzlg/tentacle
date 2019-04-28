#!/usr/bin/python

import os
import subprocess
from subprocess import PIPE
import json
import threading
from threading import Timer
from logger import TimedRotatingLogger
from logger import ConsoleLogger

logger = TimedRotatingLogger(__file__)
#logger= ConsoleLogger(__file__)

def arg_preprocess(args):
    if args == None:
        return ''
    else:
        return args

def path_preprocess(path):
    return os.path.abspath(path)

def load_conf():
    if os.path.exists('./conf/tentacle.conf'):
        with open('./conf/tentacle.conf') as f:
            conf = f.read()
            try:
                conf_js = json.loads(conf)
                return conf_js
            except Exception,err:
                logger.eror('can not load tentacle.conf as json')
                return None

class metric(object):
    def __init__(self,dt):
        self.__dict__ = dt


class worker(threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data

    def kill(self):
        if self.proc:
            self.proc.kill()
            logger.log('task {0} timeout killed'.format(self.data.name))

    def run(self):
        if os.path.exists(self.data.path):
            args = arg_preprocess(self.data.args)
            path = path_preprocess(self.data.path)
            self.proc = subprocess.Popen(['python',path,args],stdout=PIPE, stderr=PIPE)
            timer = Timer(min(self.data.interval,60), self.kill)
            try:
                timer.start()
                stdout,stderr = self.proc.communicate()
                logger.log('{0} task {1} returned {2}'.format(threading.currentThread().name,self.data.name,[stdout.strip(),stderr.strip()]))
            finally:
                timer.cancel()
        else:
            logger.error('{0} can not find {1}'.format(threading.currentThread().name,self.data.path))

def main():
    conf = load_conf()
    if not conf:
        logger.error('can not find tentacle.conf')
        exit(0)

    metrics = conf['metrics']
    for _m in metrics:
        m = metric(_m)
        t = worker(m)
        t.setDaemon(False)
        t.start()

if __name__ == '__main__':
    main()
