#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 下午2:54
# @Author  : zhangds
# @File    : restfulUtils.py
# @Software: PyCharm
import requests
import json


class httpRequestUtil(object):
    def __init__(self, uri):
        """
        data={'key1':'value1','key2':'value2'}
        json=<josnStr>
        ----
        headers = {"User-Agent":"test request headers"}
        """
        self.uri = uri
        # self.type = type
        # for _key in kwargs.keys() :
        #     if hasattr(self, _key) :
        #         setattr(self, _key, kwargs[_key])

    def doAction(self, type= "POST", **kwargs):
        if type and type.upper() == "POST":
            return requests.post(self.uri, **kwargs)
        return {}


url = "http://127.0.0.1:10001/spark/exec/sql"
data = {
  "operateType": 1,
  "jobName" : "encrypt_query_test1",
  "jdbcSourceConfig" : [{
    "jdbcUrl" : "jdbc:mysql://192.168.3.198:3306/test?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC&useSSL=false",
    "username" : "root",
    "password" : "Datago@123",
    "table" : "test.staff"
  }],
  "filename" : "staff.csv",
  "output" : "/data/rds/encrypt/staff",
  "sql" : "select det(id,'nF8vba92Tofkyr1sy9uUVw==') as id ,det(phone,'nF8vba92Tofkyr1sy9uUVw==') as phone, det(edu,'nF8vba92Tofkyr1sy9uUVw==') as edu, ope(salary,'32,64') as salary, hom(salary,'xxxx') as salary1  from staff"
}
httpRequestUtil(url).doAction("post", json=data)
# resp = requests.post(url,  json=data)
# print(resp.text)
# data = {
#         "operateType": 2,
#         "sql": "select count(a.id) from staff a ,local_people b  where a.phone=det(b.phone,'\''nF8vba92Tofkyr1sy9uUVw=='\'') and a.salary > ope(3200,'\''32,64'\'')",
#         "jdbcSourceConfig": [
#                 {
#                         "password": "Datago@123",
#                         "jdbcUrl": "jdbc:mysql://192.168.3.198:3306/test?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC&useSSL=false",
#                         "table": "local_people",
#                         "username": "root"
#                 }
#         ],
#         "fileSourceConfig": [
#                 {
#                         "path": "/data/rds/encrypt/staff/staff.csv",
#                         "type": "csv",
#                         "table": "staff"
#                 }
#         ],
#         "jobName": "eb15be25-8803-4c03-b647-4bd3b4c1cd97",
#         "output": "null"
# }
# resp = requests.post(url,  json=data)
# print(resp.text)