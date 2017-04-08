#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import threading
import time
import urllib

import requests
from bson import ObjectId
from pymongo import MongoClient

import param

count = 0

import pymongo

a = pymongo.MongoClient()['demo']['data']


class Autoinj(threading.Thread):
    """
    	sqlmapapi 接口建立和管理sqlmap任务
    	by zhangh (zhanghang.org#gmail.com)
    	php install requests
    """

    def __init__(self, server='', target='', method='', data='', cookie='', referer=''):
        threading.Thread.__init__(self)
        self.server = server
        if self.server[-1] != '/':
            self.server = self.server + '/'
            # if method == "GET":
            # self.target = target + '?' + data
            # else:
            # self.target = target
        self.target = target
        self.taskid = ''
        self.engineid = ''
        self.status = ''
        self.method = method
        self.data = data
        self.referer = referer
        self.cookie = cookie
        self.start_time = time.time()
        # print "server: %s \ttarget:%s \tmethod:%s \tdata:%s \tcookie:%s" % (self.server, self.target, self.method, self.data, self.cookie)

    def task_new(self):
        code = urllib.urlopen(self.server + param.task_new).read()
        self.taskid = json.loads(code)['taskid']
        return True

    def task_delete(self):
        url = self.server + param.task_del
        url = url.replace(param.taskid, self.taskid)
        requests.get(url).json()

    def scan_start(self):
        headers = {'Content-Type': 'application/json'}
        url = self.server + param.scan_task_start
        url = url.replace(param.taskid, self.taskid)
        data = {'url': self.target}
        t = requests.post(url, data=json.dumps(data), headers=headers).text
        t = json.loads(t)
        self.engineid = t['engineid']
        return True

    def scan_status(self):
        url = self.server + param.scan_task_status
        url = url.replace(param.taskid, self.taskid)
        self.status = requests.get(url).json()['status']

    def scan_data(self):
        url = self.server + param.scan_task_data
        url = url.replace(param.taskid, self.taskid)
        return requests.get(url).json()

    def option_set(self):
        headers = {'Content-Type': 'application/json'}
        url = self.server + param.option_task_set
        url = url.replace(param.taskid, self.taskid)
        data = {}
        if self.method == "POST":
            data["data"] = self.data
        if len(self.cookie) > 1:
            data["cookie"] = self.cookie
        # print data
        data['crawlDepth'] = 5
        data['threads'] = 10
        data['forms'] = True
        data['smart'] = True
        data['is-dba'] = True
        t = requests.post(url, data=json.dumps(data), headers=headers).text
        t = json.loads(t)

    def option_get(self):
        url = self.server + param.option_task_get
        url = url.replace(param.taskid, self.taskid)
        return requests.get(url).json()

    def scan_stop(self):
        url = self.server + param.scan_task_stop
        url = url.replace(param.taskid, self.taskid)
        return requests.get(url).json()

    def scan_kill(self):
        url = self.server + param.scan_task_kill
        url = url.replace(param.taskid, self.taskid)
        return requests.get(url).json()

    def scan_log(self):
        url = self.server + param.scan_task_log
        url = url.replace(param.taskid, self.taskid)
        return requests.get(url).json()

    def start_test(self):
        global count
        # 开始任务
        # self.target=que.get()
        self.start_time = time.time()
        if not self.task_new():
            print("Error: task created failed.")
            return False
        # 设置扫描参数
        self.option_set()
        # 启动扫描任务
        if not self.scan_start():
            print("Error: scan start failed.")
            return False
        # 等待扫描任务

        while True:
            self.scan_status()
            if self.status == 'running':
                time.sleep(5)
            elif self.status == 'terminated':
                break
            else:
                print "unkown status"
                break
            if time.time() - self.start_time > 3000:  # 多于五分钟
                error = True
                print('删除一个不怎么带劲的IP:%s' % self.target)
                count += 1
                self.scan_stop()
                self.scan_kill()
                return [self.target, {'status': 'speed too much time'}]

        # 取结果
        res = self.scan_data()
        # 删任务
        #        self.task_delete()


        print(res['data'])
        if res['data']:
            count += 1
            print("耗时:" + str(time.time() - self.start_time))
            print('已经检测%d个网站' % count)
            return {self.target: {'data': self.scan_data(), 'log': self.scan_log()}}
        else:
            count += 1
            print("耗时:" + str(time.time() - self.start_time))
            print('已经检测%d个url %s' % (count, self.target))
            return {self.target: 0}

    def run(self):
        while True:
            target = a.find_one_and_update({'scanned': {'$exists': False}}, {'$set': {'scanned': 0}})
            if not target:
                print 'no target'
                time.sleep(100)
                continue
            # a.update({'_id': ObjectId(target['_id'])}, )
            self.target = target['target']
            t = self.start_test()
            try:
                a.update({'_id': ObjectId(target['_id'])}, {'$set': {'scanned': 1, 'scan_result': t.values()}})
            except Exception:
                a.update({'_id': ObjectId(target['_id'])}, {'$set': {'scanned': 1, 'scan_result': None}})  # 懒得想了


if __name__ == '__main__':
    start_time = time.time()
    cl = MongoClient()['demo']['scanner']
    things = [i['target'] for i in cl.find()]
    print things
    used_tag = set()
    for i in things:
        if i not in used_tag:
            print i
            used_tag.add(i)  # @todo 在Scan的过程中连接失败的话把这个节点移除
            Autoinj(i).start()  # adminid 5d6b91ceb538c08299e4a5d0cb22912a
            Autoinj(i).start()
            Autoinj(i).start()
            Autoinj(i).start()
            Autoinj(i).start()
            Autoinj(i).start()
            Autoinj(i).start()
