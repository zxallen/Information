# Flask Information项目说明文档

> Powered by 賈誌翔

#登录注册

```
##1 图片验证码生成(/passport/image_code)
用户点击 注册按钮,触发js中的函数生成一个UUID并通过ajax请求到服务器端,服务器接收到来自用户的请求,
判断是否携带参数,有参数生成一张图片验证码并以用户传递过来的参数为key,图片验证码为value储存到redis中 并设置过期时间60S.
```

```
##2 短信发送(/passport/sms_code)
用户填写完注册框中内容 点击获取验证码,前端做一次数据完整性的校验,通过ajax发送给后台,
后台检验数据完整性,如果数据完整,检验验证码是否和redis中储存的数据一致,
所有数据校验通过生成一个6位数字的验证码并调用第三方短信验证码平台发送,需要三个参数(手机号、短信内容(验证码)、过期时间), 
第三方平台接收到这些数据会有一个返回值-1/0 0表示发送成功,-1表示发送失败,
根据返回值判断短信是否发送成攻,如果发送成攻将手机号和验证码内容以key-value存入redis并设置过期时间,否则返回相应的错误信息.
```


```
##3 注册(/passport/register)
用户填写完验证码之后 点击注册
前端通过ajax发送 手机号 验证码 密码到后端
后端检验数据的完整性 
通过获取到的手机号取出redis中存入的验证码校验是否和前端传过来的是否一致,如果取不到值返回验证码过期,如果取出的值于前端传送过来的值不一致 
返回错误 验证码不正确.所有验证通过之后 将数据存入数据库,存入数据库时做异常处理以及事务处理.
```


```
##4 登录(/passport/login)
用户点击登录按钮 输入相应的用户名和密码之后 通过ajax发送到服务器,服务器接收到值之后做一致性校验,
如果帐号不存在返回'用户不存在,请先注册',如果密码未能通过校验返回'用户名或者密码错误',登录成功之后将登录信息保存在session中
```

#页面展示

```
##1 主页(/)
用户进入网站默认路由是index(首页)页面
判断用户是否已经登录
用户未登录:页面右上角显示登录按钮
用户已登录:页面右上角显示个人头像名称之类
点击首页时默认展示最新数据 查询数据库 
点击不同新闻分类时触发ajax请求 不同分类的新闻有不同的class_id(cid)ajax发送请求携带cid后端接收到ajax请求 
通过cid查询对应的新闻类别返回给前端展示返回数据包括:数据总页数、当前页数、当前页面的数据
页面往下拉的时候也会触发ajax请求往下请求更多数据(当前页面小于总页面数) 当前页面等于总页面数时不再显示更多数据
```

```
##2 详情页(/<int:news_id>)
点击首页展示的新闻进入详情页面 向后端发送get请求 携带新闻的id
后端接收到前端的请求 通过新闻id查询出新闻详情 新闻的评论 点击次数 评论的点赞数量 并判断用户是否登录 
如果用户登录则查询这个 新闻用户是否收藏 点赞 
根据查询的结果返回给前端
```

```
##3 评论(/news_comment)
点击评论时判断用户是否登录,如果用户未登录则弹出登录框
用户已登 评论提交时 通过js修改前端评论展示并将提交的评论展示到评论列表最上面,同时通过ajax把评论内容 
新闻id 评论人的id 传送到后端 后端接受到这些参数 先校验参数的完整性 如果缺失任何一个参数 返回参数错误, 
若参数都有继续校验数据库是否有这存在这篇新闻是否存在 
如果不存在(管理员后台删除了请求时发生了未知的错误导致新闻id出错)返回错误'未查询到新闻'
在确认没有参数错误 没有数据错误之后将评论内容 评论的新闻id 评论人的id存入数据库中(注意所有数据库修改操作时都要加上事务处理)
```


```
##4 收藏(/news_collect)
前端发送请求包括 新闻id(news_id) 请求行为(action)
判断用户是否登录 没有登录弹出登录框
判断参数是否完整 否则返回错误'参数错误'
参数完整性校验通过后 校验数据的有效性 去数据库查找新闻是否存在
判断新闻页面是否存在 否则返回错误'未查询到新闻数据'
所有参数校验通过之后 
根据action判断用户是否收藏新闻还是取消收藏
根据判断的结果在数据库中做相应的添加和移除操作
操作完成之后返回消息'操作成功'.
数据库修改操作时都要加上事务处理
```


```
##5 评论点赞(/comment_like)
前端发送请求包括 评论id(comment_id) 请求行为(action)
判断用户是否登录 没有登录弹出登录框
判断参数是否完整 否则返回错误'参数错误'
参数完整性校验通过后 校验数据的有效性 去数据库查找评论是否存在
如果不存在 返回错误'评论不存在'
数据完整性和有效性都验证通过之后 在评论点赞表中根据用户id和评论id查找出数据
根据action判断用户的请求行为是点赞还是取消点赞
如果是点赞则在评论点赞表中删除这条记录 同时把该评论的点赞数-1
否则在评论点赞表中添加这条数据 同时把该评论的点赞数+1
数据库修改操作时都要加上事务处理
```






```
##6 关注用户(/followed_user)
前端发送请求 携带参数 关注的用户id(user_id) 请求行为(action)
判断用户是否登录 未登录弹出登录框
判断数据完整性 否则返回错误'参数错误'
根据关注的用户id(user_id)去用户表中查找是否存在这个用户
如果查找不到该用户返回错误'未查询到用户信息'
根据action判断是关注用户还是取消关注
如果是关注用户在info_user_fans中添加当前用户id为follower_id user_id为followed_id
否则在info_user_fans中移除
```

```
#3 个人中心
## 用户资料(/user/info)
用户资料展示用户填写的基本资料 个性签名 昵称 性别
根据请求方式判断用户行为
如果请求方式为GET 展示用户的现有资料
如果请求方式为POST 根据传输到后端的值改变用户资料
当请求方式为POST时 服务端收到用户传输的数据首先做数据完整性校验
根据获取到的登录用户ID去用户表中修改信息
```

