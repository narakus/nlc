#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os 
import re
import json
import logging
import functools
from datetime import datetime,timedelta

base_dir=os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
    format='[%(asctime)s] %(name)s/%(levelname)s - %(message)s',
    filename=os.path.join(base_dir,'work.log'),
    filemode='a'
)

#默认获取一天前日志,判断是否存在以及是否经过压缩
#已弃用
def select_date(mydays=0):
    def wrapper(origin_func):
        @functools.wraps(origin_func) 
        def inner(self,*args,**kwargs):
            result = {}
            select_date = datetime.now() - timedelta(days=mydays) 
            date_str = select_date.strftime('%Y%m%d')
            tmp_data = origin_func(self,*args,**kwargs)
            tmp_dict_with_date = { k:v + '-' + date_str for k,v in tmp_data.items() }
            for k,v in tmp_dict_with_date.items():
                if os.path.exists(v):
                    result[k] = v
                elif os.path.exists(v + '.gz'): 
                    result[k] = v + '.gz'
                else:
                    continue
            return result
        return inner
    return wrapper

  
#处理压缩日志,将日志文件转化为文件流传入函数
#已弃用
def mgz(origin_func):
   def wrapper(self,*args,**kwargs):
       tf = args[0]
       if tf.endswith('gz'):
           tmp_obj = cl(tf)
           tmp_file = tmp_obj.cpy_gzip
           if tmp_obj.ungz_file:
               return origin_func(self,tmp_obj.tmpfile)
       return origin_func(self,*args,**kwargs)
   return wrapper

def no_select_date(origin_func):
    @functools.wraps(origin_func)
    def wrapper(*args,**kwargs):
        result = {}
        tmp_data = origin_func(*args,**kwargs)
        for k,v in tmp_data.items():
            if os.path.exists(v):
                result[k] = v
            else:
                continue
        return result
    return wrapper
 
class logBase(object):
    '''用于获取配置文件中日志路径等信息'''
    def __init__(self,log_path):
        self.base_path = log_path

    def get_confs(self):
        return [ i for i in os.listdir(self.base_path) if i.endswith('.conf')]

    def get_abs_confs(self):
        return [ os.path.join(self.base_path,i) for i in self.get_confs() ]

    def get_regx_by_conf(self,regx):
        result = {}
        for curr_file in self.get_abs_confs():
           fp = open(curr_file,'r')
           for i in fp.readlines():
               tp = regx.match(i)
               if(tp):
                   result[curr_file] = tp.group(1)
           fp.close()
        return result
 
    @no_select_date
    def get_access_log_path(self):
        regx = re.compile(r'\s*access_log\s*(/\S+)\s*.*?')
        return self.get_regx_by_conf(regx)
       
    def get_servername_by_conf(self):
        regx = re.compile(r'\s*server_name\s*(\S+)\s*;')
        return self.get_regx_by_conf(regx)

    def map_path_with_servername(self):
        result = {}
        pdict = self.get_access_log_path()
        sdict = self.get_servername_by_conf()
        for pk,pv in pdict.items():
            for sk,sv in sdict.items():
                if pk == sk:
                    result[sv] = pv
        return result
        #return dict(zip(sdict.values(),pdict.values()))      

class logCat(logBase):
    ''' 解析日志状态值，访问数量，具体连接访问情况'''
    def __init__(self,log_path):
        super(logCat,self).__init__(log_path)

    def _only_get_apiurl(self,urlstr):
        x = urlstr.split('?')
        if len(x) == 1:
            return False
        else:
            return x[0]

    def run(self,log_file):
        result = {
                'pv':0,
                'uv':0,
                'status':{},
                'url':{},
                'client':{},
                }

        #获取已读取文件位置
        seek_dict = {}
        config_dir =  os.path.join(os.environ.get('HOME'),'.nlc')
        if not os.path.exists(config_dir):
          os.makedirs(config_dir)
        tag_file = os.path.basename(log_file)
        config_file = os.path.join(config_dir,tag_file)
      
        #判断日志是否已轮询
        mydate = datetime.now()
        date_str = mydate.strftime('%Y%m%d')
        target_file = log_file + '-' + date_str + '.gz'
        if not os.path.exists(target_file):
            for item in os.listdir(config_dir):
                if tag_file == item:
                #if log_file == item:
                    tmpfile = os.path.join(config_dir,item)
                    logging.info("remove tag file: " + tag_file)
                    os.remove(tmpfile)
                else:
                    continue
        #判断是否第一次读取
        if os.path.exists(config_file):
            cf = open(config_file,'r')
            curr_seek = cf.read()
            try:
                curr_seek = int(curr_seek)
            except:
                curr_seek = 0
            cf.close()
        else:
            curr_seek = 0

        f = open(log_file,'r')

        #判断文件是否有新增
        f.seek(0,os.SEEK_END)
        if curr_seek == f.tell():
            f.close()
            return None

        f.seek(curr_seek)

        for item in f.xreadlines():
            #获取http返回码
            try:
                jitem = json.loads(item)
            except:
                logging.warn('json can not load: ' + item)
                continue
            result['status'].setdefault(jitem['status'],0)
            result['status'][(jitem['status'])] += 1

            #获取请求url
            request_url = self._only_get_apiurl(jitem['url'])
            if request_url:
               result['url'].setdefault(request_url,0)
               result['url'][request_url] += 1

            #获取请求客户端IP
            result['client'].setdefault(jitem['clientip'],0)
            result['client'][(jitem['clientip'])] += 1

            #获取PV
            result['pv'] += 1

        #获取UV
        result['uv'] = len(result['client'].keys())

        lcurr_seek = f.tell()
        cf = open(config_file,'w')
        cf.write(str(lcurr_seek.real))
        read_row_number = lcurr_seek.real - int(curr_seek)
        if read_row_number != 0:
            #logging.info('read_row_number: ' + str(read_row_number))
            tmp_str = 'read row {} line from {}'.format(read_row_number,tag_file)
            logging.info(tmp_str)
            logging.info(result)
        cf.close()

        f.close()
        return result

    def run_all(self):
        result = {}
        abs_confs = self.get_confs()
        work_dict = self.map_path_with_servername()
        for servername,logpath in work_dict.items():
            tmp_result = self.run(logpath)
            if tmp_result != None:
                result[servername] = tmp_result
            else:
                continue
        return result

if '__main__' == __name__:
    mylogs = logCat('/etc/nginx/conf.d')
    #print mylogs.map_path_with_servername()
    #print mylogs.run('/data/logs/nginx/appservice.zeasn.tv_ssl.access.log')
    mylogs.run_all()
