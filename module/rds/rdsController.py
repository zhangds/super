#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 下午6:14
# @Author  : zhangds
# @File    : rdsController.py
# @Software: PyCharm

import sys, os
from common.utils import aseHelper, httpRequestUtil
from ftplib import FTP
import datetime
import demjson

import json

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from common.utils import Config, MetaDB


class rdsController(object) :
    def __init__(self, config=None) :
        if config is not None :
            self.config = config
        # 元数据库初始化
        print(self.config, file=sys.stderr)
        if self.config is None :
            print("!!!!!!!!!无法配置文件", file=sys.stderr)
            return
        else :
            self.metadb = MetaDB.instance(self.config)
            self.vm_path = self.config.get("rdsModels").get("MW_DOCKER_BASH_PATH")
            self.local_path = self.config.get("rdsModels").get("LOCAL_FILE_PATH")

    def export2File(self, userId, tabId, columns) :
        _key, _tabName, _schema, _driver, _url, _user, _pwd = None, None, None, None, None, None, None
        _columns, export_sql, filePath = None, None, None
        if userId != "" :
            # FIXME 获取加密key,存在问题，不同的算法需要不同的key
            _key = 'nF8vba92Tofkyr1sy9uUVw=='
        if _key and tabId != "" and self.vm_path and self.local_path :
            # 获取加密表的信息
            _result = self.metadb.queryForMap("select A.tab_id,a.tab_name,A.DB_NAME, \
                                              A.SCHEMA_NAME,b.DRIVER_CLASSNAME,b.URL,b.USER_NAME,b.PASSWORD \
                                              from meta_table_tpl A,sys_dblist B where A.TAB_ID='%s' \
                                              and A.db_name = B.db_name" % tabId)
            if _result :
                _tabName, _schema, _driver, _url, _user, _pwd = _result.get("TAB_NAME"), _result.get("SCHEMA_NAME"), \
                                                                _result.get("DRIVER_CLASSNAME"), _result.get("URL"), \
                                                                _result.get("USER_NAME"), _result.get("PASSWORD")
                _pwd = aseHelper().decrypt(_pwd) if _pwd and _pwd != "" else ""
                _url = _url if "serverTimezone" in _url else (_url + "&serverTimezone=UTC")
                # print(_tabName, _schema, _driver, _url, _user, _pwd)
        if _key and _tabName and _schema and _driver and _url and _user and _pwd :
            if columns != "" :
                _columns = columns.split(",")
                _columns = ["'%s'" % one for one in _columns]
                print(",".join(_columns))
            _sql = "select COL_NAME,COL_TYPE,ENCY_TYPE1,COL_SEQ from cypt_table_column where TAB_ID='%s'" % tabId
            if _columns and 0 < len(_columns) :
                _sql = '%s and lower(COL_NAME) in (%s)' % (_sql, ",".join(_columns))
            columnResult = self.metadb.queryForList(_sql)
            if _key and columnResult and 0 < len(columnResult) :
                columnResult = ["%s(%s,'%s') as %s" % (k.get('ENCY_TYPE1'), k.get('COL_NAME'), _key, k.get('COL_NAME')) for k in columnResult if k.get('COL_NAME') and \
                                k.get('COL_NAME') != "" and k.get('ENCY_TYPE1') and \
                                k.get('ENCY_TYPE1') != ""]
                # print(",".join(columnResult))
                export_sql = "select %s from %s.%s" % (",".join(columnResult), _schema, _tabName)
                if export_sql :
                    data = {
                        "operateType" : 1,
                        "jobName" : "encrypt_query_test1",
                        "jdbcSourceConfig" : [{
                            "jdbcUrl" : _url,
                            # "jdbcUrl" : "jdbc:mysql://192.168.3.198:3306/test?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC&useSSL=false",
                            "username" : _user,
                            "password" : _pwd,
                            "table" : "%s.%s" % (_schema, _tabName)
                        }],
                        "filename" : "%s.csv" % _tabName,
                        "output" : os.path.join(self.vm_path, _tabName),
                        "sql" : export_sql
                    }
                    print(json.dumps(data))
                    res = httpRequestUtil("http://127.0.0.1:10001/spark/exec/sql").doAction("POST", headers={"Content-Type" : "application/json"}, json=data)
                    if res and res.status_code == 200 :
                        print(res.text)
                        res = json.loads(res.text)
                        if res.get("code") == 200 :
                            filePath = res.get("data")
        if filePath :
            print(filePath)
            ftp = FTP()
            ftp.connect('127.0.0.1', 21)
            ftp.login('admin', '123456')
            dir_res = []
            ftp.dir('.', dir_res.append)
            try :
                ftp.cwd(_tabName)
            except :
                ftp.mkd(_tabName)
            with open(os.path.join(os.path.join(self.local_path, _tabName), "%s.csv" % _tabName), 'rb') as fp :
                print('STOR %s/%s-%s.csv' % (_tabName, _tabName, datetime.datetime.now().strftime('%Y%m%d%H%M%S%s')[:-7]))
                ftp.storbinary('STOR %s/%s-%s.csv' % (_tabName, _tabName, datetime.datetime.now().strftime('%Y%m%d%H%M%S%s')[:-7]), fp)
                # ftp.storbinary('STOR %s' % ("%s/%s.csv" % (_tabName, _tabName)), fp)

            ftp.quit()
            ftp.close()
        pass
