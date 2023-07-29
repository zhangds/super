#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午4:53
# @Author  : zhangds
# @File    : ApiCodeControler.py
# @Software: PyCharm
import sys, os
import demjson
# import json

# import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from common.utils import Config, MetaDB


class ApiCodeControler(object) :
    def __init__(self, fileName="", config= None) :
        if config is not None :
            self.config = config
        elif fileName != "" :
            self.config = Config(fileName)
        else :
            self.config = config
        # 元数据库初始化
        print(self.config, file=sys.stderr)
        if self.config is None :
            print("!!!!!!!!!无法配置文件", file=sys.stderr)
            return
        else :
            # print("配置文件:",self.config.get("metadb"))
            self.metadb = MetaDB.instance(self.config)

    def getApiInfo(self, apiCode) :

        sql = "SELECT id, api_code, datasource, tbname, keyfield, sql_template,para,para_order FROM sys_api_list where api_code='%s'" % apiCode
        apiInfo = self.metadb.queryForMap(sql)
        return apiInfo

    def processSqlParam(self, sqltext="", paramTplStr="", paramValMap={}, orderStr="") :
        newSql = sqltext
        if paramValMap is None :
            paramValMap = {}

        paramMap = {}
        if paramTplStr is not None and paramTplStr != "" :
            paramMap = demjson.decode(paramTplStr)
        # paramMap=json.loads(paramTplStr)

        whereArray = []

        for key in paramValMap :
            newSql = newSql.replace("{" + key + "}", str(paramValMap[key]) + "")
            if paramMap.get(key) is not None :
                paraStr = paramMap[key].replace("‘", "'").replace("’", "'")
                paraVal = paramValMap[key].replace("‘", "'")
                whereArray.append(paraStr.replace("{" + key + "}", str(paraVal)) + " ")

        print(" and ".join(whereArray))
        if len(whereArray) == 0 :
            return newSql

        if newSql.find(" where ") == -1 :
            newSql += " where " + " and ".join(whereArray)
        else :
            newSql += " and " + " and ".join(whereArray)

        return newSql

    def getPageSql(self, sqltext, start, limit, orderStr) :
        if limit == -1 or limit == "-1" :
            return sqltext

        sqltext += " limit {},{}".format(start, limit)
        if orderStr is not None and orderStr != "" :
            sqltext += " " + orderStr
        return sqltext

    ###sql查询数据
    def querySqlData(self, initSql, start=0, limit=50, params={}, para_order="") :
        print("** startinitSql=", initSql, ",start=", start, ",limit=", limit, ",params=", params, file=sys.stderr)
        newSql = initSql
        total = self.metadb.getQuerySQLCount(newSql)

        fields = self.metadb.getSqlColums(newSql)
        # print("fields:",fields, file=sys.stderr)
        columns = fields
        dataSql = self.getPageSql(newSql, start, limit, para_order)
        root = self.metadb.queryForList(dataSql)
        result = {"count" : total, "fields" : fields, "root" : root, "success" : True, "msg" : dataSql}
        # print(result)
        return result

    def queryApiData(self, apiCode, start=0, limit=50, params={}, para_order="", apiInfoDict=None) :
        print("** startapiCode=", apiCode, ",start=", start, ",limit=", limit, ",params=", params, file=sys.stderr)
        apiInfo = apiInfoDict if apiInfoDict else self.getApiInfo(apiCode)
        print("apiInfo:", apiInfo, file=sys.stderr)
        newSql = self.processSqlParam(apiInfo['SQL_TEMPLATE'], apiInfo.get('PARA', ""), params)
        total = self.metadb.getQuerySQLCount(newSql)

        fields = self.metadb.getSqlColums(newSql)
        # print("fields:",fields, file=sys.stderr)
        columns = fields
        dataSql = self.getPageSql(newSql, start, limit, para_order)
        root = self.metadb.queryForList(dataSql)
        result = {"count" : total, "fields" : fields, "root" : root, "success" : True, "msg" : dataSql}
        # print(result)
        return result

    def insertApiData(self, apiCode, records, apiInfoDict=None) :
        apiInfo = apiInfoDict if apiInfoDict else self.getApiInfo(apiCode)
        tabname = apiInfo.get("TBNAME", "")
        if tabname == "" :
            return {"success" : False, "msg" : apiCode + ",没有配置表名"}
        else :
            tabfieldArray = self.metadb.getTabColums(tabname)
            tabfields = []
            for field in tabfieldArray :
                tabfields.append(field.get("name"))
            result = self.metadb.insertData(records, tabname, tabfields)
            return {"success" : True, "status" : "ok", "msg" : apiCode + ",成功插入条数：" + str(result)}

    def deleteApiData(self, apiCode, records, apiInfoDict=None) :
        apiInfo = apiInfoDict if apiInfoDict else self.getApiInfo(apiCode)
        tabname = apiInfo.get("TBNAME", "")
        keyField = apiInfo.get("KEYFIELD", "")
        if tabname == "" :
            return {"status" : "error", "msg" : apiCode + ",没有配置表名"}
        elif keyField == "" :
            return {"success" : False, "msg" : apiCode + ",没有配置keyfield"}
        else :
            sumDelNum = 0
            for row in records :
                result = self.metadb.deleteData(tabname, row, keyField)
                sumDelNum = sumDelNum + result
            return {"success" : True, "status" : "ok", "msg" : apiCode + ",成功删除条数：" + str(sumDelNum)}
        pass

    def updateApiData(self, apiCode, records, apiInfoDict=None) :
        apiInfo = apiInfoDict if apiInfoDict else self.getApiInfo(apiCode)
        tabname = apiInfo.get("TBNAME", "")
        keyField = apiInfo.get("KEYFIELD", "")
        if tabname == "" :
            return {"status" : "error", "msg" : apiCode + ",没有配置表名"}
        elif keyField == "" :
            return {"success" : False, "msg" : apiCode + ",没有配置keyfield"}
        else :
            sumDelNum = 0
            status = "ok"
            success = True
            for row in records :
                result, msg = self.metadb.updateData(tabname, row, keyField)
                if result is not None and result == -1 :
                    status = "error"
                    success = False
                sumDelNum = sumDelNum + result if sumDelNum is not None else 0
            return {"success" : success, "status" : status, "msg" : msg}
        pass


if __name__ == '__main__' :
    config = Config('/Users/wangqs/Documents/source/mlink-code/python/apiService/config.json')
    apiCodeControler = ApiCodeControler('../../config.json', config)
    apiCodeControler.queryApiData("sysUser", limit=-1, params={"limit" : -1})
    # apiInfo=apiCodeControler.getApiInfo('sysUser')
    # print(apiInfo)
    # print(apiCodeControler.processSqlParam('select * from sys_user where name = \'{name}\' ','{"name":" user_name=\'{name}\'","id":"user_id={id}"}',{"name":"wangqs","id":1}))
    # newSql=apiCodeControler.processSqlParam(apiInfo['sql_template'],apiInfo['para'],{"username":"wangqs","cnname":1},"order by user_name")
    # print(newSql)
    # print(apiCodeControler.queryForData(newSql))
    # print(apiCodeControler.getPageSql(newSql,100,30,''))

