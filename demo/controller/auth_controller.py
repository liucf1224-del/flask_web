from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from demo.model import User  # 使用统一导入方式
from demo.utils.respose_utils import success_response, error_response

#权限控制
class AuthController:
    @staticmethod
    def check_user(username,password):
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                access_token = create_access_token(identity=username)
                # additional_claims = {"role": "admin", "user_id": user.id}    增加对应的数据操作
                # access_token = create_access_token(identity=username, additional_claims=additional_claims)
                return success_response(data={"access_token": access_token,"username":username})
            else:
                return error_response(message="用户名或密码错误")
        except SQLAlchemyError as e:
            return error_response(message=f"数据库查询失败: {str(e)}")

