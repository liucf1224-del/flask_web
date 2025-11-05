# run.py
from demo import create_app, db,get_app_instance  # 导入 get_app_instance
from sqlalchemy import inspect
from sqlalchemy.sql import text  # 导入text

app = create_app()

with app.app_context():
    try:
        # 使用text()明确声明SQL语句
        db.session.execute(text('SELECT 1'))
        print("数据库连接成功!")
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        # 打印详细错误信息
        import traceback
        traceback.print_exc()
        exit(1)

    # 正确方式：使用SQLAlchemy的inspect API检查表是否存在
    inspector = inspect(db.engine)
    # 获取所有模型类
    from demo.model import User  # 使用统一导入方式

    # 检查每个模型对应的表是否存在
    tables_exist = True
    for model in [User]:  # 添加所有模型类到这里
        if not inspector.has_table(model.__tablename__):
            tables_exist = False
            break

    # 如果任何表不存在，则创建所有表
    if not tables_exist:
        db.create_all()
        print("数据库表已创建")
    else:
        print("数据库表已存在")

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
