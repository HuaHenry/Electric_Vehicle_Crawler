# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferred_cars = db.Column(db.Text, nullable=True)  # 用户偏好车型（保存车型名列表，逗号分隔）

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 新增销量数据
# class Car(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)        # 车型名
#     brand = db.Column(db.String(100), nullable=True)         # 品牌
#     min_price = db.Column(db.Float, nullable=True)           # 最低售价
#     max_price = db.Column(db.Float, nullable=True)           # 最高售价
#     month = db.Column(db.String(6), nullable=True)           # 销售月份
#     url = db.Column(db.String(255), nullable=True)           # 车型详情页链接
#     image_url = db.Column(db.String(2550), nullable=True)     # 车型图片链接
#     sales = db.Column(db.Integer, nullable=True)             # 新增字段：销量

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    min_price = db.Column(db.Float, nullable=True)
    max_price = db.Column(db.Float, nullable=True)
    month = db.Column(db.String(6), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(2550), nullable=True)
    sales = db.Column(db.Integer, nullable=True)

    # 新增字段（统一描述车型信息）
    size = db.Column(db.String(32), nullable=True)             # 车型尺寸
    battery_type = db.Column(db.String(32), nullable=True)     # 电池类型
    range_km = db.Column(db.Integer, nullable=True)            # 续航
    autopilot_level = db.Column(db.String(16), nullable=True)  # 智能驾驶等级