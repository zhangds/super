#!/usr/bin/env python
# coding=utf-8
import base64
from Crypto.Cipher import AES
import os
from hashlib import sha256
import uuid


class sha256Helper(object):
    salt = None

    def __init__(self, salt=None):
        if salt is None:
            self.salt = ''.join(str(uuid.uuid4()).split('-'))
        else:
            self.salt = salt

    def encrypt(self, content):
        salt_content = content.encode('utf-8') + self.salt.encode('utf-8')
        return sha256(salt_content).hexdigest(), self.salt

# def hashCode(content, salt):
#     salt_content = content.encode('utf-8') + salt.encode('utf-8')
#     hashed_password = sha256(salt_content).hexdigest()
#     return hashed_password , salt


class aseHelper(object):
    secretKey = "DTUo7Nzdc2+xux4e9kriXrIYXp6c2VOc"
    IV_LENGTH_BYTE = 12
    TAG_LENGTH_BIT = 128

    def __init__(self) :
        self.mode = AES.MODE_GCM
        self.iv = os.urandom(self.IV_LENGTH_BYTE)
        self.TAG_LENGTH_BYTE = int(self.TAG_LENGTH_BIT / 8)
        # self.log_util = LogUtil(level='info')

    def encrypt(self, text) :
        """
        AES 加密
        :param text: 原始字符串
        :return: 返回加密后的字符(string)
        """
        text = text.encode("utf-8")
        cipher = AES.new(bytes(self.secretKey, encoding="utf8"), self.mode, self.iv)
        params, tag = cipher.encrypt_and_digest(text)
        encrypted_text_byte = self.iv + params + tag
        encrypted_text = str(base64.b64encode(encrypted_text_byte), encoding='utf-8')
        return encrypted_text

    def decrypt(self, text) :
        """
        AES 解密
        :param text: 加密后的字符
        :return: 返回原始字符串(string)
        """
        try :
            decode_text = base64.b64decode(text)
            iv = decode_text[:self.IV_LENGTH_BYTE]
            enc = decode_text[self.IV_LENGTH_BYTE :-self.TAG_LENGTH_BYTE]
            cipher = AES.new(self.secretKey.encode("utf8"), self.mode, iv)
            plain_text_byte = cipher.decrypt(enc)
            plain_text_str = plain_text_byte.decode()
            # 解密结果如果为空，返回原文
            return plain_text_str if len(plain_text_str) > 0 else text
        except Exception as e:
            print("解密失败，返回原文!")
            return text


if __name__ == '__main__' :
    # str = aseHelper().encrypt('123456')
    # print(str)
    # print(aseHelper().decrypt(str))
    # str = 'FCw3mG4/D5gJYG7hF+HcZpWobkQLZaAV64XTC+i1WbKgMYeR0pPqOLBZxm4f71pNDsOaljU='
    # print(aseHelper().decrypt(str))

    pwd, slat = sha256Helper().encrypt('Super!369')
    _pwd , _slat = sha256Helper(slat).encrypt('Super!369')
    print(pwd, _pwd)
    print(pwd == _pwd)