```
## 头像修改(/user/pic_info )
用户点击修改头像 服务端接收到用户请求根据用户的请求方式GET,POST判断用户是查看头像还是修改头像,请求方式为GET时是查看头像 返回用户头像模板和头像展示给用户,
请求方式为POST时根据用户传输过来的数据提取到用户头像并上传到七牛云上 将传送到云上的URL保存到用户表中并将更新之后的数据返回给用户展示
```

```
## 关注列表(/user/user_follow)
用户点击我的关注之后进入关注页面 服务端收到用户请求,获取到当前用户的登录信息 查询用户的关注列表 以每页四个做分页 将总页面数 
当前页面数据以及当前所在页面返回给用户显示
```

```
## 密码修改(/user/pass_info)
用户点击密码修改 服务端接收到用户的请求根据用户请求方式GET,POST 判断用户是请求更改密码的页面(GET)还是发生更改密码行为(POST)
GET请求返回修改密码界面 
POST请求 携带参数旧密码 新密码 
前端需要填写两次密码同时会校验两次密码是否一致如果不一致弹出提示'两次密码输入不一致'前端校验通过 后将新密码和旧密码传送到服务端,服务端收到POST请求 
先校验数据的是否完整,数据校验通过之后 
根据当前登录用户的id去用户表中查询当前登录的用户密码,通过check_password函数(创建用户表时写的方法)对比前端传输过来的旧密码和存在用户表中的密码是否相同,
如果密码不同返回错误"原密码错误",
如果验证通过 将新密码存入用户表中,返回消息 保存成功
```

```
## 我的收藏(/user/collection)
用户点击我的关注之后进入关注页面 服务端收到用户请求,获取到当前用户的登录信息 查询用户的收藏列表 
以每页十个收藏的新闻做分页处理 处理完成之后将 总页面数 当前页面数 当前页面收藏的新闻 返回给前端展示
```

```
## 新闻列表(/user/news_list)
用户点击新闻列表获取自己投稿的新闻 以及状态
服务端接收用户请求 根据seesion获取到当前登录用户的信息
通过获取到的信息去新闻表中根据用户id查询用户发布的新闻以每页十条新闻做分页处理
处理完成之后将 总页面数 当前页面数 当前页面新闻 返回给前端展示 前端接收到服务端传送过来的数据 根据数据中 
当前页面中的新闻状态(0,1,其余数值)显示新闻的相应状态(已通过,审核中,未通过)
```


```
## 新闻发布(/user/news_release)
用户点击新闻发布进入新闻发布
服务端接收请求 根据请求方式不同执行不同的操作(GET)请求新闻发布模板,(POST)传送编辑好的新闻到后端
用户点击新闻发布时对后端发送一个GET请求 服务端接收到GET请求 到数据库中查询新闻分类信息和新闻发布模板一起返回给前端
用户根据新闻发布页面填写内容,点击"发布"将内容以Ajax形式POST方式发送到后端,在Ajax发送之前JS在前端做一次数据完整性校验,校验不通过弹出"参数有误",
前端校验通过之后数据发送到后端,后端接收到数据 做数据完整性校验 校验不通过返回错误"参数有误", 校验通过后 将数据写入新闻表中
```

``` python
news.title = title
news.digest = digest
news.source = source
news.content = content
news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
news.category_id = category_id
news.user_id = g.user.id
```


```
# 后台管理
## 登录(admin/login)
用户GET请求后台登录模板时
判断当前是否有登录，如果有登录直接重定向到管理员后台主页
在session中获取user_id,is_admin两个字段如果能获取到重定向到admin主页
获取不到 返回登录页面
用户发送POST请求时(username, password)
先做数据完整性校验
到用户表中查询是否有这个用户 并且is_admin字段为True
如果没有返回错误"未查询大炮用户信息"
登录完成之后将登录信息保存到seeion中并跳转到admin主页面
```


```
## 用户管理
### 用户统计(/admin/user_count)
管理员点击 用户统计 发送请求
后台收到请求
查询User表中所有用户total_count
根据time.localtime() 获取到当前月份和年份并拼接到当前月份第一天
python 
t = time.localtime()
begin_mon_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
#将字符串转成datetime对象
begin_mon_date = datetime.strptime(begin_mon_date_str, "%Y-%m-%d")
通过begin_mon_date去数据库中查询创建时间在这之后的用户的总数mon_count
通过循环 获取到每一天中新增加的用用户active_count
将获取到的数据和和模板一起返回给前端渲染
### 用户列表(/admin/user_list )
查询用户表将所有非管理员用户查询出来之后以每页十个做分页处理
将查询出的数据(用户信息, 总页面, 当前页面)返回给前端
```

```
## 新闻管理
### 新闻审核(/admin/news_review)
查询用户表将所有待审核新闻,查询出来之后以每页十个做分页处理
将查询出的数据(待审核新闻, 总页面, 当前页面)返回给前端
### 新闻分类管理(/admin/news_type)
根据用户请求方式不同做不同处理
GET:获取到所有分类
POST:参数(id(分类ID),name(类名))如果有id则根据name对已存在的id查询出数据 对数据中的name修改
如果没有id 将name存入新闻分类表中
### 新闻板式编辑(/admin/news_edit)
用户点击新闻板式编辑,服务端接收到请求
请求方式为GET时
如果请求链接后没有携带参数则
查询到所有的新闻以发布时间排序 返回给用户展示,用户通过关键词搜索在链接后面添加
如果请求链接携带参数为keyword
将关键词添加到查询条件中,如果没有查询所有,将查询出来的结果以每页10条分页处理,将处理好的数据返回给用户(总页面,当前页面,当前页面数据)
如果请求参数为news_id
根据news_id后面的id查询出新闻的内容返回给前端
请求方式为POST时
根据POST过来的数据和news_id和内容对新闻进行跟新
```

