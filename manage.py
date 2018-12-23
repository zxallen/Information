import logging

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app, db, models   # 导入模型类所在文件models


# 调用ａｐｐ创建的函数生成ａｐｐ对象,参数传入字典中想使用的配置
app = create_app("development")

# 6.设置命令行运行和数据库迁移准备
manager = Manager(app)
Migrate(app,db)
manager.add_command("db",MigrateCommand)

# 数据库迁移：
# 创建数据库，根据已有模型类，利用数据库迁移创建表
# 因为模型类并不在此文件中，所以执行此文件创建表不会成功
# 所以需要导入模型类的文件
# 命令行执行：
# 1.python manage.py db init    初始化
# 2.python manage.py db migrate -m"版本注释"   生成迁移版本
# 3.python manage.py db upgrade   生成数据库迁移

if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
