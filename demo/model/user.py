from demo import db
from datetime import datetime

# 用户
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 添加这行

    def check_password(self, password):
        return self.password == password  # 建议使用 hash 比较
    # 添加外键关联
    # dd_id = db.Column(db.Integer, db.ForeignKey('dd.id'), nullable=False)
    #
    # # 关系定义（多对一关系，多个用户可能属于同一个 dd）
    # # dd = db.relationship('Dd', backref='users')
    # dd = db.relationship('Dd', backref='user', uselist=False)

    # 外键关联
    dd_id = db.Column(db.Integer, db.ForeignKey('dd.id'), unique=True)
    # 一对一关系（一个 User 对应一个 Dd）
    dd = db.relationship('Dd', back_populates='user')
    def __repr__(self):
        return f'<User {self.username}>'