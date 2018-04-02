#!/usr/bin/env python

import json
import os,time,requests
import ConfigParser
from nlc import logCat

def start():
    base_dir=os.path.dirname(os.path.abspath(__file__))
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(base_dir,'nlc.conf'))
    nginx_conf_path = cf.get('nginx','path')
    time_interval = cf.get('nlc','time_interval')
    send_url = cf.get('nlc','send_url')
    header = {"Content-Type": "application/json;charset=utf-8"}

    while True:
        logobj = logCat(nginx_conf_path)
        data = logobj.run_all()
        response = requests.post(send_url,data = json.dumps(data),headers=header) 
        time.sleep(float(time_interval))

if __name__ == '__main__':
    start()
