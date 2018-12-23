from flask import Blueprint
"""
本文件夹为实现注册界面的业务逻辑
在本文件创建蓝图
"""
passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

from .views import *