***

# 一、项目分析

```
（一）新经资讯

1、新闻展示的Web项目

2、以抓取其他网站数据为新闻、用户发布数据为来源

3、基于Flask框架，前后端不分离
```


```
（二）技术实现

1、使用Flask框架实现

2、使用Redis + MySQL 进行数据存储

3、使用第三方扩展

（1）云通信

（2）七牛云
```

```
（三）功能模块分类

1、新闻模块

2、用户模块

3、后台管理模块
```

```
（四）项目目录说明

1、项目根目录 说明

/info 项目应用核心目录

/logs 项目日志目录

config.py 项目配置文件--保存session信息、调试模式、密钥等

manage.py 项目启动文件

requirements.txt     项目依赖文件
```

```
2、项目/info目录 说明

/libs 项目用到的资源库--第三方扩展(云通信)

/modules 项目模块--所有的蓝图对象和视图函数

/static 项目静态文件夹

/template 项目模板文件夹

/utils 项目通用设施--自定义状态码、上传图片等

__init__.py 项目应用初始化文件--应用程序实例、数据库实例、注册蓝图、日志等

constants.py 项目常量信息--数据库缓存信息、验证码、房屋信息等

models.py 项目模型类
```

```
3、项目/info/libs目录 说明

/yuntongxun 第三方扩展--发送短信

sms.py 发送短信
```


```
4、项目/info/static目录 说明

/admin/ 项目admin模块的静态文件，css/html/js等

/news/ 项目admin模块的静态文件，css/html/js等

favicon.ico 项目logo
```


```
5、项目/info/utils目录 说明

image_storage.py 云存储设施文件--七牛云

response_code.py 自定义状态码
```



***
注意：

一、用工厂方法来实例化应用对象app

def create_app(config_name):

     app = Flask(__name__) //实例化启动app

app.config.from_object(config[config_name])  //导入配置信息并动态传入配置信息

     db.init_app(app) //关联db和app
    
     Session(app) //把Session对象和app关联
    
     CSRFProtect(app) // csrf保护关联app

**此处使用请求钩子,在每次请求之后将csrf_token的值传给前端页面**

     **此处用来注册蓝图对象
    
     from pro_info.modules.news import news_blue
    
     app.register_blueprint(news_blue)

……

**注册模板使用的过滤器**

     from pro_info.utils.common import do_index_class
    
     app.add_template_filter(do_index_class, 'index_class')

return app

 

二、每次的请求都需要设置跨站保护，该方法可以使用请求钩子的方法，即每次请求之后执行,这个功能可以设置在实例化应用对象的时候就定义，即放在__init__.py文件中的实例化app对象的工厂方法中

@app.after_request

def after_request(response):

    csrf_token = csrf.generate_csrf()
    
    response.set_cookie('csrf_token',csrf_token)
    
    return response

并在前端的ajax中设置请求头

headers:{

X-CSRFToken:getCookie('csrf_token')

}

三、由于很多接口需要判断用户是否在线的情况，对此我们采用的是用装饰器的方式实现这一功能的。

def login_required(f): è 定义一个方法，方便被调用

     @functools.wraps(f) è 这是一个python内置的装饰器工具，目的是让被装饰的函数的属性不会被改变
    
     def wrapper(*args,**kwargs):
    
         user_id = session.get('user_id') è 尝试获取用户的登录信息
    
         user = None
    
         if user_id:
    
             try:
    
                 user = User.query.get(user_id)
    
             except Exception as e:
    
                 current_app.logger.error(e)
    
         g.user = user è 使用引用上下文的g变量来保存用户的信息
    
         return f(*args,**kwargs)

//具体的实现方式是让被装饰的函数的名称在返回wrapper之前赋值给wrapper的__name__ è wrapper.__name__ = f.__name__

     return wrapper

 


四、统一设置返回的错误页面

由于用户的很多不恰当的操作，或者服务器的原因，导致页面无法显示等错误，我们可以设置指定的错误页面，可以使用

app.errorhandle(code_or_exception) 装饰器来实现这一功能，来达到与用户的更加友好的交互页面，写在__init__文件的工厂方法中

@app.errorhandle(错误码)

@user_login_data

def page_not_found(_):

user = g.user

data = {“user_info”:user.to_dict() if user else None}

return render_template(‘指定的错误页面的模板文件’,data=data)

 

五、为了更直观的展示后台数据效果，需要添加一些测试用户到数据库中，再目录下新建一个.py文件,复制如下代码直接运行即可


```
import datetime

import random

from info import db

from info.models import User

from manage import app

 

def add_test_users():

     users = []

     now = datetime.datetime.now()

     for num in range(0, 10000):

         try:

             user = User()

             user.nick_name = "%011d" % num

             user.mobile = "%011d" % num

         user.password_hash="pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"

             user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))

             users.append(user)

              print(user.mobile)

         except Exception as e:

             print(e)

     # 手动开启一个app的上下文

     with app.app_context():

         db.session.add_all(users)

         db.session.commit()

     print('OK')

 

if __name__ == '__main__':

     add_test_users()
```




新闻首页模块
一、注册相关接口

（一）图片验证码

1、获取前端生成的UUID编码

image_code_id = generate()前端调用该方法生成UUID编号，并发送给服务器

由于这是一个imp标签所以服务器可以request.args.get()获取到这个编码

2、调用captcha(图灵测试)扩展生成图片验证码

对获取到的参数进行验证，判断是否存在

存在则：name,text,image = captcha.generate_captcha()调用captcha生成图片验证码

3、以前端获取的UUID为键，captcha生成的text为值，存储到Redis数据库中

使用Redis数据库redis_store.setex(imageCodeId,time,text)将数据进行保存

4、使用flask中的make_response将图片返回给前端页面

response = make_response(image)

5、修改前端相应报头并返回

response. headers['Content-Type'] = 'image/jpg'

return….

（二）发送手机短信

1、根据接口文档指定请求方式，以及确定需要接受的参数

