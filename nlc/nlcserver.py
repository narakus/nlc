#!/usr/bin/env python
#-*- coding:utf-8 -*-

import config
from flask import  Flask,request,jsonify
from flask.ext.script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

class SmartTv(db.Model):
    __tablename__ = 'smarttv_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)
    
    def __repr__(self):
        return '<nlc %r>' % ('smarttv.zeasn.tv')

class AppsTv(db.Model):
    __tablename__ = 'apps_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)

    def __repr__(self):
        return '<nlc %r>' % ('apps.zeasn.tv')

class ProductTv(db.Model):
    __tablename__ = 'product_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)

    def __repr__(self):
        return '<nlc %r>' % ('product.zeasn.tv')

class RecommendTv(db.Model):
    __tablename__ = 'recommend_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)

    def __repr__(self):
        return '<nlc %r>' % ('recommend.zeasn.tv')


class TouTv(db.Model):
    __tablename__ = 'tou_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)

    def __repr__(self):
        return '<nlc %r>' % ('tou.zeasn.tv')

class TvappTv(db.Model):
    __tablename__ = 'tvapp_zeasn_tv'
    id = db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    pv = db.Column(db.Integer,nullable=False)
    uv = db.Column(db.Integer,nullable=False)
    state = db.Column(db.Text(256),nullable=True)
    request_url = db.Column(db.String(128),nullable=True)
    create_date = db.Column(db.Date,nullable=False)

    def __repr__(self):
        return '<nlc %r>' % ('tvapp.zeasn.tv')

db.create_all()

import json
from datetime import date,datetime

app = Flask(__name__)
manger = Manager(app)

@app.route('/api/nlc',methods=['POST'])
def nlc():
    data = request.get_data()
    json_obj = json.loads(data)
    for domain,it in json_obj.items():
        t = eval(config.t_d[domain])
        m = t.query.filter(t.create_date==date.today()).first()
        if m == None:
            n = t(pv=it['pv'],uv=it['uv'],
                  state=json.dumps(it['status']),create_date=date.today())
            db.session.add(n)
        else:
            m.pv = it['pv'] + m.pv
            m.uv = it['uv'] + m.uv
            curr_stat = json.loads(m.state)
            t_stat = it['status']
            mystat = {}
            for stat,value in curr_stat.items():
                if t_stat.has_key(stat):
                    value = t_stat[stat] + value
                    mystat[stat] = value
                else:
                    mystat[stat] = value
            m.state = json.dumps(mystat) 
        db.session.commit()
    return jsonify({'success':True})

@app.route('/api/query',methods=['GET'])
def query():
    domain = request.args.get('domain')
    mydate = request.args.get('date')
    if config.t_d.has_key(domain):
        t = eval(config.t_d[domain])
        if mydate == None:
            m = t.query.filter(t.create_date==date.today()).first()
        else:
            try:
                mydate_obj = datetime.strptime(mydate,'%Y%m%d')
                m = t.query.filter(t.create_date==mydate_obj).first()
            except:
                return jsonify({'error':True})
        if m != None:
            mydate = m.create_date
            return jsonify({'pv':m.pv,'uv':m.uv,'state':json.loads(m.state),
                           'date':mydate.strftime('%Y%m%d')})
        else:
            return jsonify({'result':None})
    else:
        return jsonify({'result':None})

if __name__ == '__main__':
    manger.run()
