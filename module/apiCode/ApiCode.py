#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午4:46
# @Author  : zhangds
# @File    : ApiCode.py.py
# @Software: PyCharm
from flask import Blueprint, request, render_template, current_app
import json
import sys
import os
from common.utils import R, Config, MetaDB
from .ApiCodeControler import ApiCodeControler

# 注册蓝图
ApiCode = Blueprint('ApiCode', __name__, url_prefix='/dataService')


def getApiConfig(appConfig, appId, apiCode):
    content = None
    if appConfig is None or appConfig.get('appModels') is None or apiCode is None \
            or apiCode == "":
        raise Exception('应用配置列表、appId或apiCode不能为空!apiCode:%s' % apiCode if apiCode else '')
    elif (appId is None or appId == "") and apiCode is not None and apiCode != "":
        pass
    else:
        appModelList = appConfig.get('appModels')
        if appId != "common":
            _runConfig = findModule(appModelList, appId)
            realPath = _runConfig.get("path") if _runConfig is not None and _runConfig.get("path") else None
            realPath = os.path.join(realPath, "apiCode") if realPath else None
            files = os.listdir(realPath) if realPath else None
            fileName = [filename if files and appId and isinstance(apiCode, str) \
                                    and filename.lower().startswith(apiCode.lower()+".") else None \
                        for filename in files]
            fileName = list(set(fileName))
            if fileName and (None in fileName):
                fileName.remove(None)
            if fileName and len(fileName) > 0:
                # 优先去加载apiCode文件，默认去第一个
                try :
                    _file = open(os.path.join(realPath, fileName[0]), encoding='utf-8')
                    content = _file.read()
                    content = content.replace("\n", "") if content and len(content) >0 else ""
                    _file.close()
                except Exception as e:
                    raise Exception("读取文件失败!filePath:%s--msg:%s" % (os.path.join(realPath, fileName[0]), e.args[0]))
    try :
        if content is None:
            info = ApiCodeControler("", appConfig).getApiInfo(apiCode)
            if info is None:
                raise Exception('读取数据库配置未发现数据!apiCode:%s' % apiCode)
            content = json.dumps(info) if info and isinstance(info, dict) else ""
    except Exception as e:
        raise Exception("读取数据库配置出错!%s" % e.args[0])
    return content


@ApiCode.route('/getApi', methods=["POST", "GET"], strict_slashes=False)
def getApi():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    # appModelList = app.config.get('APPS_CONFIG').get('appModels')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    try:
        content = getApiConfig(appConfig, appId, apiCode)
        result = {"status": "ok", "data": content}
    except Exception as e:
        result = {"status": "error", "message": e.args[0]}
    return result


@ApiCode.route('/saveApi', methods=["POST", "GET"], strict_slashes=False)
def saveApi():
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    apiJson = getRequestValue(request, "apiJson")
    if appId and appId != "" and apiCode and apiCode != "" and apiJson and apiJson !="":
        _runConfig = findModule(appConfig.get('appModels'), appId)
        realPath = _runConfig.get("path") if _runConfig is not None and _runConfig.get("path") else None
        realPath = os.path.join(realPath, "apiCode") if realPath else None
        if apiJson:
            with open(os.path.join(realPath, apiCode + ".json"), 'w') as f:
                f.write(apiJson)
                # json.dump(apiJson, f)
    return {"status": "ok"}


@ApiCode.route('/sqlQuery', methods=["POST", "GET"], strict_slashes=False)
def sqlQuery():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    initSql = getRequestValue(request, "initSql")
    if initSql and initSql != "":
        limit = request.values.get("limit", 50)
        start = request.values.get("start", 0)
        print("** start initSql=", initSql, ",start=", start, ",limit=", limit, file=sys.stderr)
        apiCodeControler = ApiCodeControler("", appConfig)
        result = apiCodeControler.querySqlData(initSql, start, limit)
    return result


