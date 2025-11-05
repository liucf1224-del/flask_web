from .. import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from demo.model import User  # 使用统一导入方式
from demo.utils.respose_utils import success_response, error_response


class UserController:
    @staticmethod
    def get_all_users():
        try:
            users = User.query.all()
            # users_data = [{'id': u.id, 'username': u.username} for u in users]
            users_data = [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'dd_info': {
                    'id': u.dd.id if u.dd else None,
                    'name': u.dd.name if u.dd else None
                }
            } for u in users]
            return success_response(data=users_data)
        except SQLAlchemyError as e:
            return error_response(message=f"数据库查询失败: {str(e)}")

    @staticmethod
    def create_user(username, email):
        try:
            if User.query.filter_by(username=username).first():
                return error_response(message=f"用户名 '{username}' 已存在", status_code=400)
            if User.query.filter_by(email=email).first():
                return error_response(message=f"邮箱 '{email}' 已存在", status_code=400)

            #   `created_at` datetime DEFAULT NULL,
            new_user = User(username=username, email=email)
            db.session.add(new_user)
            db.session.commit()
            return success_response(data={"message": f"用户 {username} 添加成功", "id": new_user.id}, status_code=201)
            db.session.rollback()
            return error_response(message=f"数据完整性错误 {str(e)}", status_code=400)
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response(message=f"数据库错误 {str(e)}", status_code=500)

    @staticmethod
    def edit_user(username, email, id):
        try:
            #  检查用户是否已存在
            user = User.query.filter_by(id=id).first()
            if not user:
                return error_response(message=f"用户不存在", status_code=404)
            if User.query.filter_by(username=username).first():
                return error_response(message=f"用户名 '{username}'已存在 ", status_code=400)
            # 修改
            user.username = username
            user.email = email
            db.session.commit()
            return success_response(data={"message": f"修改成功"})
        except IntegrityError as e:
            db.session.rollback()
            return error_response(message=f"数据完整性错误 {str(e)}", status_code=400)
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response(message=f"数据库错误 {str(e)}", status_code=500)

    @staticmethod
    def delete_user(id):
        try:
            # 检查用户是否已存在
            user = User.query.filter_by(id=id).first()
            if not user:
                return error_response(message=f"用户不存在", status_code=404)
            # 删除用户
            db.session.delete(user)
            db.session.commit()
            return success_response(data={"message": f"用户 {user.username} 删除成功"})
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response(message=f"数据库错误 {str(e)}", status_code=500)
