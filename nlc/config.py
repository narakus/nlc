# -*- config:utf-8 -*-

DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'root'
HOST = '127.0.0.1'
PASSWORD = 'zeasn2018'
PORT = 3306
DATABASE = 'nlc'

SQLALCHEMY_DATABASE_URI  = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,
                                               USERNAME,PASSWORD,HOST,PORT,DATABASE)

SQLALCHEMY_TRACK_MODIFICATIONS = False

t_d = {
       'smarttv.zeasn.tv':'SmartTv',
       'apps.zeasn.tv':'AppsTv',
       'product.zeasn.tv':'ProductTv',
       'recommend.zeasn.tv':'RecommendTv',
       'tou.zeasn.tv':'TouTv',
       'tvapp.zeasn.tv':'TvappTv',
      }
