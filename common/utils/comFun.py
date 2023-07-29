#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 下午6:54
# @Author  : zhangds
# @File    : comFun.py
# @Software: PyCharm
import re

"""
检查字符串是否为空
:param string: 需要检查的字符串
"""


def isNull(string) :
    # 判断字符串是否为空
    if string is None :
        return True
    elif string.strip() == '' :
        return True
    elif string.strip() == "null" :
        return True
    else :
        return False


"""
检查整个字符串是否包含中文
:param string: 需要检查的字符串
"""


def isChinese(string) :
    for ch in string :
        if u'\u4e00' <= ch <= u'\u9fff' :
            return True
    return False


"""
检查字符串是否大写
:param string: 需要检查的字符串
"""


def isupper(string) :
    if string is None or len(string) == 0 or len(string.strip()) == 0 :
        return True
    else :
        return string.isupper()


"""
检查字符串是否小写
:param string: 需要检查的字符串
"""


def islower(string) :
    if string is None or len(string) == 0 or len(string.strip()) == 0 :
        return True
    else :
        return string.islower()


"""
表名中一定只能用英文单词表示含义，尽量不使用拼音进行命名
:param string: 需要检查的字符串
"""


def englishWord(string) :
    return True


"""
表名中一定只能用英文单词表示含义，尽量不使用拼音进行命名
:param string: 需要检查的字符串
"""


def specialChar(string) :
    for ch in string :
        if ch in r'\/:^*?!"<>|[]' :
            return True
    return False


'''
SQL语句in条件校验
:param sql: sql
'''


def checkSQLIn(sql) :
    inwhere = ''
    if isNull(sql) : return False
    sql = sql.upper().strip()
    # "[\s\n]+in[\s\n]+"
    res = re.search("[\s\n]+IN[\s\n]*\(", sql)
    if res :
        tmp = sql[res.end() :]
        for char in tmp :
            if char != ')' :
                inwhere += char
            else :
                break
        incols = inwhere.split(",")
        if len(incols) >= 1000 :
            return False
        else :
            return True
    else :
        return True
