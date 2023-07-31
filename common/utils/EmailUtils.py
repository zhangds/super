#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/30 下午10:58
# @Author  : zhangds
# @File    : EmailUtils.py
# @Software: PyCharm

import smtplib
from email.mime.text import MIMEText


class EmailUtils(object):
    def __init__(self, host, port: int, user, pwd, sender):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.sender = sender

    def sendEmail(self, receivers: list, title, content):
        # 信息拼接
        message = MIMEText(content, 'Plain', "utf-8")
        message['From'] = "{}".format(self.sender)
        message['To'] = ",".join(receivers)
        message['Subject'] = title

        try:
            smtpObj = smtplib.SMTP_SSL(self.host, self.port)  # 加密
            smtpObj.login(self.user, self.pwd)  # 登录
            smtpObj.sendmail(self.sender, receivers, message.as_string())  # 发送邮件
            print("mail has been send successfully")
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print(e)


if __name__ == '__main__':
    # SendMail()
    EmailUtils("smtp.qq.com", 465, "381717913@qq.com", "rqyvzufmdiwpcbai","381717913@qq.com")\
        .sendEmail(['zhang198058@hotmail.com', 'zhangds@faithindata.com.cn'],
                   "密码初始化", "Python Send Mail test!")