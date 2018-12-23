import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.wtf.csrf import generate_csrf
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

# 导入封装的字典
from config import config




#   注意：在配置类中设置等级：DevelopmentConfig.LOG_LEVEL  才能传入： config["development"].LOG_LEVEL
# 空的文件夹是不会被提交到git上的，别人在取开发代码的时候，一运行就报错


def set_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    # 需要创建一个logs文件在项目的根路径下
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



# １．类和字典
# 因为加载不同的配置类，可以调用不同使用环境，且类太多，不建议使用*,或者导入太多的类，
# 所以在配置文件中创建字典，使用字典的封装添加不同配置类，
# 以使用字典【key】调用不同配置的加载

# ２．工厂方法封装ａｐｐ的创建：
# 又因为每次加载配置时候得改变三个位置，我们可以选择将它变为一个形参来接收
# 所以将创建app放在函数中，最后返回app,就是工厂方法，调用这个函数，创建app，将配置作为参数
# 传到函数中，传入不同参数来创建不同配置的app

# ３．db的问题：
# 建立函数后，ｄｂ变成局部变量,在ｍａｎａｇｅ文件中导入时并不能导入db，所以我们
# 将db拿出来，将其变为全局变量：
# 但是此时ａｐｐ不能识别

# 抽取试图函数到蓝图，并且蓝图注册在返回app前，在本文件注册蓝图时，注意避免循环导入问题

db = SQLAlchemy()

# 先申明下redis_store传入None，但需要使用# type: StrictRedis告诉解释器是StrictRedis的对象
redis_store = None   # type: StrictRedis

def create_app(config_name):

    # 在调用ａｐｐ生成时调用set_log
    set_log(config_name)

    app = Flask(__name__)

    # 从类中添加配置
    app.config.from_object(config[config_name])
    # 2.集成SQLAlchemy
    # db = SQLAlchemy(app)
    # 为解决ｄｂ传入ａｐｐ的问题，借用原生ｄｂ传入ａｐｐ的方法：
    db.init_app(app)

    # 3.集成redis
    # 4.数据库迁移前夕，解决redis_store变量问题
    global redis_store
    redis_store = StrictRedis(host= config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT,decode_responses=True)

    # 4.CRSF,只帮我们进行校验工作,需要我们自己设置csrf_token值,设置cookie
    # 当我们使用CSRFProtect进行保护的时候，那么这个csrf_token值必须用CSRFProtect提供的
    # 在每次获取请求后,处理完后端逻辑进入csrf设csrf_token值保存在cookie,和前端的函数头里获取的
    # token值进行对比,而且每次post都会重新设置token值,get时候值不会变(也不一定)
    CSRFProtect(app)
    @app.after_request
    def set_cookie_csrf(response):
        # print(response.headers["Content-Type"])   # 检测response什么时候传进来
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token",csrf_token)
        # print(csrf_token)
        return response



    # 5.集成flask_session
    Session(app)

    # 注册蓝图,哪里注册哪里导入，避免循环导入
    from .modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    # 注册过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class,"indexClass")

    return app
