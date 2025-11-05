from demo import db
class Copyright(db.Model):
    __tablename__ = 'copyright_pay_info_2025_03'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id = db.Column(db.String(16), nullable=False, comment='场所号')
    device_id = db.Column(db.Integer, default=None, comment='云账号或者新的云账号（换房时）')
    order_no = db.Column(db.String(100), default=None, comment='订单号')
    facilitator_id = db.Column(db.Integer, default=0, comment='服务商id：3云南 4贵州 6江西 9广西 10山东 14山西 0是平台')
    old_device_id = db.Column(db.Integer, default=None, comment='旧的云账号（换房时写入数据）')
    old_order_no = db.Column(db.String(100), default=None, comment='旧的订单号（换房时写入数据）')
    total = db.Column(db.Numeric(10, 2), default=None, comment='金额')
    payment_time = db.Column(db.DateTime, default=None, comment='支付时间')
    start_time = db.Column(db.DateTime, default=None, comment='开始时间')
    end_time = db.Column(db.DateTime, default=None, comment='结束时间')
    order_type = db.Column(db.SmallInteger, default=0, comment='订单类型：0无类型 1调试，2开台/续费')
    method = db.Column(db.String(255), default=None, comment='方法')
    result = db.Column(db.SmallInteger, default=2, comment='结果：0成功 非0失败')
    practical = db.Column(db.Numeric(10, 2), default=None, comment='平台收入')
    remark = db.Column(db.String(255), default=None, comment='备注')
    tax_rate = db.Column(db.Numeric(10, 2), default=None, comment='税率')
    after_amount = db.Column(db.Numeric(10, 8), default=None, comment='税后金额')
    service_charge = db.Column(db.Numeric(10, 2), default=None, comment='手续费')
    distribution_proportion = db.Column(db.Integer, default=None, comment='分发比例')
    pay_facilitator_money = db.Column(db.Numeric(10, 8), default=None, comment='应打款金额')
    who_will_pay_the_handling_charge = db.Column(db.SmallInteger, default=None, comment='由谁支付手续费:1收款方 2发款方')
    click_count = db.Column(db.Integer, default=0, comment='点唱次数')
    is_invoiced = db.Column(db.SmallInteger, default=0, comment='是否开发票：0否 1是')
    day = db.Column(db.Date, default=None, comment='天数')
    created_at = db.Column(db.Integer, default=0, comment='添加时间')
    updated_at = db.Column(db.Integer, default=0, comment='更新时间')

    def __repr__(self):
        return f'<Copyright {self.shop_id}>'
