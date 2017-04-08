import datetime
import hashlib
import re
import socket
import time
from urlparse import urlparse

import pymongo
import requests
from bson import ObjectId

temp_cli = pymongo.MongoClient()['demo']['temp']
cli = pymongo.MongoClient()['demo']['data']


def do_sth(i):
    def get_ip(host):
        try:
            return socket.gethostbyname(host)
        except Exception:
            return None

    host = urlparse(i)[1]
    ip = get_ip(host)
    title = None
    if ip:
        try:
            req = requests.get(i, timeout=10)
        except Exception as e:
            return
            pass
        try:
            req.encoding = req.apparent_encoding
            title = re.findall('<title>(.*?)</title>', req.text, flags=re.I | re.M)
            if title:
                title = title[0]
            uniq_hash = hashlib.md5(req.content).hexdigest()
            cli.insert_one(
                {'target': i, 'ip': ip, 'title': title, 'add_time': datetime.datetime.utcnow(), 'domain': host,
                 'hash': uniq_hash
                 }
            )
        except Exception as e:
            print e
            pass

while True:
    for i in temp_cli.find({}):
        do_sth(i['target'])
        temp_cli.remove({'_id': ObjectId(i['_id'])})
    time.sleep(10)
print 'fick'
