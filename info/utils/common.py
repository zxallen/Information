# 本文件用来写一些通用,或公用的工具,例如过滤器,装饰器等

# 点击排行前三个样式的过滤器
import functools
from flask import current_app
from flask import g
from flask import session

from info.models import User


def do_index_class(index):
    """
    根据index的取值,在index.html文件中,98行左右新闻点击排行
    前三条的新闻确定span标签的类属性对应的值,first,second,third

    注意:在__init__文件中注册,才能在前端文件使用
    :return:
    """
    if index == 1:
        return "first"

    elif index == 2:
        return "second"

    elif index == 3:
        return "third"

    else:
        return ""


# 显示登录状态的装饰器
# 注意:在加装饰器时,被装饰函数名字会变成内函数名,
#  @functools.wraps(f)的作用是不改变被装饰函数的名字
# 装饰器中使用g变量保存数据
def user_login(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # g变量:是应用上下文全局变量,在一次请求中保存临时变量,
        # 这里是将查询到的user保存到g变量中,在装饰器修饰视图函数时取出user
        g.user = user
        return f(*args, **kwargs)
    return wrapper