#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午3:20
# @Author  : zhangds
# @File    : config.py.py
# @Software: PyCharm
import json
import os
import sys
import requests
import logging
import time
from importlib import import_module
from logging.handlers import RotatingFileHandler


class Config(object):
    """
    # Config().get_content("user_information")

    配置文件里面的参数
    [notdbMysql]
    host = 192.168.1.101
    port = 3306
    user = root
    password = python123
    """
    _instance: None
    _cookie: None

    def __init__(self, config_filename="config.json"):
        if config_filename=="":
            print("配置文件为空", file=sys.stderr)
            return
        print("cur config_filename dir:", config_filename)
        Config._cookie = None
        Config._instance = self
        self.config_filename = config_filename
        self.configData = self.readConfig(config_filename)
        self.logger = None

    @classmethod
    def instance(cls, *args, **kwargs):

        if not hasattr(Config, "_instance"):
            Config._instance = Config(*args, **kwargs)
        return Config._instance

    # 读取配置文件
    def readConfig(self, config_filename):
        """"读取配置"""
        with open(config_filename, encoding='utf-8') as json_file:
            config = json.load(json_file)
        return config

    def update_config(self):
        """"更新配置"""
        with open("config.json", 'w') as json_file:
            json.dump(config, self.config_filename, indent=4)
        return None

    # 支持从列表中按name的属性判断key值
    def get(self, key, key1=None, key2=None):
        result = self.configData.get(key)
        if key1 is not None and result is not None:
            result = self.getSubKeyVal(result, key1)
        if key2 is not None and result is not None:
            result = self.getSubKeyVal(result, key2)
        return result

    def getSubKeyVal(self, val, subkey):
        result = None
        if type(val) == list:
            for item in val:
                if item.get("name") == subkey:
                    result = item
        elif type(val) == dict:
            result = val.get(subkey)
        return result

    def getArrayItemByKey(self, arrayData, key, keyVal):
        for item in arrayData:
            if item.get(key) == keyVal:
                return item
        return None

    def getDBConfig(self, dbName):
        db = self.get("dblist", dbName)
        if db is None:
            db = self.getDBConfigFromDatago(dbName)
        return db

    def getDBConfigFromDatago(self, dbName):
        res = self.getDataGoFromUrl("/dimmgr/info/dimDB")
        dbList = json.loads(res)
        for db in dbList:
            if db.get('db_name') == dbName:
                decryptPass = self.getDataGoFromUrl("/crypto/decrypt?message=" + db.get("password"))
                cfgDbList = self.get("dblist")
                cfgDb = {"name": db.get("db_name"), "type": db.get("db_type"), "url": db.get("url"),
                         "user": db.get("user_name"), "password": decryptPass}

                strList = db.get("url").split(":")
                host = strList[2].replace("//", "")
                str2List = strList[3].split("/")
                port = str2List[0]
                db = str2List[1]
                cfgDb["host"] = host
                cfgDb["port"] = int(port)
                cfgDb["db"] = db
                cfgDbList.append(cfgDb)

                return cfgDb

    def getDataGoFromUrl(self, url):
        s = requests.session()
        if url.find("http") < 0:
            datagoWebCfg = self.get("datagoweb")
            host = datagoWebCfg.get("host")
            url = host + url
        cookies = self.getDataGoLoginCookie()

        r = s.get(url=url, cookies=cookies)
        return r.text

    def getDataGoLoginCookie(self):
        if Config._cookie != None:
            return Config._cookie
        try:
            s = requests.session()
            datagoWebCfg = self.get("datagoweb")
            loginUrl = datagoWebCfg.get("loginurl")  # 'http://localhost:18080/sys/login'
            postData = {'username': datagoWebCfg.get("user"), 'password': datagoWebCfg.get("password"),
                        'captcha': ''}
            print("后台模拟登录....")
            rs = s.post(loginUrl, postData)
            c = requests.cookies.RequestsCookieJar()  # 利用RequestsCookieJar获取
            s.cookies.update(c)
            Config._cookie = s.cookies.get_dict()
            return Config._cookie
        except:
            print("登录datago-web失败！")

    ######log 操作
    # log配置，实现日志自动按日期生成日志文件
    def make_dir(self, make_dir_path):
        print(make_dir_path)
        path = make_dir_path.strip()
        if not os.path.exists(path):
            os.makedirs(path)

    def initLoger(self, logger=None, logfileName="gosql.log", optime=""):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''
        if self.logger is not None:
            return self.logger
        print("############init logger,config.py")
        if optime == '':
            optime = time.strftime("%Y%m%d")
        # 创建一个logger
        if logger == None:
            self.logger = logging.getLogger(logger)
        else:
            self.logger = logger

        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        self.log_time = optime
        self.log_path = "logs/" + optime + "/"
        print(self.log_path , logfileName)
        self.log_name = self.log_path + logfileName
        self.make_dir(self.log_path)

        fh = logging.handlers.RotatingFileHandler(
            filename=self.log_name,
            maxBytes=1024 * 1024 * 50,
            backupCount=5,
            encoding='utf-8'
        )

        # fh = logging.FileHandler(self.log_name, 'a')
        # fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        #  添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getLogger(self, logfileName="gosql.log", optime=""):
        if self.logger is None:
            self.initLoger(logfileName=logfileName, optime=optime)
        return self.logger

    # 动态加载包
    def getClass(self, classPath, className):
        allObj = globals()
        calssObj = allObj.get(className)
        if calssObj is None:
            calssObj = getattr(import_module(classPath), className)
        return calssObj

    # 动态加载包
    def getClassMethod(self, classPath, className, methodName):
        allObj = globals()
        calssObj = allObj.get(className)
        if calssObj is None:
            calssObj = getattr(import_module(classPath), className)
        if calssObj is not None:
            f = getattr(calssObj, methodName)
            return f,calssObj
        return None

    def getDBDriver(self, dbname):
        dbOptions = self.getDBConfig(dbname)

        dbtype = dbOptions.get("type")
        dbconfig = self.get("plats", dbtype)
        classObj = self.getClass(dbconfig.get("classPath"), dbconfig.get("className"))
        # module_meta = __import__(dbconfig.get("classPath"), globals(), locals(), [dbconfig.get("className")])
        # class_meta = getattr(module_meta, dbconfig.get("className"))
        driver = classObj(dbOptions)
        return driver

    def getDBDriverByDbOptions(self, proc, dbname, init=True):
        dbOptions = proc.metadb.queryForMap(
            "select URL as 'url',USER_NAME as 'user',`PASSWORD` as 'password',DB_TYPE as 'type' from sys_dblist where DB_CODE='{0}'".format(
                dbname))
        # jdbc:mysql://10.168.11.124:3306/mlink_db
        if dbOptions is not None and dbOptions.get('url').startswith('jdbc:mysql'):
            url = dbOptions.get('url')
            dbOptions['host'] = url.split("//", 1)[1].split(":", 1)[0]
            dbOptions['port'] = int(url.split("//", 1)[1].split(":", 1)[1].split("/", 1)[0])
            dbOptions['db'] = url.split("//", 1)[1].split(":", 1)[1].split("/", 1)[1]
            dbOptions['charset'] = 'utf8'
            dbtype = dbOptions.get("type")
            dbconfig = self.get("plats", dbtype)
            classObj = self.getClass(dbconfig.get("classPath"), dbconfig.get("className"))
            driver = classObj(dbOptions,init=init)
            return driver
        else:
            self.getDBDriver(dbname)

    def getDriver(self, driverType):
        dbconfig = self.get("plats", driverType)
        print(dbconfig)
        classObj = self.getClass(dbconfig.get("classPath"), dbconfig.get("className"))
        # module_meta = __import__(dbconfig.get("classPath"), globals(), locals(), [dbconfig.get("className")])
        # class_meta = getattr(module_meta, dbconfig.get("className"))
        driver = classObj()
        return driver


if __name__ == '__main__':
    config = Config("../../config.json")
    print(config.get("metadb"))
    url = 'jdbc:mysql://10.168.11.124:3306/mlink_db'
    print(url.startswith('jdbc:mysql'))
    print(url.split("//", 1))
    print(url.split("//", 1)[1].split(":", 1))
    print(url.split("//", 1)[1].split(":", 1)[0])
    print(url.split("//", 1)[1].split(":", 1)[1].split("/", 1)[0])
    print(url.split("//", 1)[1].split(":", 1)[1].split("/", 1)[1])
    pass
