#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午4:10
# @Author  : zhangds
# @File    : R.py
# @Software: PyCharm

class R(object) :
    """docstring for R"""

    def __init__(self) :
        self._data = {}
        self.result = True

    def remark(self, msg="") :
        self._data["remark"] = msg
        return self

    def code(self, code) :
        self._data["status"] = code
        return self

    def row(self, rownum) :
        self._data["rownum"] = rownum
        return self

    def data(self, data) :
        self._data["data"] = data
        return self

    def sqltext(self, sqltext="") :
        if sqltext == "" :
            return self._data.get("sqltext", "")
        else :
            self._data["sqltext"] = sqltext
            return self

    def get(self, key) :
        return self._data.get(key, "")

    def put(self, key, value) :
        self._data[key] = value
        return self

    @staticmethod
    def ok() :
        r = R()
        r._data["status"] = 'ok'
        return r

    @staticmethod
    def error() :
        r = R()
        r._data["status"] = 'error'
        r.result = False
        return r