2、对接受的参数进行校验

（1）确认参数的完整性

if not all([mobile,image_code,image_code_id])

return…

（2）确认手机号是否符合规范（采用正则的方式验证）

if not re.match(r‘1[3456789]\d{9}’,mobile)

return…

（3）确认验证码是否正确，从Redis数据库中取出之前保存的text值进行比对，为防止二次使用验证码，取出后删除数据库中数据

real_image_code = redis_store.get(image_code_id)

redis_store. delete(…)

if not real_image_code.lower() != image_code.lower()

return…

3、参数校验完成后判断用户是否已经注册

查询MySQL数据库中是否存在该用户

user = User.query.filter_by(mobile=mobile).first()

if user 表示用户存在已经注册

return…

4、生成6位随机数，并以用户手机号位键，随机数位值将数据存储到Redis数据库

sms_code = '%06d' % random.randint(0,999999)

redis_store.setex(mobile,time,sms_code)

5、调用第三方云通讯接口发送生成的6位随机数给用户手机，

生成6位随机数：sms_code = '%06d' % random.randint(0,999999)

调用云通讯发送短信：ccp = sms.CCP()

         result = ccp.send_template_sms(mobile,[sms_code,time / 60],1)

如果result == 0 表示发送成功，else发送失败

（三）注册按钮

1、根据接口文档指定请求方式，以及确定需要接受的参数

2、对接受的参数进行校验

（1）确认参数的完整性

if not all([mobile,sms_code,password])

return…

（2）确认手机号是否符合规范（采用正则的方式验证）

if not re.match(r‘1[3456789]\d{9}’,mobile)

return…

（3）确认手机验证码是否正确，从Redis数据库中取出之前保存的sms_code值进行比对，为防止二次使用，取出后删除数据库中数据

real_sms_code = redis_store.get(mobile)

由于之前设置的是有时效的数据，因此需要判断是否还存在该sms_code

redis_store.delete(…)

if not real_sms_code != str(sms_code)

return…

3、将用户的数据存储到MySQL数据库

user = User()

user.moblie = mobile

user.password = password(加密存储)

user.nike_name = mobile(给用户默认设置一个昵称)

db.session.add(user)

db.session,commit()

4、为实现状态保持，将用户的注册的信息存储到Reids数据库中,并提示注册完成

session['user_id'] = user.id

     session['mobile'] = user.mobile
    
     session['nick_name'] = mobile

二、登录相关接口

1、根据接口文档确定需要接受的参数以及请求方式

2、校验参数的完整性

if not all([mobile,password])

3、判断手机号码是否符合规则

if not re.match(r‘1[3456789]\d{9}’,mobile)

return…

4、根据手机号码进行MySQL的数据查找

user = User.query.filter_by(mobile=mobile).first()

5、判断是否存在用户或则密码是否正确

if user is None or not user.check_password(password)（调用加密密码的检查匹对方法）

return

6、保存用户的登录信息并记录用户的最后登录时间

session['user_id'] = user.id

     session['mobile'] = mobile
    
     session['nick_name'] = user.nick_name

 


     user.last_login = datetime.now()

7、记录的用户登录时间需要提交到数据库中

db.session.commit()

8、返回提示用户登录成功

三、退出相关接口

退出即删除用户的登录信息

session.pop('user_id')

     session.pop('mobile')

session.pop('nick_name')

此处建议使用pop()方法，不建议使用clear()方法

 

四、主页相关接口

采用模板的方式，所以需要导入render_template

1、确认用户是否登录在线

user = g.user //此处是定义的装饰器

2、展示点击排行按点击量进行排序查找，且根据前端的设计是显示的六条信息

news_list = News.query.order_by(News.clicks.desc()).limit(6)

3、判断点击排行数据查找结果是否存在

if not news_list:

return…

4、定义一个列表容器保存查询结果

news_dict_list = []

5、遍历所有的查询对象并添加到列表容器中，并调用模型类中to.dict()的方法将之转换成字符串

for news in news_list:

news_dict_list.append(news.to_dict())

6、展示新闻分类数据需搜索所有分类信息

categories = Category.query.all()

7、判断分类数据是否存在

if not categories:

return

8、定义一个列表容器保存查询结果

category_list = []

9、遍历所有的查询对象并添加到列表容器中，并调用模型类中to.dict()的方法将之转换成字典

for category in categories:

category_list.append(category.to_dict())

10、定义一个字典保存所有数据，并将之传给模板进行数据填充

data = {

         "user":user.to_dict() if user else None,//表示如果用户未登录的情况下也是可以访问主页面的
    
          "news_dict_list":news_dict_list,
    
         "category_list":category_list
    
     }

return render_template(‘模板’，data=data)

 

五、首页新闻数据列表接口

1、根据接口文档定义路由，请求方式以及需要哪些参数等（备注：ajax/get请求）

2、接受所需要参数并进行校验（cid，page，per_page）

为实现友好的交互，即使后端没传过来数据，在首页也是需要展示新闻的，所以我们默认会给其定义一个参数

cid = request.args.get('cid','1') è分类id

     page = request.args.get('page','1')
    
     per_page = request.args.get('per_page','10')

3、校验参数，并将数字参数转换成整型值（为了和数据库进行查找）

try:

         cid,page,per_page = int(cid),int(page),int(per_page)
    
     except Exception as e:

return

4、根据参数进行查询数据库

（1）定义变量，存储过滤条件è根据分类id

filters = []

if cid > 1:  => filters.append(News.category_id == cid)

（2）默认按照分类id进行过滤，按新闻发布时间进行排序，对查询数据进行分页

paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)

paginate（页数，每页多少条目数，分页异常不报错）

5、获取分页后的新闻数据模型对象，总页数以及当前页数

news_list = paginate.items //模型对象

     total_page = paginate.pages //总页数
    
     current_page = paginate.page //当前页数

6、遍历模型对象并添加到一个列表容器，使用to_dict()方法转换成字典

