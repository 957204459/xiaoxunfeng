# encoding: utf-8
import os

from bson.objectid import ObjectId
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from pymongo import MongoClient

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask('app', template_folder=tmpl_dir, static_folder=static_dir)
app = Flask(__name__)

demo_db = MongoClient()['demo']['data']
t = MongoClient()['demo']['temp']
m_cli = demo_db


@app.route('/')
def hello_world():
    global m_cli
    if request.method == 'GET':
        c = []
        d = 0
        count = m_cli.count()
        c = m_cli.find().limit(50)
        return render_template('index.html', host=c, count=count, key='all', Title='资产概览'.decode('utf-8'))


@app.route('/info/<_id>')
def info(_id):
    print _id
    a = m_cli.find_one({'_id': ObjectId(_id)})
    a['_id'] = None
    return jsonify(a)


@app.route('/add_scanner/', methods=['POST', 'GET'])
def add_scanner():
    cl = MongoClient()['demo']['scanner']
    if request.method == 'GET':
        scanner = '\r\n'.join([i['target'] for i in cl.find()])
        print scanner
        return render_template('addtag.html', current_scanner=scanner)
    else:
        req = request.form['comment']
        print 'xxx'
        for i in req.split('\n'):
            # print {'target':i.strip()}
            target = i.strip()
            print 'insert %s' % target
            if 'http' not in target[0:5]:
                target = 'http://%s' % target
            cl.insert({'target': target})
            print 'insert %s' % target
        return render_template('add_success.html')


@app.route('/scanner_status')
def scanner_status():
    pass


@app.route('/sqlinj')
def return_sqlinj():
    c = [i for i in demo_db.find({'scan_result.data.success': True})]
    print 'None'
    return render_template('index.html', host=c, key='all')


@app.route('/add', methods=['GET', 'POST'])
def return_add():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        req = request.form['comment']
        for i in req.split('\n'):
            target = i.strip()
            if 'http' not in target[0:5]:
                target = 'http://%s' % target
            t.insert_one({'target': target})
        return render_template('add_success.html')


@app.route('/xunfeng')
def return_xunfeng():
    return render_template('xunfeng.html')


@app.route('/scanner_add')
def scanner_add():
    return render_template('addtag.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/status')
def status():
    inj_count = demo_db.find({'scan_result.data.success': True}).count()
    all = demo_db.find().count()
    scanned = demo_db.find({'scanned': {'$exists': True}}).count()
    return render_template('status.html', has_scaned=scanned, inj_count=inj_count, remain=all - scanned)


@app.route('/search/')
def search():
    domain = request.args['domain']
    count = m_cli.find({'target': {'$regex': '%s' % domain}}).count()
    host = m_cli.find({'target': {'$regex': '%s' % domain}}).limit(200)
    return render_template('index.html', host=host, count=count, key=domain)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0')
