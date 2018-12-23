import logging
from redis import StrictRedis

# 工作中需要各种配置，各种配置存在不同，也有相同配置，所以使用继承
# 因为不同的使用环境需要加载不同的配置，所以在本文件中设置不同配置，让app加载，
# 比如开发环境的配置，测试环境的配置/应用时候的配置


# 1.类中加载配置

class Config(object):

    SECRET_KEY = "MDxZKFpRE5K6VoV9qIHMquUTwWTbifVkkJ58vuzE/l4GMQgkWiHVS0iCDPCTa/putMTkx2+5jEG1KBjV6yTvNw=="

    # 开发环境用debug，应用时不用
    # DEBUG  = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 如果为True，当我们对一个已经查询出来的对象进行修改操作的话，不需要使用db.session.commit()
    # 但是这个自动提交是在视图函数return后才提交,如果return前用过或从数据库查询取出
    # 要提交的数据,则查询不到,所以谨慎使用
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    # 设置专门储存session的对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置session是否加密
    SESSION_USE_SIGNER = True
    # 设置session过期时间，True:关闭浏览器就消失，False：默认31天，
    SESSION_PERMANENT = False
    # 设置session保存时间2天
    PERMANENT_SESSION_LIFETIME = 86400 * 2


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "pruduction": ProductionConfig,
    "testing": TestingConfig
}