for news in news_list:

         news_dict_list.append(news.to_dict())

7、准备返回数据：

(1) data = {

(2)         'news_dict_list':news_dict_list,

(3)         'total_page':total_page,

(4)         'current_page':current_page

(5)     }

8、进行返回 return jsonify(errno=RET.OK,errmsg='OK',data=data)

 

 

 

新闻详情页模块
一、详情页模板接口

1、获取参数以url传参的形式获取参数

@蓝图对象.route(‘/<int:news_id>’)

def get_news_detail(news_id):

2、判断用户是否登录在线，并获取用户信息

user = g.user

3、根据news_id进行查询数据库

news = News.query.get(news_id)

4、检查查询的结果

if not news：

return…

5、展示详情页的分类数据，查询数据库

categories = Category.query.all()

6、检查查询的结果，并定义容器保存遍历的查询对象

if not categories：

return…

7、将新闻详情的点击次数 +1

news.clicks += 1

8、判断是否收藏，默认情况为False，如果用户已经登录，并且被该用户收藏

is_collected = False

    if user and news in user.collection_news:
    
        is_collected = True

9、评论内容，查询数据库获取当前新闻的所有评论

comments = []

comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()

 

10、判断用户登录

if user:

获取所有的评论id

        comment_ids = [comment.id for comment in comments]

再查询当前用户点赞了哪些评论

    comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),CommentLike.user_id == g.user.id).all()

获取当前用户点赞的评论id

    comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]

11、定义一个列表用户来保存评论数据

comment_dict_li = []

12、遍历查询到所有评论数据

    for comment in comments:
    
        comment_dict = comment.to_dict()

判断评论是否被点赞，默认为False 

    comment_dict['is_like'] = False
    
    if comment.id in comment_like_ids:
    
        comment_dict['is_like'] = True

将查询到的点赞的评论数据保存到之前定义的列表中

    comment_dict_li.append(comment_dict)

13、如果用户是登录的，查询用户关注的新闻发布者，默认为Falas

is_followed = False    

    if news.user and user:
    
        if news.user in user.followers:
    
            is_followed = True

14、将所有数据添加到一个字典容器中

data = {

        "news":news.to_dict(),
    
        "category_list":category_list,
    
        'user': user.to_dict() if user else None,//如果用户未登录，那么有关用户的信息就为False，新闻详情页没必要规定用户必须在线
    
        'is_collected': is_collected,
    
        'is_followed': is_followed,
    
        'comments': comment_dict_li
    
    }

15、调用模板页面返回数据，并对模板进行数据填充显示

    return render_template('news/detail.html',data=data)

 


二、收藏和取消收藏接口

根据接口文档进行路由分析，指定请求方式

1、尝试获取用户信息，如果用户未登录，需提示用户登录，才能进行收藏

user = g.user

if not user:

return…

2、获取参数news_id，action（collect，cancle_collect）

request.json.get()方法获取

3、检查参数，对news_id强转为整型值，对数据库进行查询，如果强转出错返回错误信息

4、检查action的值是否存在

if action not in ['collect', 'cancel_collect']:

return…

5、判断新闻是否存在数据库中

news = News.query.get(news_id)

if not news:

return…

6、判断选择的是collect还是cancle_collect,并判断用户是否收藏过该新闻,未收藏过添加到收藏，收藏过返回已收藏

if action == collect:

if news not in user.collection_news:

user.collection_news.append(news)

else:

If news in  user.collection_news:

User.collection_news.remove(news)

7、提交数据库

8、返回ajax响应信息

 

三、关注和取消关注接口

与收藏接口类似，只需根据接口文档定好路由以及请求方式，不过多赘述

 

四、新闻评论接口

根据接口文档确定路由及请求方式

1、获取用户登录信息，如果用户未登录直接返回并提示登录

user = g.user

2、获取参数，news_id,comment,parent_id(回复的评论的id)

request.json.get()方法

3、校验参数完整性

if not all([news_id,comment]):

return…

4、对news_id进行强转，并判断是否有parent_id，如果强转失败返回错误信息

news_id = int（news_id）

if parent_id:

parent_id = int（parent_id）

5、查询新闻并判断新闻是否存在

news = News.query.get(news_id)

if not news：

return…

6、实例化评论模型的对象，并添加数据

comment = Comment()

     comment.user_id = user.id
    
     comment.news_id = news.id
    
     comment.content = comment_conent

7、判断父评论是否存在，存在则添加父评论的信息

if parent_id：

comment.parent_id = parent_id

8、提交数据到数据库

try:

        db.session.add(comment)
    
        db.session.commit()
    
    except Exception as e:
    
        current_app.logger.error(e)
    
        db.session.rollback()

9、返回评论数据给前端ajax

 

五、点赞和取消点赞接口

根据接口文档确定路由及请求方式

1、获取用户登录信息，如果用户未登录直接返回并提示登录

user = g.user

2、获取参数，comment_id,action(add,remove)

request.json.get()方法

3、校验参数完整性

if not all([comment_id,action])

return…

if action not in [add,remove]

return…

4、把comment_id转成整型，强转错返回错误信息

5、根据comment_id查询数据

comment = Comment.query.get(comment_id)

6、判断查询结果，如果不存在，返回错误信息

7、判断action参数是否为add或者remove

（1）如果为add，判断行为是点赞还是取消点赞，使用CommentLike进行过滤查询（user_id，comment.id）

comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id, CommentLike.comment_id == comment.id).first()

if not comment_like_model：è 点赞行为，点赞数加1

    comment_like_model = CommentLike()
    
        comment_like_model.user_id = user.id
    
        comment_like_model.comment_id = comment.id
    
        db.session.add(comment_like_model)
    
        comment.like_count += 1

（2）否则为取消点赞 è 取消点赞，点赞数减1

db.session.delete(comment_like_model)

        comment.like_count -= 1

8、将数据提交到数据库中

db.session.commit()

9、返回结果给ajax

 

 