#全sql和全command
@ApiCode.route('/apiQuery', methods=["POST", "GET"], strict_slashes=False)
def apiQuery():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    apiInfo = None
    try:
        content = getApiConfig(appConfig, appId, apiCode)
        apiInfo = json.loads(content)
        print(apiInfo)

        params = {}
        for key in request.values :
            if key == 'params':
                params = request.values.get("params", {})
            elif key and key != "":
                params[key] = getRequestValue(request, key)
        limit = getRequestValue(request, "limit")
        limit = limit if limit != "" else 50
        start = getRequestValue(request, "start")
        start = start if start != "" else 0
        para_order = getRequestValue(request, "para_order")

        print("** start apiCode=", apiCode, ",start=", start, ",limit=", limit, ",params=", params, ",para_order=", para_order, file=sys.stderr)
        apiCodeControler = ApiCodeControler("", appConfig)
        result = apiCodeControler.queryApiData(apiCode, start, limit, params, para_order, apiInfo)
    except Exception as e:
        result = {"status": "error", "message": e.args[0]}
    return result


@ApiCode.route('/apiUpdate', methods=["POST", "GET"], strict_slashes=False)
def apiUpdate():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    apiInfo = None
    try :
        content = getApiConfig(appConfig, appId, apiCode)
        apiInfo = json.loads(content)

        recordStr = getRequestValue(request, "records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", appConfig)
        result = apiCodeControler.updateApiData(apiCode, records, apiInfo)

    except Exception as e :
        result = {"status" : "error", "message" : e.args[0]}
    return result


@ApiCode.route('/apiInsert', methods=["POST", "GET"], strict_slashes=False)
def apiInsert():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    apiInfo = None
    try :
        content = getApiConfig(appConfig, appId, apiCode)
        apiInfo = json.loads(content)

        recordStr = getRequestValue(request, "records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", appConfig)
        result = apiCodeControler.insertApiData(apiCode, records, apiInfo)

    except Exception as e :
        result = {"status" : "error", "message" : e.args[0]}
    return result


@ApiCode.route('/apiDelete', methods=["POST", "GET"], strict_slashes=False)
def apiDelete():
    result = {}
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    appId = getRequestValue(request, "appId")
    apiCode = getRequestValue(request, "apiCode")
    apiInfo = None
    try :
        content = getApiConfig(appConfig, appId, apiCode)
        apiInfo = json.loads(content)

        recordStr = getRequestValue(request, "records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", appConfig)
        result = apiCodeControler.deleteApiData(apiCode, records, apiInfo)

    except Exception as e :
        result = {"status": "error", "message": e.args[0]}
    return result


@ApiCode.route('/dyLoad', methods=["POST", "GET"], strict_slashes=False)
def dyLoad():
    return {}


@ApiCode.route('/<path:code>', methods=["POST", "GET"], strict_slashes=False)
def apicodeNew(code) :
    result = {}
    _path = code.split("/") if "/" in code else [code]
    # print(_path)
    appId = _path[0] if len(_path) > 0 else None
    appId = request.values.get("appId") if appId is None and request.values.get("appId") else appId

    apiCode = _path[1] if len(_path) > 1 else None
    apiCode = getRequestValue(request, "apiCode") if apiCode is None else apiCode
    initSql = getRequestValue(request, "initSql")
    command = getRequestValue(request, "command")
    if (apiCode == "" or apiCode is None) and initSql == "" :
        result = {"status" : "error", "message" : "没有apiCode或initSql"}
    elif initSql and initSql != "" :
        print(initSql)
    else :
        app = current_app._get_current_object()
        # sys.path[0]
        realPath = None

        if appId != "common" :
            _runConfig = findModule(app.config.get('APPS_CONFIG').get('appModels'), appId)
            realPath = _runConfig.get("path") if _runConfig is not None and _runConfig.get("path") else None
            realPath = os.path.join(realPath, "apiCode") if realPath else None
        # print(realPath)
        files = os.listdir(realPath) if realPath else None
        fileName = [filename if files and appId and isinstance(apiCode, str) \
                                and filename.lower().startswith(apiCode.lower()) else None \
                    for filename in files]
        if fileName and None in fileName:
            fileName.remove(None)
        if fileName and len(fileName) > 0:
            # 优先去加载apiCode文件，默认去第一个
            pass
        else:
            # 去数据库加载
            pass


    return result


def getRequestValue(req, key) :
    result = None
    if req and key :
        result = req.values.get(key, "")
        result = req.form.get(key) if result == "" and req.form.get(key) else result
    return result


