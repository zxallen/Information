import random
import re
from datetime import datetime

from flask import abort,current_app, make_response, request, jsonify
from flask import session

from info import constants, db
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET

# 生成并刷新验证码的视图函数，


@passport_blu.route("/image_code")
def get_image_code():
    """
    生成图片验证码
    1、接收uuid
    2、校验uuid是否存在
    3、生成验证码
    4、文本验证码保存到redis数据库中
    5、返回图片验证码
    :return:
    """
    # 1.获取uuid,从main.js中，在点击函数中
    image_code = request.args.get("imageCodeId")

    # 2.校验uuid是否存在
    if not image_code:
        return abort("404")

    # 3.获取验证码，调用的captcha工具生成的验证码图片
    # 返回三个数据，第一个没用，第二个验证码文本，第三个对应的图片
    _, test, image = captcha.generate_captcha()
    print(test)
    # 4.文本验证码test保存在redis中，其中uuid为key,test为值，
    # 其中三个参数，第一个key,可以拼接下好区分，第二个存活时间，在constants.py文件中导入
    # 第三个是刚刚通过图片验证码的工具包生成的图片，为二进制格式保存的图片
    # 一般在保存到数据库中时候使用try ，出现错误时候可以保存到日志
    try:
        redis_store.setex("ImageCode_"+ image_code, constants.IMAGE_CODE_REDIS_EXPIRES, test)
    except Exception as e:
        current_app.logger.error(e)
        return abort("500")

    # 修改返回的图片格式，如果不修改，默认test/html,避免浏览器不能识别,
    # 使用response对象，调用make_response函数，函数中传入需要返回的对象
    # 这样可以设置响应报文中的一些属性，最后将response返回，既返回本来需要返回的
    # 也将响应报文内容做出更改,返回"image/png"格式
    response = make_response(image)
    response.headers["Content-Type"] = "image/png"

    return response


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    获取短信验证码
    1、接收参数 mobile image_code image_code_id
    2、校验参数的完整性
    3、校验手机号是否正确
    4、比对数据库中的图片验证码和用户输入的验证码是否一致
    5、生成短信验证码
    6、发送短信验证码
    7、保存短信验证码到redis数据库中
    8、返回响应
    :return:
    """
    # 1.想进行发送短信的功能，需要先获取手机号，用户输入图片验证码内容,以及验证码的编码
    # 对此进行判断,满足了才能实现发送短信功能
    mobile = request.json.get("mobile")
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")

    # 2.判断各个需要传入的全了,不全抛出异常
    if not all([mobile,image_code,image_code_id]):
        return jsonify(erron = RET.PARAMERR,errmsg="参数不完整")

    # 3.验证手机号码是否正确:利用正则
    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(erron = RET.PARAMERR,errmsg="手机号码错误")

    # 4.对比用户输入的图片验证码和数据库中保存的是否一致:
    # 又由于操作数据库,在try中执行:
    try:
        # 根据编码获取保存在数据库中的图片验证码内容
        # 操作数据库出现异常时写入日志,并给用户返回数据库查询错误的信息
        real_image_code = redis_store.get("ImageCode_"+ image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron = RET.DBERR,errmsg="查询错误")
    # 5.验证是否查询到数据:
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")
    # 6.和用户输入的比较,判断是否一样:注意忽略大小写,使用.upper()
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    # 7.满足上述条件则生成随机验证码:
    sms_code = "%06d" % random.randint(0,999999)
    print(sms_code)
    # 8.发送手机验证码:
    # result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # print(result)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="第三方发送短息出错")

    # 9.发送成功,则保存短信验证码到redis数据库中
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")

# 注册功能
@passport_blu.route("/register", methods=["POST"])
def register():
    """
    提交注册信息,后端获取mobile,sms_code,password,
    进行数据校验:1数据完整性,2.手机号,3.短信验证码,
    将数据保存到mysql数据库中,并保持登陆状态,返回响应
    :return:
    """
    # 1.获取参数
    mobile = request.json.get("mobile")
    smscode = request.json.get("smscode")
    password = request.json.get("password")

    # 2.完整性验证
    if not all ([mobile,smscode,password]):
        return jsonify(erron = RET.PARAMERR,errmsg="参数不完整")

    # 3.手机号校验
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(erron=RET.PARAMERR, errmsg="手机号码错误")

    # 4.短信验证码校验,和存在数据库的相对比
    # 取出数据库中的smscode:
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron = RET.DBERR,errmsg="查询错误")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5.保存用户注册信息到数据库
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 哈希算法加密密码保存,在模型类中集成了哈希加密方法,
    # 使用property装饰器实现"对象.方法 = 值"的调用形式
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 6.保持用户登陆状态:
    session["user_id"] = user.id

    # 7.返回响应:
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 登陆功能:
@passport_blu.route("/login", methods=["POST"])
def login():
    """
    登陆逻辑:
    获取用户输入的手机号,密码
    校验:1,数据完整性
        2.手机号格式
        3.查找手机号是否存在于数据库
        4.存在,则取出对应的密码和用户输入的密码对比
    密码正确,则更改用户最后登录时间并返回响应
    :return:
    """

    # 1.获取数据
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    # print(mobile,password)
    if not all([mobile,password]):
        return jsonify(erron = RET.PARAMERR,errmsg="参数不完整")

    if not re.match(r"1[35678]\d{9}",mobile):
        return jsonify(erron = RET.PARAMERR,errmsg="手机号码错误")

    try:
        user = User.query.filter_by( mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户未注册")

    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


# 退出登录
@passport_blu.route("/logout")
def logout():
    """
    退出登录:清除session
    :return:
    """
    #
    session.pop("user_id",None)
    return jsonify(errno=RET.OK, errmsg="退出成功")











