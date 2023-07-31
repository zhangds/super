#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/31 下午1:54
# @Author  : zhangds
# @File    : sysUserController.py
# @Software: PyCharm
import sys, os
from common.utils import MetaDB, sha256Helper, aseHelper, EmailUtils


class sysUserController(object) :
    def __init__(self, config) :
        if config is not None :
            self.config = config

        print(self.config, file=sys.stderr)
        if self.config is None :
            print("!!!!!!!!!无法配置文件", file=sys.stderr)
            return
        else :
            self.metadb = MetaDB.instance(self.config)

    def addUser(self, userId, cnname, password, phone, mail) :
        # sql = "SELECT id, api_code, datasource, tbname, keyfield, sql_template,para,para_order FROM sys_api_list where api_code='%s'" % apiCode
        # apiInfo = self.metadb.queryForMap(sql)
        # return apiInfo
        if not self.metadb :
            raise Exception('元数据未配置!')
        sql = "select count(1) as NUMS from sys_user where USER_ID = '%s'" % userId
        count = self.metadb.queryForMap(sql)
        if count and count.get('NUMS') > 0 :
            return {"status" : "error", "message" : r'用户ID已经存在!'}
        else:
            _pwd, _salt = sha256Helper().encrypt(password)
            _sql = "insert into sys_user(user_id, username, cnname, password, phone, mail, salt) values('%s', '%s','%s', '%s','%s', '%s', '%s')" \
                   % (userId, userId, cnname, _pwd, aseHelper().encrypt(phone),
                      aseHelper().encrypt(mail), _salt)
            self.metadb.excuteSql(_sql)
        return {"status": "ok", "message": r'用户添加成功!'}

    def checkUser(self, userId, password) :
        sql = "select salt,password from sys_user where USERNAME='%s'" % \
              userId
        dbResult = self.metadb.queryForMap(sql)
        if dbResult:
            salt = dbResult.get("SALT")
            _pwd, _salt = sha256Helper(salt).encrypt(password)
            print(_pwd, dbResult.get("PASSWORD"))
            if _pwd == dbResult.get("PASSWORD"):
                return {"status": "ok", "message": r'用户登录成功!'}
        return {}

    def userInfo(self, userId):
        sql = "select a.user_id, a.username, a.cnname, a.phone, a.mail," \
              " a.head_img, a.state,a.eff_time, a.state_time, a.remark," \
              " a.area_code, a.role, a.dept_id,b.ENT_NAME from sys_user a " \
              "left join sys_enterprise b on a.dept_id = b.ENT_ID " \
              "where a.USERNAME='%s'" % userId
        dbResult = self.metadb.queryForMap(sql)
        if dbResult :
            mail = dbResult.get("MAIL") if dbResult.get("MAIL") else ""
            phone = dbResult.get("PHONE") if dbResult.get("PHONE") else ""
            return {
                "code" : 0,
                "msg" : "",
                "data" : {
                    "userInfo" : {
                        "servEnv" : "python",  ###兼容store，ajax的参数处理
                        "userCode" : userId,  # --
                        "userName" : dbResult.get("USERNAME"),
                        "phone" : aseHelper().decrypt(phone) if phone != "" else "",
                        "mail" : aseHelper().decrypt(mail) if mail != "" else "",
                        "state" : "ENABLED",
                        "userType" : "web",
                        "role": dbResult.get("ROLE"),
                        "deptId" : dbResult.get("DEPT_ID"),
                        "deptName" : dbResult.get("ENT_NAME")
                    }
                }
            }
        return {}

    def forget(self, userId, configs, uri="") :
        try :
            if userId != "" and configs :
                sql = "select count(1) as NUMS from sys_user where USER_ID = '%s'" % userId
                count = self.metadb.queryForMap(sql)
                if count and count.get('NUMS') > 0 :
                    _pwd, _salt = sha256Helper().encrypt(configs.get('INIT_PWD'))
                    _sql = "update sys_user set PASSWORD='%s',SALT='%s' where user_id='%s'" % (_pwd, _salt, userId)
                    self.metadb.excuteSql(_sql)
                    EmailUtils(configs.get('EMAIL_HOST'), configs.get('EMAIL_PORT'),
                               configs.get('EMAIL_USER'), configs.get('EMAIL_PWD'),
                               configs.get('EMAIL_SENDER')).sendEmail(['zhang198058@hotmail.com', 'zhangds@faithindata.com.cn'],
                           "密码初始化", "网站:%s\n网址:%s\n用户id:%s\n密码初始化完成!初始密码为:%s" %
                                                                      (configs.get('APP_NAME'), uri, userId, configs.get('INIT_PWD')))
        except Exception as e:
            pass
        return {}
        # 'EMAIL_HOST'

