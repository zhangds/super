#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/30 上午11:13
# @Author  : zhangds
# @File    : httpUtils.py
# @Software: PyCharm

class HttpUtils(object):

    @staticmethod
    def getRequestValue(req, key, defaultVal=""):
        result = None
        if req and key :
            result = req.values.get(key, defaultVal)
            result = req.form.get(key) if result == defaultVal and req.form.get(key) else result
        return result
