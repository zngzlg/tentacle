#!/usr/bin/python
# -*- encoding:utf-8 -*-

import urllib2
import json
import threading
import random
import time
import socket
import struct
from datetime import datetime
import sys
import os


class worker(threading.Thread):
    def __init__(self,ip,metrics):
        threading.Thread.__init__(self)
        self.ip = ip
        self.metrics = metrics
    def run(self):
        beans = self.metrics.keys()
        collector = {}
        local = {}
        for bean in beans:
            try:
                fetch_data(self.ip,bean,self.metrics[bean],collector,local)
            except Exception,err:
                break

        if collector:
            data = compute(collector,local)
            if data:
                print collector
                tdbank_report(self.ip,collector)
            save_local(local)

def compute(collector,local):
    pre_data = load_pre()
    if not pre_data:
        print 'can not find datanode_jmx file'
        return None
    for k,v in local.items():
        collector[k] = float(local[k]) - float(pre_data[k])
    return True

def save_local(local):
    with open('datanode_jmx','w') as f:
        for k,v in local.items():
            f.write('{0}:{1}'.format(k,v))
            f.write('\n')
        
def load_pre():
    result = {}
    try:
        if not os.path.exists('datanode_jmx'):
            return None

        with open('datanode_jmx') as f:
            for item in f:
                k,v = item.strip().split(':')
                result[k] = v
            return result
    except Exception,err:
        os.remove('datanode_jmx')
        print repr(err)
        return None
        
def tdbank_report(ip,metrics):
    try:
        # tdbank report
        servers = []
        port = 46801
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client.connect((random.choice(servers), port))
        b_attr = bytes('bid=b_teg_gdtjk&tid=null&dt=%s' % (int(time.time() * 1000)))
        b_body = bytes(
            'sysID=381&intfID=12&timestamp=%s&logtime=%s&ip=%s&%s' % (
                datetime.now().strftime('%Y%m%d%H%M%S'),
                datetime.utcnow().strftime('%Y%m%d%H%M%S') + datetime.utcnow().strftime('%f')[:3],
                ip,
                '&'.join(['{0}={1}'.format(k,v) for k,v in metrics.items()])
            ))
        pack_format = '!ici%dsi%ds' % (len(b_body), len(b_attr))
        total_len = 1 + 4 + len(b_body) + 4 + len(b_attr)
        data = struct.pack(pack_format, total_len, chr(2), len(b_body), b_body, len(b_attr), b_attr)
        client.send(data)
        client.close()
    except Exception,err:
        print repr(err),ip

'''
  ip:host ip
  bean:jmx bean
  metrics:contract
  collector:metrics collector
  local:local state data
'''
def fetch_data(ip,bean,metrics,collector,local):
    url = 'http://{0}:8081/jmx?qry={1}'.format(ip,bean.format(ip=ip))
    page = None
    try:
        page = urllib2.urlopen(url,timeout=5)
        html = page.read()
        if html:
            js_data = json.loads(html)
            # get key from json
            keys = metrics.keys()
            if js_data and js_data['beans']:
                for b in js_data['beans']:
                    for key in keys:
                        if b.has_key(key):
                            collector[key] = b[key]
                            if metrics[key]['type'] == 'COUNTER':
                                local[key] = b[key]
    except Exception,err:
        print ip,repr(err)
        raise Exception(err)
    finally:
        if page:
            page.close()

def load_metrics():
    with open('./conf/datanode.conf') as f:
        js_data = json.load(f)
        return js_data

def fetch():
    js_metrics = load_metrics()
    node = socket.gethostbyname(socket.gethostname())
    node = ''
    t = worker(node,js_metrics)
    t.setDaemon(False)
    t.start()

if __name__ == '__main__':
    fetch()