个人中心模块
基于iframe进行实现，子页面的数据更新之后需要同步主页面相关联数据，可以采用js进行实现，本项目即采用了ajax的数据交互方式

一、用户页面接口

这里我们用到的是之前就定义好的装饰器来获取的用户信息

1、获取用户信息

user = g.user

2、判断是否获得了用户的信息，如果没有则重定向到主页

if not user:

return redirect(‘/’)

3、将获取的用户信息使用字典容器保存起来

4、将数据返回给user.html模板，进行页面显示

二、用户基本信息展示和修改接口

根据接口文档确定路由以及请求方式[‘GET’,‘POST’]

1、判断请求方式，默认GET请求加载模板页面，可以直接以装饰器获取到用户的信息进行返回

user = g.user

if request.method == ‘GET’:

将用户信息返回给模板

return… è 模板为：user_base_info.html

2、获取参数（signature,nick_name,gender(男，女)）

request.json.get()方法

3、校验参数的完整性

if not all([signature,nick_name,gender])

return…

4、检查参数gender参数

if gender not in [‘MAN’，‘WOMEN’]

return…

5、使用user对象将用户的基本信息保存到数据库

user.signature = signature

    user.nick_name = nick_name
    
     user.gender = gender
    
     try:
    
         db.session.add(user)
    
         db.session.commit()
    
     except Exception as e:
    
         current_app.logger.error(e)
    
         db.session.rollback()

6、返回结果

 

三、上传用户头像接口

根据接口文档确定路由以及请求方式[‘GET’,‘POST’]

1、判断请求方式，默认GET请求加载模板页面，可以直接以装饰器获取到用户的信息进行返回

user = g.user

if request.method == ‘GET’:

将用户信息返回给模板

return… è 模板为：user_pic_info.html

2、获取参数（avatar）

request.files.get()方法

3、校验参数是否存在

if not avatar：

return…

4、使用read()方法读取图片的二进制数据并保存

avatar_data = avatar.read()

5、调用第三方接口storage()，将图片上传到七牛云，并保存七牛云返回的图片名称

image_name = storage(avatar_data)

6、给用户保存图片的名称并提交到到数据库

user.avatar_url = image_name

try:

         db.session.add(user)
    
         db.session.commit()
    
     except Exception as e:
    
         current_app.logger.error(e)
    
         db.session.rollback()

7、拼接图片的绝对路径并返回给ajax

设置的七牛云地址 + image_name

 

四、修改用户密码接口

根据接口文档确定路由以及请求方式[‘GET’,‘POST’]

1、判断请求方式，默认GET请求加载模板页面

if request.method == ‘GET’:

return… è 模板为：user_pass_info.html

2、获取参数（old_password,new_password）

request.json.get()方法

3、检查参数完整性

if not all([old_password,new_password])

return…

4、获取用户信息，并比较用户输入的旧密码，验证是否正确

user = g.user

if not user.check_password(old_password):

return…

5、验证成功后保存用户的新密码，并提交到数据库

user.password = new_password

     try:
    
         db.session.add(user)
    
         db.session.commit()
    
     except Exception as e:
    
         current_app.logger.error(e)
    
         db.session.rollback()

6、返回结果给ajax

 

五、新闻发布接口

根据接口文档确定路由以及请求方式[‘GET’,‘POST’]

1、判断请求方式，默认GET请求加载模板页面

if request.method == 'GET':

查询新闻分类，与新闻首页模块的主页相关接口6、7、8、9雷同

return… è 模板为：user_ news_release.html

2、获取请求参数

request.form.get()方法获取表单参数

request.files.get()方法获取新闻图片参数

3、校验参数完整性

if not all([title,category_id,digest,index_image,content]):

         return…

4、强转分类id，如果报错直接返回错误信息

5、read()方法读取获取的新闻图片的二进制数据并调用第三方七牛云接口上传图片，并保存返回的图片名称

image_data = index_image.read()

        image_name = storage(image_data)

6、实例化新闻类对象，用来保存新闻数据

news = News() è 新闻类对象

     news.title = title è 新闻标题
    
     news.source = '个人发布' è 新闻发布机构
    
     news.category_id = category_id è 新闻分类id
    
     news.digest = digest è 新闻摘要
    
     news.index_image_url = 设置的七牛云地址 + image_name è 新闻图片绝对路径
    
     news.content = content è 新闻内容
    
     news.status = 1 è 新闻状态，1表示待审核，0表示审核通过，-1表示未通过审核

7、提交数据到数据库中

 

六、用户新闻列表接口

根据接口文档确定路由和请求方式

1、获取参数，页数，默认1

request.args.get()方法

2、校验参数，将page强转为整型，如果报错直接返回错误信息

3、获取用户信息，定义容器存储查询结果，总页数默认1，当前页默认1

4、查询数据库，查询新闻数据并进行分页，

user = g.user

paginate = News.query.filter(News.user_id==user.id).paginate(page,每页数据数目 ,False)

**可参看新闻首页模块的新闻列表接口**

5、返回数据给模板：user_news_list.html

 

七、用户关注信息接口

根据接口文档确定路由和请求方式

**与用户新闻列别接口流程类似**

返回数据给模板：user_follow.html

 

八、查询用户关注的其他用户信息

根据接口文档确定路由和请求方式

1、获取用户的登录信息

user = g.user

2、获取参数other_id(用户关注的用户)

request.args.get()方法

3、校验参数是否存在，如果不存在，返回错误信息

4、查询信息

other = User.query.get(other_id)

5、判断新闻是否有作者，且用户关注过作者，默认为False

is_follwed = False

if other and user:

         if other in user.followed:
    
             is_follwed = True

6、返回数据给模板：other.html

 

九、返回指定用户发布的新闻接口

根据接口文档确定路由和请求方式

1、获取参数(user_id,页数默认为1)

request.args.get()方法获取

2、校验参数，强转页数的参数，如果报错，直接返回错误信息

3、判断用户是否存在

