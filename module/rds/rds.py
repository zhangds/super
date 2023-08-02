#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 下午5:31
# @Author  : zhangds
# @File    : rds.py
# @Software: PyCharm
from flask import Blueprint, request, render_template, current_app
from common.utils import HttpUtils
from .rdsController import rdsController

# 注册蓝图
rdsApi = Blueprint('rdsApi', __name__, url_prefix='/rds')


@rdsApi.route('/export2File', methods=["GET", "POST"])
def export2File():
    appConfig = current_app.app_context().app.config.get('APPS_CONFIG')
    # current_app._get_current_object().config.get('APPS_CONFIG')
    userId = HttpUtils.getRequestValue(request, "userId")
    tabId = HttpUtils.getRequestValue(request, "tabId")
    columns = HttpUtils.getRequestValue(request, "columns")
    if userId != "" and tabId != "":
        rdsController(appConfig).export2File(userId, tabId, columns)
    return {}