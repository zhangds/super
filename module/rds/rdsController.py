#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 下午6:14
# @Author  : zhangds
# @File    : rdsController.py
# @Software: PyCharm

import sys, os
import demjson
# import json

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from common.utils import Config, MetaDB


class rdsController(object) :
    def __init__(self, config=None):
        if config is not None:
            self.config = config
        # 元数据库初始化
        print(self.config, file=sys.stderr)
        if self.config is None:
            print("!!!!!!!!!无法配置文件", file=sys.stderr)
            return
        else:
            self.metadb = MetaDB.instance(self.config)

    def export2File(self, userId, tableName, columns):
        if userId != "" and tableName != "" and columns != "":
            pass
        pass
