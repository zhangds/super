#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/30 上午11:04
# @Author  : zhangds
# @File    : sysUser.py
# @Software: PyCharm

from flask import Blueprint, request, render_template, current_app
from common.utils import HttpUtils
from .sysUserController import sysUserController
import json
import sys
import os
from common.utils import R, Config, MetaDB

# 注册蓝图
SysUser = Blueprint('SysUser', __name__, url_prefix='/user')


@SysUser.route('/login', methods=["GET", "POST"])
def login():
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    userId = HttpUtils.getRequestValue(request, "userId")
    password = HttpUtils.getRequestValue(request, "password")
    if userId != "" and password != "":
        return sysUserController(appConfig).checkUser(userId, password)
    return


@SysUser.route('/add', methods=["GET", "POST"])
def addUser():
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    """添加用户"""
    userId = HttpUtils.getRequestValue(request, "userId")
    cnname = HttpUtils.getRequestValue(request, "cnname")
    password = HttpUtils.getRequestValue(request, "password")
    phone = HttpUtils.getRequestValue(request, "phone")
    mail = HttpUtils.getRequestValue(request, "mail")

    if userId != "" and cnname != "" and password != "" and \
        phone != "" and mail != "":
        return sysUserController(appConfig).addUser(userId, cnname,
                                                    password, phone, mail)
    return {}


@SysUser.route('/forget', methods=["GET", "POST"])
def forgetUser():
    """遗忘用户密码"""
    config = current_app._get_current_object().config
    appConfig = config.get('APPS_CONFIG')
    userId = HttpUtils.getRequestValue(request, "userId")
    if userId != "" :
        return sysUserController(appConfig).forget(userId, config, request.host_url)
    return {}


@SysUser.route('/info', methods=["GET", "POST"])
def getUser():
    appConfig = current_app._get_current_object().config.get('APPS_CONFIG')
    """获取用户信息"""
    userId = HttpUtils.getRequestValue(request, "userId")
    if userId != "":
        return sysUserController(appConfig).userInfo(userId)
    return {}