other = User.query.get(user_id)

if not other:

return…

4、如果用户存在，分页用户发布的新闻数据

paginate = other.news_list.paginate(page,每页条目数,False)

5、获取分页数据，并遍历数据

news_list = paginate.items

        current_page = paginate.page
    
        total_page = paginate.pages

6、返回数据给ajax

 

 

后台管理模块
主要是为了方便网站的管理而创建的后台管理员模块。管理员与普通用户公用一张表，管理员也具有普通用户的功能，用指定的字段区分普通用户和管理员用户，管理员可以登录到后台管理页面对新闻以及相应的数据进行操作。

一、创建管理员

使用flask-script扩展自定义脚本命令，以自定义函数的形式实现创建管理员用户

@manage.option('-n','-name',dest='name')

@manage.option('-p','-password',dest='password') //使用脚本扩展必须要的装饰器函数

def create_supperuser(name,password): //定义创建管理员的函数，并传入用户名和密码参数

     if not all([name,password]): //校验参数完整性
    
         print('参数缺失')
    
     user = User() //创建模型类User的对象
    
     user.nick_name = name // 添加相应的数据
    
     user.mobile = name
    
     user.password = password
    
     user.is_admin = True
    
     try: //提交数据到数据库
    
         db.session.add(user)
    
         db.session.commit()
    
     except Exception as e:
    
         db.session.rollback()
    
         print(e)
    
     print('管理员创建成功')

最后使用终端命令行创建管理员用户

python manage.py 函数名 -n 用户名 -p 密码

 

二、管理员登录请求钩子的应用 è 判断当前登录的用户是否是管理员，并且判断当前访问的url是否是管理员登录的页面url

因为后台管理不需要让每个普通用户都知道，所以在每次请求前先判断，在后台管理的模块中的创建蓝图的模块中就可使用before_request请求钩子实现该功能。具体方式如下：(在后台管理模块的 __init__.py 文件中)

@admin_blu.before_request //每次的请求之前执行的请求钩子

def check_admin():

     is_admin = session.get("is_admin", False) //从Redis数据库中获取用户登录状态的信息，默认为False
    
     //判断获取的is_admin,如果不是False表示是管理员，并判断访问的页面是否是管理员登录页面的url，否则返回主页，终止后续操作。

if not is_admin and not request.url.endswith(url_for('admin.login')):

         return redirect('/') //使用重定向返回到主页页面

 


三、后台管理首页接口

定义路由，返回后台管理首页模板页面

@admin_blu.route('/index') //定义路由

@login_required //确认用户是否登录

def index():

user = g.user //获取用户相关信息

    return render_template('admin/index.html',user=user.to_dict()) //返回后台管理首页模板

 


四、后台管理员登录接口

定义路由，指定请求方式（GET，POST）

1、如果为GET请求，使用session获取登录信息。

request.method == ‘GET’

2、判断用户是否登录并且是管理员,则重定向到后台管理页面

if user_id and is_admin:

