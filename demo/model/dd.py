from demo import db


class Dd(db.Model):
    __tablename__ = 'dd'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    # 一对一关系（一个 Dd 对应一个 User）
    user = db.relationship('User', back_populates='dd', uselist=False)
    def __repr__(self):
        return f'<Dd {self.name}>'