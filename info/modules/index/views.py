from flask import current_app, jsonify
from flask import render_template
from flask import request
from flask import session

from info.models import User, News, Category
from info.modules.index import index_blu

# 抽取的视图函数用蓝图写，在init文件中初始化，
# 本文件用蓝图来写不同的视图函数主要用于index页面


# 首页新闻数据的显示
from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    1.获取参数,接口文档中定义的:cid(分类),page(页码),per_page(每页显示新闻条数)
    2.校验参数
    3.查询新闻及其分类
    4.按照时间排序并分页显示
    :return:
    """
    # 1.获取参数:
    # 使用request.args.get(a,b),a:参数的key. b:当没传时候,获取不到,则默认b
    # 以下这些参数都写在接口文档
    cid = request.args.get("cid", "1")   # 获取cid,获取不到默认取值1
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 校验下数据,万一传过来不是数字,是个a呀什么的
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron = RET.PARAMERR,errmsg="数据错误")

    # 查询新闻及其分类,并且分页:
    """
    如果是第一类,证明是所有新闻,按照时间降序
    if cid == 1:
    当分类是2-6时,在查询的filter()中添加过滤条件:News.category_id == cid
        paginate = News.query.filter().order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
         获取的paginate 是查询集,对象, 其查询方法在SQLAlchemy中
    """


    # 上述多行注释的查询过程可以使用列表拆包的思想 *list的形式传入过滤条件
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)     # 当cid != 1时添加到列表中
    paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

    news_lists = paginate.items     # 获取所有新闻,是个新闻对象的列表
    current_page = paginate.page    # 获取当前页
    all_pages = paginate.pages      # 获取总页数

    # 像passport/views.py中的方法一样,需要将news_lists中的对象转化为字典,
    # 添加到新的列表中,在自定义data{}中以键值对形式传给前端渲染
    news_dict_li = [news.to_dict() for news in news_lists]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": all_pages
    }

    return jsonify(errno = RET.OK, errmsg = "获取新闻成功", data = data)

# 主页面
@index_blu.route("/")
def index():
    """
    1.在用户登录或注册后,要显示用户登陆状态:
    在用户登录和注册时,保存了session("user_id")用来保存登录状态
    所以在进入首页中,能获取到user_id就能说明你是登录的
    利用查询到的数据进行渲染,返回数据到首页
    :return:
    """
    user_id = session.get("user_id")
    # 为避免假的user_id,不能只进行if not user_id:这样的判断
    # 需要假设一个user = None对象为后续查询做准备
    user = None
    # 如果user_id存在,去数据库查询:
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)


    """
    2.渲染新闻点击排行的界面
        1. 查询所有新闻
        2. 排序,按照点击量降序
        3. 取出前6条进行渲染
    """
    # 取出前六条新闻,是
    news_list = News.query.order_by(News.clicks.desc()).limit(6).all()
    # 此时的news_list如下所示:是新闻对象组成的列表,后边数字是id
    # news_list = [<News 1086>, <News 134>, <News 297>, <News 86>, <News 166>, <News 208>]
    # 为了渲染,需要将对象转化为每条新闻的字典(to_dict方法),放在列表中,
    # 传给前端,前端想获取什么就通过字典获取什么
    # 定义一个新列表,用于保存转化的字典传给前端
    news_list_li = []
    for news_obj in news_list:
        news_list_li.append(news_obj.to_dict())


    """
    3.新闻分类显示:
    之前的前端代码中分类是写死的,现在需要将报存在数据库中的分类拿出来进行渲染
    同样以字典形式放在data中,以键值对形式传给前端进行渲染
    """
    category_list = Category.query.all()
    # 同上述排序一样,获取的对象是列表,其中是每个分类的对象,
    # category_list = [<Category 1>, <Category 2>, <Category 3>, <Category 4>, <Category 5>, <Category 6>]
    # 需要创建一个新的列表,将对象新闻类别对象化转化为字典,同样保存在data中传给前端
    category_list_li = [categorys.to_dict() for categorys in category_list]


    # 判断user是否存在,存在则保存到自定义一个渲染前端的变量
    # 渲染前端时,将字典传进去,key:user_info.值为user对象调用模型类中to_dict方法,保存的字典
    # 这样在模板文件中,通过出入的data.user_info.key(模型类中to_dict保存的键值)获取各种想要的值
    # 详情见'news/index.html'中,配合理解
    # 排序的新闻列表:将保存新闻字典的列表放在之前的data中,传给前端:
    data = {
        "user_info": user.to_dict() if user else None ,  # if判断三元运算符
        "news_list_li": news_list_li,
        "category_list_li": category_list_li
    }

    return render_template('news/index.html', data = data)


# 请求图标：浏览器会自动请求GET/favicon.ico，需要我们去写接口:
@index_blu.route("/favicon.ico")
def favicon():
    """
    返回favicon.ico，且状态码200
    不能使用重定向,重定向状态码是302，
    :return:图标
    """
    return current_app.send_static_file("news/favicon.ico")