return redirect(url_for(‘后台管理页面模板’)

3、否则返回后台管理登录页面模板

return render_template(‘后台管理登录页面’)

4、POST请求方式下获取参数（user_name,password）

request.form.get()方法

5、校验参数完整性

if not all([user_name,password]):

return…

6、查询数据库，并判断用户密码是否正确

user = User.query.filter(User.mobile==user_name,User.is_admin==True).first()

if user is None or not user.check_password(password)：

return…

7、缓存用户信息，实现状态保持

session['user_id'] = user.id

     session['mobile'] = user.mobile
    
     session['nick_name'] = user.nick_name
    
     session['is_admin'] = user.is_admin

8、重定向到后来管理首页

return redirect(url_for('admin.index'))

 

五、后台用户数据展示接口

定义路由，获取数据一般默认为GET请求

1、根据页面显示内容包括总人数，月新增人数，日新增人数

2、查询数据库统计总人数，排除管理员用户的所有普通用户

总人数 = User.query.filter(User.is_admin == False).count()

3、查询数据库统计月新增人数，排除管理员用户的所有普通用户

（1）使用time模块获取时间对象（tm_year=2018, tm_mon=6, tm_mday=9）

 t = time.localtime()

（2）通过时间对象生成每月开始日期的字符串

 mon_begin_date_str = '%d-%02d-01' %(t.tm_year,t.tm_mon)

（3）使用strptime（）方法将日期的字符串转换成日期对象

 mon_begin_date = datetime.strptime(mon_begin_date_str,'%Y-%m-%d')

（4）作为过滤条件查询数据库，获取月新增人数

 mon_count = User.query.filter(User.is_admin == False,User.create_time > mon_begin_date).count()

4、查询数据库统计日新增人数，排除管理员用户的所有普通用户

具体步骤同统计月新增人数方式，先获取当前日期，生成字符串，再转换成日期对象，查询数据库加上过滤条件，获取日新增用户数据

5、实现统计活跃人数/活跃日期

定义列表容器存储活跃人数，和活跃日期

（1）获取当前日期，生成字符串，再转换成日期对象

today_begin_date_str = '%d-%02d-%02d' %(t.tm_year,t.tm_mon,t.tm_mday)

     today_begin_date = datetime.strptime(today_begin_date_str,'%Y-%m-%d')

（2）遍历日期，获取每天的开始日期和结束日期

for x in range(0,31): //一个月按30天

//开始时间，即每天的0时0分

begin_date = today_begin_date - timedelta(days=x) //timedelta()代表两个时间之间的时间差，两个data或datatime

//结束时间，即第二天的0时0分 //对象相减就可以返回一个timedelta对象，传入的参数表示前多少天

end_date = today_begin_date - timedelta(days=(x-1))

（3）使用时间的过滤条件查询数据库统计活跃日期的活跃人数

count = User.query.filter(User.is_admin == False, User.last_login >= begin_date, User.last_login < end_date).count()

（4）将需要的数据添加到之前定义的列表中

active_time.append(begin_date_str)

         active_count.append(count)

6、定义字典保存所需数据，将之返回给指定的模板进行渲染

data = {……}

return render_template('admin/user_count.html',data=data)

 

六、后台用户列表展示接口

1、获取参数，页数，默认为1

request.args.get()方法

2、校验参数，强转为int类型，如果错误，直接返回错误信息

3、查询数据库获取用户列表信息采用分页查找方式

paginate = User.query.filter(User.is_admin==False).paginate(page, 每页数目, False)

提取查询结果

current_page = paginate.page

         total_page = paginate.pages
    
         users = paginate.items

4、定义容器，遍历查询结果，并添加到容器中

for user in users:

         user_dict_list.append(user.to_admin_dict())

5、返回数据到指定的模板进行渲染

return render_template('admin/user_list.html', data=data)

 

七、后台新闻审核展示接口

1、获取参数，（页数，默认为1，关键字参数，默认为None）

request.args.get()方法

2、校验参数，强转页数为int类型，如果错误，直接返回错误信息

3、初始化变量,news_list[],current_page = 1,total_page = 1

4、设置过滤查询条件，当新闻状态不为0的情况下查询新闻数据

filters = [News.status != 0]

5、判断关键字参数是否存在，如果存则添加关键字搜索到过滤查询条件中

if keywords:

        filters.append(News.title.contains(keywords))

6、根据参数，进行分页过滤查询数据库并提取查询结果

paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

提取查询结果

news_list = paginate.items

        current_page = paginate.page
    
        total_page = paginate.pages

7、遍历查询到的对象，组织数据返回给指定模板渲染

return render_template('admin/news_review.html', data=data)

 

八、后台新闻详情展示接口

通过url传入新闻id的参数，如下定义路由

@admin_blu.route('/news_review_detail/<int:news_id>')

def news_review_detail(news_id):

……

1、根据news_id查询新闻详情数据

news = News.query.get(news_id)

2、校验查询结果，如果未查到返回给指定模板错误信息

if not news:

         return render_template('admin/news_review_detail.html',data={'errmsg':'未查到数据'})

3、查询到结果调用to_dict()方法再传回指定模板渲染数据

return render_template('admin/news_review_detail.html',data= {"news":news.to_dict()})

 

九、后台新闻审核接口

根据需求，应该为POST请求，定义路由指定请求方式

1、获取参数（新闻id，action）

request.json.get()方法

2、校验参数完整性

if not all([news_id,action]):

return…

3、校验action参数是否为accept或reject

if action not in [accept,reject]:

return…

4、根据新闻id查询数据库

news = News.query.get(news_id)

5、判断是否查询到数据

if not news:

return…

6、判断action的具体值，accept表示接受，reject表示拒绝

如果为accept修改新闻状态为  0

如果为reject修改新闻状态为 -1

7、如果拒绝，接受拒绝原因

request.json.get()方法，获取拒绝内容

8、判断是否接受到接受原因，未接受到返回错误信息

9、将数据提交到数据库

try:

         db.session.commit()
    
     except Exception as e:
    
         current_app.logger.error(e)
    
        db.session.rollback()

10、返回信息

 

十、后台新闻版式编辑接口

1、获取参数（页数默认为1，关键字参数默认为None）

request.args.get()方法获取

2、校验参数，强转页数为int类型，如果错误，直接返回错误信息

3、初始化变量,news_list[],current_page = 1,total_page = 1

4、定义过滤条件，并判断关键字参数是否存在，如果存在，添加到过滤条件中

filters = [News.status != 0]

     if keywords:
    
         filters.append(News.title.contains(keywords))

5、根据相关数据进行分页查询数据库，并保存到之前初始化的遍历中

paginate = News.query.filter(*filters).paginate(page,每页数目,False)

        news_list = paginate.items
    
        current_page = paginate.page
    
        total_page = paginate.pages

6、遍历查询数据对象，调用to_basic_dict()方法

news_dict_list = [] //定义一个容器接受

     for news in news_list:
    
         news_dict_list.append(news.to_basic_dict())

7、组织好数据返回给指定的模板进行渲染

return render_template('admin/news_edit.html',data=data)

 

十一、后台新闻编辑详情接口

根据需求判断，应该是GET请求和POST请求，定义路由，和请求方式

1、判断是否是GET请求

2、获取参数新闻id，校验参数存在，强转int，如果错误，返回错误

3、根据新闻id获取新闻数据

4、校验查询数据是否存在，查询错误或则查询失败直接返回给指定模板错误信息

5、查询分类信息并移除最新分类，使用pop方法

6、遍历分类信息，并判断当前遍历到的分类和新闻所属分类是否一致

8、所有条件成立的情况下，组织数据返回给指定模板进行渲染

9、如果为POST请求，获取参数（news_id,title,digest,content,index_image,category_id）

request.form.get()获取表单中的数据

request.files.get()获取图片文件

10、校验参数完整性，与之前大同小异

11、根据新闻id查询数据库，确认新闻是否存在，与之前大同小异

12、读取图片数据，调用第三方接口（七牛云）上传图片并保存七牛云返回的图片名称，拼接图片的绝对路径

13、将数据保存到数据库进行提交

14、返回结果。（***大部分操作可参照个人中心模块新闻发布接口***）

 

十二、后台新闻分类修改接口

根据需求判断请求方式应该为GET和POST，定义路由

1、判断如果是GET请求

2、查询所有分类数据，遍历查询结果，并移除最新分类（使用pop()方法）

3、组织数据返回给指定模板进行渲染

4、如果是POST请求

5、获取参数（name，cid） //如果有cid表示编辑已存在的分类

request.json.get()方法获取

6、校验参数name的存在

7、判断cid是否存在，如果存在即修改已有的分类，强转为int类型

8、根据分类cid查询数据库，校验查询结果

9、修改cid的分类信息为name的值

10、实例化分类模型类的对象，保存分类名称，并将数据库提交到数据库

11、返回结果