# TODO 有机会和runApi里的合并
def findModule(configs, appId) :
    if configs is not None and appId is not None and len(appId) > 0 :
        objs = [one if one is not None and isinstance(one, dict) and \
                       one.get('appCode') is not None and one.get('appCode') == appId \
                    else None for one in configs]
        objs.remove(None)
        if objs is not None and len(objs) == 1 :
            _module = objs[0]
            if _module is not None and _module.get("path") is not None :
                return _module
    return None


@ApiCode.route('/', methods=["POST", "GET"], strict_slashes=False)
def apicode() :
    # print('apiCode**************************', file=sys.stderr)
    # print (request.is_json, file=sys.stderr)
    app = current_app._get_current_object()
    # print(app.config['config'], file=sys.stderr)

    # print("***get_json*************", request.get_json(), file=sys.stderr)
    # print("***get_data*************", request.get_data(as_text=True), file=sys.stderr)
    # print("***request values*************", request.values, file=sys.stderr)

    # print('apiCode------',request.values.get("apiCode"), file=sys.stderr)
    # print('command------',request.values.get("command"), file=sys.stderr)
    # print('request.args------',request.args, file=sys.stderr)
    # print('request.form',type(request.form),request.form, file=sys.stderr)
    #
    # command=request.form.get("command")
    # records=request.form.get("records")
    # print("paramMapStr",type(paramMapStr),paramMapStr, file=sys.stderr)

    # print("paramMap",type(paramMap),paramMap, file=sys.stderr)

    apiCode = request.args.get("apiCode") if request.args.get("apiCode") else request.form.get("apiCode")
    initSql = request.values.get("initSql", "")
    if (apiCode == "" or apiCode is None) and initSql == "" :
        return {"status" : "error", "message" : "没有apiCode或sql"}

    command = request.values.get("command") if request.values.get("command") else request.args.get("command")
    command = command if command is not None else ""
    if command == "queryBySql" :
        limit = request.values.get("limit", 50)
        start = request.values.get("start", 0)
        print("** start initSql=", initSql, ",start=", start, ",limit=", limit, file=sys.stderr)
        apiCodeControler = ApiCodeControler("", app.config['config'])
        result = apiCodeControler.querySqlData(initSql, start, limit)
        pass
    elif command == "init" or command == "query" :
        # paramMapStr=request.get_data(as_text=True)
        # paramMap=json.loads(paramMapStr)
        params = {}
        for key in request.values :
            if key == 'apiCode' :
                apiCode = request.values.get("apiCode")
            elif key == 'command' :
                command = request.values.get("command")
            elif key == 'limit' :
                limit = request.values.get("limit", 50)
            elif key == 'start' :
                start = request.values.get("start", 0)
            elif key == 'para_order' :
                para_order = request.values.get("para_order", "")
            elif key == 'params' :
                params = request.values.get("params", {})
            elif key is not None or key != "" :
                params[key] = request.values.get(key, "")
            else :
                pass
        limit = request.values.get("limit", 50)
        start = request.values.get("start", 0)
        para_order = request.values.get("para_order", "")
        print("** start apiCode=", apiCode, ",start=", start, ",limit=", limit, ",params=", params, ",para_order=", para_order, file=sys.stderr)
        apiCodeControler = ApiCodeControler("", app.config['config'])
        result = apiCodeControler.queryApiData(apiCode, start, limit, params, para_order)

    elif command == "insert" :
        recordStr = request.form.get("records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",command=", command, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", app.config['config'])
        result = apiCodeControler.insertApiData(apiCode, records)
    elif command == "delete" :
        recordStr = request.form.get("records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",command=", command, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", app.config['config'])
        result = apiCodeControler.deleteApiData(apiCode, records)
    elif command == "update" :
        recordStr = request.form.get("records")
        records = json.loads(recordStr)
        print("**apiCode=", apiCode, ",command=", command, ",records=", records, file=sys.stderr)

        apiCodeControler = ApiCodeControler("", app.config['config'])
        result = apiCodeControler.updateApiData(apiCode, records)
    else :
        result = {"staus" : "error", "message" : "未知命令command:%s" % command}

    return result
    # return getMenu()


if __name__ == '__main__' :
    pass
