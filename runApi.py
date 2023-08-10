#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from common.utils.config import Config
import copy
import json
import os

app = Flask(import_name=__name__,
            static_url_path='/static',
            static_folder='static',
            template_folder='templates')
CORS(app, resources=r'/*')
app.config.from_pyfile('settings.py')

print(app.config["APP_NAME"])
app.config["APPS_CONFIG"] = Config("config.json")


def findModule(appId) :
    if appId is not None and len(appId) > 0 and app.config["APPS_CONFIG"].get('appModels') is not None :
        objs = [one if one is not None and isinstance(one, dict) and \
                       one.get('appCode') is not None and one.get('appCode') == appId \
                    else None for one in app.config["APPS_CONFIG"].get('appModels')]
        # objs.remove(None)
        if objs and len(objs) > 0 :
            for one in objs:
                if one and one.get("path")is not None :
                    return one
            #
            # _module = objs[0]
            # if _module is not None and _module.get("path") is not None :
            #     return _module
    return None


@app.route('/initApp')
def initApp() :
    app.config["APPS_CONFIG"] = Config("config.json")
    return jsonify({'message': r"应用刷新成功!", "status": "ok"})


@app.route('/<path:uri>', methods=["GET", "POST"])
def dynamicLoad(uri):
    if uri is not None:
        if "/" in uri:
            path = uri.split("/")
            appId = path[0] if len(path) > 0 else None
            apps = findModule(appId)
            if apps is not None and apps.get("path") is not None:
                relativePath = uri[len(appId)+1:]
                absolutePath = os.path.join(apps.get("path"), relativePath)
                # absolutePath包含文件名称
                if os.path.exists(absolutePath):
                    # Linux目录，windows待验证
                    allPaths = absolutePath.split(os.sep)
                    return send_from_directory(os.sep.join(allPaths[:-1]), allPaths[-1])
    return {}


# @app.errorhandler(404)
# def page_404(e):
#     return render_template('404.html'), 404


def loadBlueprint() :
    app.logger.info(app.config["APPS_CONFIG"].get("apiModes"))
    apiModels = app.config["APPS_CONFIG"].get("apiModes")

    for apiModel in apiModels :
        classObj = app.config["APPS_CONFIG"].getClass(apiModel.get("classPath"), apiModel.get("className"))
        app.register_blueprint(classObj)


loadBlueprint()

if __name__ == '__main__' :
    app.run(debug=True, port=5000, host='0.0.0.0')
    # app.run()
