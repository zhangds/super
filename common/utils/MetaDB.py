#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午4:07
# @Author  : zhangds
# @File    : MetaDB.py
# @Software: PyCharm
import pymysql


class MetaDB(object) :
    _instance = None
    cursor = None

    def __init__(self, config, options={}) :
        # config = Config.instance(config_filename="gosql/conf/config.json")
        self.options = config.get("metadb")

        self.getConnection()
        MetaDB._instance = self

    def getConnection(self) :
        if self.cursor is None :
            opts = {'host' : self.options.get("host"),
                    'port' : self.options.get("port"),
                    'user' : self.options.get("user"),
                    'passwd' : self.options.get("password"),
                    'db' : self.options.get("db"),
                    'charset' : self.options.get("charset")
                    }
            self.conn = pymysql.connect(**opts)
            self.cursor = self.conn.cursor()
        # 保证conn丢失时自动重连
        self.conn.ping(reconnect=True)
        return self.cursor

    @classmethod
    def instance(self, config) :
        if MetaDB._instance is None :
            MetaDB._instance = MetaDB(config)
        return MetaDB._instance

    def transCursor2Dict(self, cursor, type='list') :
        colnames = [desc[0] for desc in cursor.description]
        resultData = []
        for result in cursor.fetchall() :
            i = 0
            rowdata = {}
            for field in colnames :
                rowdata[field.upper()] = result[i]
                i = i + 1
            # print("row1:",rowdata)
            resultData.append(rowdata)
        if type == 'list' :
            return resultData
        elif type == 'map' and len(resultData) >= 1 :
            return resultData[0]
        elif type == 'map' and len(resultData) == 0 :
            return None

    ##取sql查询的总记录数
    def getQuerySQLCount(self, sql) :
        cursor = self.getConnection()
        cursor.execute("select count(*) from ( " + sql + ") _tmp")
        result = cursor.fetchall()[0][0]
        return result

    ##取表的字段列表
    def getTabColums(self, tableName) :
        cursor = self.getConnection()
        # 用以获取列标题
        colSql = 'select * from {} limit 1'.format(tableName)
        # print("colSql:",colSql, file=sys.stderr)
        cursor.execute(colSql)
        # for col in cursor.description:
        #     print(cursor.description)
        columns = [col[0] for col in cursor.description]
        fields = []
        for col in columns :
            fields.append({"name" : col, "type" : "string"})

        return fields

    ##取查询的字段列表
    def getSqlColums(self, sqltext) :
        cursor = self.getConnection()
        # 用以获取列标题
        colSql = 'select * from ({}) _tmp limit 1'.format(sqltext)
        cursor.execute(colSql)
        # for col in cursor.description:
        #     print(cursor.description)
        columns = [col[0] for col in cursor.description]
        fields = []
        for col in columns :
            fields.append({"name" : col, "type" : "string"})

        return fields

    def queryForList(self, sql) :
        cursor = self.getConnection()
        cursor.execute(sql)
        tabMap = self.transCursor2Dict(cursor, type='list')
        return tabMap

    def queryForMap(self, sql) :
        cursor = self.getConnection()
        cursor.execute(sql)

        tabMap = self.transCursor2Dict(cursor, type='map')
        return tabMap

    def excuteSql(self, sql, val=None) :
        result = -1
        cursor = self.getConnection()
        if val is None :
            result = cursor.execute(sql)
        else :
            result = cursor.execute(sql, val)
        self.conn.commit()
        return result

    def insertData(self, data, tabname, tabfields, datafields=None) :
        sourceFields = []
        dataList = []
        if datafields == None :
            datafields = tabfields

        insertToken = ""

        for field in tabfields :
            if insertToken == '' :
                insertToken = "%s"
            else :
                insertToken = insertToken + ",%s"
        insertSql = "insert into " + tabname + "(" + ",".join(tabfields) + ")"

        for sourceRow in data :
            row = []
            for datafield in datafields :
                fieldVal = sourceRow.get(datafield.upper())
                row.append(fieldVal)
            dataList.append(row)
        # print(dataList,insertSql)

        try :
            cursor = self.getConnection()
            sql = insertSql + " values (" + insertToken + ")"
            print(sql)
            print(dataList)
            result = cursor.executemany(sql, dataList)
            self.conn.commit()
            print(result)
            return result

        except Exception as e :
            print("执行MySQL: %s 时出错：%s" % (sql, e))

        pass

    def deleteData(self, table, record, keyfield) :
        keyfields = keyfield.split(",")
        keyVals = []
        for field in keyfields :
            keyVals.append(str(record.get(field, "")))

        delsql = " delete from {table} where ({fields})=({keyval})"
        delsql = delsql.format(table=table, fields=",".join(keyfields), keyval=",".join(keyVals))
        print(delsql)
        try :
            cursor = self.getConnection()
            result = cursor.execute(delsql)
            self.conn.commit()
            print(result)
            return result
        except  Exception as e :
            print('Failed')
            print(e)
            self.conn.rollback()

    def updateData(self, tableName, record, keyfield) :
        # 1.计算主键数组
        keyfields = keyfield.split(",")
        # 2.根据住建拿数据
        keyfieldVals = []
        for field in keyfields :
            keyfieldVals.append(str(record.get(field, "")))
        sqltext = "select * from {table} where ({keyfields})=({keyfieldVals})";
        sqltext = sqltext.format(table=tableName, keyfields=",".join(keyfields), keyfieldVals=",".join(keyfieldVals))
        dbRecordVal = self.queryForMap(sqltext)
        if dbRecordVal == None :
            print("没有可更新的记录")
            return -1
        # 3.对当前数据的字段，如果不是住建，更现有值不一样就更新
        tabFieldsArray = self.getTabColums(tableName)
        updateFields = []
        updateVals = []
        updateFieldVals = []
        for field in tabFieldsArray :
            fieldName = field.get('name').upper()
            fieldType = 'integer'
            if type('www') == type(dbRecordVal.get(fieldName)) :
                fieldType = 'str'
            if type('www') == type(record.get(fieldName)) :
                fieldType = 'str'
            # print(fieldName,type(dbRecordVal.get(fieldName)),type(record.get(fieldName)))
            if fieldName in keyfields :
                pass
            elif record.get(fieldName, "") == dbRecordVal.get(fieldName, "") :
                pass
            else :
                updateFields.append(fieldName)
                updateVals.append(str(record.get(fieldName, "")))
                if fieldType == 'str' :
                    updateFieldVals.append(fieldName + " = '" + str(record.get(fieldName, "") + "'"))
                else :
                    updateFieldVals.append(fieldName + " = " + str(record.get(fieldName, "")))

        if len(updateFields) == 0 :
            return 0, "没有变化"

        # upsql=" update  {table} set ({updateFields})=({updateVals}) where ({keyfields}) =({keyfieldVals})"
        # upsql=upsql.format(
        #         table=tableName,
        #         updateFields=",".join(updateFields),
        #         updateVals=",".join(['36']),#updateVals
        #         keyfields=",".join(keyfields),
        #         keyfieldVals=",".join(keyfieldVals)
        #     )
        upsql = " update  {table} set {updateFieldVals} where ({keyfields}) =({keyfieldVals})"
        upsql = upsql.format(
            table=tableName,
            updateFieldVals=",".join(updateFieldVals),
            keyfields=",".join(keyfields),
            keyfieldVals=",".join(keyfieldVals)
        )
        print(upsql)
        try :
            cursor = self.getConnection()
            result = cursor.execute(upsql)
            self.conn.commit()
            return result, '成功更新'
        except  Exception as e :
            print('Failed')
            print(e)
            self.conn.rollback()
            return -1, "Error {0}".format(str(e))

    # 更新数据
    #  data = {
    # 'id': '20180606',
    # 'name': 'Lily',
    # 'age': 25
    # }
    def upSertData(self, table, data, keyfield) :
        # table = 'students'
        keyfields = ["imp_code"]
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        chksql = "select 1 as num from {table} where {keyfield}='{keyval}'".format(table=table, keyfield=keyfield, keyval=data.get(keyfield))
        insertSql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        updateTab = 'update  {table} set '.format(table=table)
        updateField = ','.join([" {key} = %s".format(key=key) for key in data])
        updateWhere = " where " + ','.join([" {key} = %s".format(key=key) for key in keyfields])
        updateSql = updateTab + updateField + updateWhere
        print(chksql)
        print(insertSql)
        print(updateSql)
        values = tuple(data.values())
        print(values)
        updataVals = list(values)
        for field in keyfields :
            updataVals.append(data.get(field))

        print(updataVals)
        try :
            cursor = self.getConnection()
            chekObj = self.queryForMap(chksql)
            if chekObj is None :
                print('start insertSql:' + insertSql)
                cursor.execute(insertSql, tuple(data.values()))
                print('insertSql Successful')
            else :
                print('start updateSql:' + updateSql)
                cursor.execute(updateSql, updataVals)
                print('updateSql Successful')
            self.conn.commit()
        except  Exception as e :
            print('Failed')
            print(e)
            self.conn.rollback()

    # db.shema.tabname的解析,返回db,shema.tabname
    def parserTabNames(self, tabObjName) :
        strList = tabObjName.split(".")
        dbname = strList[0]
        if len(strList) == 2 :
            tabName = strList[1]
        elif len(strList) > 2 :
            tabName = strList[1] + "." + strList[2]
        return dbname, tabName

    def regLog(self, params={}, user="", objname="", state="ok", operation="query", sqltext="", remark="") :
        sql = '''
            insert into dc_op_log(username, operation, method, params, ip, obj_type, obj_name, remark, audit_state)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s )
        '''
        if user == "" :
            user = params.get("applyUser")
        if objname == "" :
            objname = params.get("objname")
        val = (user, operation, "web call", sqltext, "", "tab", objname, remark, state)
        self.excuteSql(sql, val)

        # sql="SELECT id, username, operation, method, params, ip, obj_type, obj_name, eff_date, remark, audit_state FROM dc_op_log"

    # 去除字符串中的换行，空格
    def cleanSqltext(self, sqltext) :
        # newStr = " ".join((re.sub("\n", " ", sqltext)).split(" "))
        newStr = str.replace(sqltext, "\n", " ").replace("\r", " ").replace("    ", " ");
        newStr = str.replace(newStr, "  ", " ");
        return newStr

    def getTabInfo(self, fullName="", dbname="", schema="", tabName="", selfield="") :
        if fullName != '' :
            strList = fullName.split(".")
            dbname = strList[0]
            schema = strList[1]
            tabName = strList[2]
        if selfield == "" :
            selfield = "*"
        sql = "select {3} from meta_table_tpl where DB_NAME='{0}' and SCHEMA_NAME='{1}' and TAB_NAME='{2}'".format(
            dbname, schema, tabName, selfield)

        return self.queryForMap(sql)

    def sqlEncode(self, sql) :
        strList = [['&&34', "'"], ['&&37', "%"], ['&&60', "<"], ['&&62', ">"], ['&&61', "="]]
        newSql = sql
        for newstr, oldstr in strList :
            newSql = newSql.replace(oldstr, newstr)
        return newSql

    def sqlDecode(self, sql) :
        strList = [['&&34', "'"], ['&&37', "%"], ['&&60', "<"], ['&&62', ">"], ['&&61', "="]]
        for oldstr, newstr in strList :
            sql = sql.replace(oldstr, newstr)
        return sql

    def getUserInfo(self, username) :
        # 取用户的信息
        # 用户角色信息
        # 用户贵司团队信息
        # 团队客户访问数据的编码
        return {"name" : "username",
                "orgs" : [{"title" : "data center", "name" : "org1", "orgcode1" : 'hb', "orgcode2" : 'bj'}]}

    def getEntInfo(self, entId) :
        sql = "select * from sys_enterprise where ENT_ID='{0}'".format(entId)
        deptInfo = self.queryForMap(sql)
        return deptInfo
