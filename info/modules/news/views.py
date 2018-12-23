from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import db
from info.models import User, News, Comment
from info.modules.news import news_blu
from info.utils.common import user_login
from info.utils.response_code import RET
# 本文件用于写新闻详情页的视图函数

# 评论和回复功能
@news_blu.route("/news_comment", methods = ["POST"])
@user_login
def news_comment():
    """
    思路类似收藏
    1. 获取参数 news_id  comment_content  parent_id
    2. 校验参数
    3. 在数据库添加评论,
    4. 返回给前端进行渲染
    注意: 当前只是返回到ajax是局部刷新,当重新加载新闻页面评论会消失
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    params_dict = request.json
    news_id = params_dict.get("news_id")
    comment_content = params_dict.get("comment")
    # parent_id是为了获取父评论,为了回复,可以不存在
    parent_id = params_dict.get("parent_id")

    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 新建评论对象,将评论添加到数据库,并传到前端进行渲染json格式
    # parent_id是Comment模型类的字段,存在就说明是回复
    # 且评论是News模型类中的comments字段,
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    return jsonify(errno = RET.OK, errmsg = "评论成功", data = comment.to_dict())








# 收藏和取消收藏功能
@news_blu.route("/news_collect", methods = ["POST"])
@user_login
def news_collect():
    """
    1. 获取参数 用户,新闻,收藏事件
    2. 校验参数
    3. 查询新闻
    4. 收藏:在用户的关系中添加该条
    5. 取消收藏:删除该条新闻
    :return:
    """
    user = g.user   # 通过装饰器加载用户

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    # 如果用户存在,获取该条新闻id,和前端传过来的action
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 前端的action只两个值,
    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")


    # 终于校验完数据,所以以下才是核心业务逻辑:
    if action == "collect":   # 如果是收藏事件
        # 如果该条新闻已经收藏,就不添加了,没收藏才添加进去
        # 理解下这个collection_news是模型类User的中定义新闻和用户之间的多对多收藏的关系
        # if news not in user.collection_news:
        #     print(action)
        #     user.collection_news.append(news)
        #     print(news)
        #     print(user)
        #     print(type(user.collection_news))
        # 如果自动提交的配置不设置为True,不能提交到数据库
        # 必须设置SQLALCHEMY_COMMIT_ON_TEARDOWN = True,否则需要自己提交
        if news not in user.collection_news:
            user.collection_news.append(news)

    else :   # 否则就是取消收藏,== cancel_collect,已经验证过了,就这俩数据可能
        if news in user.collection_news:
            user.collection_news.remove(news)
            # print(action)

    return jsonify(errno = RET.OK, errmsg="OK")



# 新闻内容详情的显示
@news_blu.route("/<news_id>")
@user_login
def detail(news_id):
    """
    思路:
    1.获取参数:
    2.校验参数
    3.查找对应新闻
    4.返回给前端进行渲染
    注意:需要先检验用户是否是登陆状态,显示,并显示排行
    :param news_id: 获取到用户想要显示的new.id,显示对应的新闻,采用<news_id>接收相应变量
    :return:
    """
    # 下面这段获取登录信息的代码改为装饰器:
    # user_id = session.get("user_id")
    #
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    user = g.user    # 装饰器实现的g变量,可以不用装饰器,使用请求钩子


    # 显示排行
    news_list = News.query.order_by(News.clicks.desc()).limit(6).all()
    news_list_li = []
    for news_obj in news_list:
        news_list_li.append(news_obj.to_dict())


    # 渲染新闻详情内容:
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    if not news:
        abort(404)

    # 点击新闻,点击量加1,
    news.clicks += 1
    try :
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    # 收藏按钮的显示,之前是写死的,现在根据数据库查询结果,判断用户是否收藏,然后显示
    # 用户和新闻之间收藏的关系是多对多,存在收藏的表格:info_user_collection
    # 首先假设一个数据:is_collected 表示是否收藏
    is_collected = False     # 默认表示未收藏
    if user:   # 如果用户存在
        # user.collection_news 是调用模型类中的关系对象,属于
        if news in user.collection_news:  # 如果当前新闻在用户收藏的新闻列表中
            is_collected = True    # 就认为True ,表示收藏
    # 最后将表示是否收藏的is_collected传给前端,根据其取值,选择不同显示

    # user.collection_news是可迭代对象,在info_user_collection保存数据,就有值
    # 否则,对象不存在
    # for i in user.collection_news:
    #     print(i)   # i获取的是用户保存的所有新闻对象
    #     print(type(user.collection_news))
    # print(user.collection_news)


    # 评论完成后只是ajax局部刷新,再次刷新新闻页面不会显示评论,html没有改变
    # 需要在新闻界面的视图函数进行控制改变,并让评论数加1
    # 所以以下是新闻页面显示评论的后段代码:
    # 根据新闻显示它的评论,所以通过new_id查询评论:
    comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    # 得到的是评论对象组成的列表,遍历列表得到对象,转化成字典,添加到返回给前端的字典中进行渲染
    comment_dict_li = [comment.to_dict() for comment in comment_list]


    data = {
        "user_info": user.to_dict() if user else None,  # 用户信息
        "news_list_li": news_list_li ,                  # 排行
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comment_dict_li
    }
    # print(user)
    return render_template("news/detail.html", data = data)