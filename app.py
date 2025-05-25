# app.py
from flask import Flask, render_template, url_for, flash, redirect, request
from models import db, User, Car
from forms import RegistrationForm, LoginForm
from config import Config
from recommend import recommend_for_user
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy.sql.expression import func
from flask import jsonify

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = '你的数据库连接串'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app(app)
migrate = Migrate(app, db)   # <<< 加上这一行

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# @app.route("/")
# @login_required
# def home():
#     return render_template('home.html')

# 新增偏好汽车导入页面
@app.route("/")
@login_required
def home():
    if not current_user.preferred_cars:
        return redirect(url_for('choose_cars'))
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        print(f"[DEBUG] 表单提交通过: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print(f"[DEBUG] 找到了用户: {user.username}")
        else:
            print(f"[DEBUG] 没找到用户")
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('登录失败，请检查邮箱和密码', 'danger')
    else:
        flash('登录失败，请检查邮箱和密码', 'danger')
        print(f"[DEBUG] 表单提交失败")

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# @app.route("/choose", methods=['GET', 'POST'])
# @login_required
# def choose_cars():
#     cars = Car.query.order_by(func.random()).limit(10).all()  # 随机选20辆
#     if request.method == 'POST':
#         selected_cars = request.form.getlist('cars')
#         if selected_cars:
#             current_user.preferred_cars = ','.join(selected_cars)
#             db.session.commit()
#             flash('偏好保存成功！', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('请至少选择一辆喜欢的车型', 'danger')
#     return render_template('choose_cars.html', cars=cars)

@app.route("/choose", methods=['GET', 'POST'])
@login_required
def choose_cars():
    cars = Car.query.order_by(func.random()).all()  # 随机展示所有车型
    if request.method == 'POST':
        selected_cars = request.form.get('selected_cars')
        if selected_cars:
            car_list = selected_cars.split(',')
            current_user.preferred_cars = ','.join(car_list)
            db.session.add(current_user)    # <<<<<<< 补上这句！
            db.session.commit()
            flash('已成功保存你的偏好车型！', 'success')
            return redirect(url_for('home'))
        else:
            flash('请选择至少一辆喜欢的车型', 'danger')
    return render_template('choose_cars.html', cars=cars)

@app.route("/recommend")
@login_required
def recommend():
    if not current_user.preferred_cars:
        return redirect(url_for('choose_cars'))

    preferred_models = current_user.preferred_cars.split(',')
    recommended_models = recommend_for_user(preferred_models)

    print(f"[DEBUG] 推荐车型: {recommended_models}")

    # 在数据库中寻找名字完全一致的车型，找到一个即可，拼接位list
    recommended_cars = []
    for model in recommended_models:
        car = Car.query.filter_by(name=model).first()
        if car:
            recommended_cars.append(car)
        else:
            print(f"[DEBUG] 没找到车型: {model}")

    # 去重，名字存在的去掉
    uni_car={}
    for car in recommended_cars:
        if car.name not in uni_car:
            uni_car[car.name] = car
        else:
            # 从推荐列表中删除
            recommended_cars.remove(car)

    print(f"[DEBUG] 推荐的车型: {[car.name for car in recommended_cars]}")

    # print(f"[DEBUG] 推荐的车型: {[car.name for car in recommended_cars]}")

    return render_template('recommend.html', cars=recommended_cars)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    # 查询同一车型所有月份销量记录
    sales_records = Car.query.filter_by(name=car.name).order_by(Car.month.asc()).all()
    return render_template('car_detail.html', car=car, sales_records=sales_records)


@app.route('/like_car', methods=['POST'])
@login_required
def like_car():
    car_name = request.json.get('car_name')
    if not car_name:
        return jsonify({"error": "No car_name provided"}), 400

    preferred_list = current_user.preferred_cars.split(',') if current_user.preferred_cars else []

    # 删除（如果存在）
    if car_name in preferred_list:
        preferred_list.remove(car_name)
    else:
        preferred_list.insert(0, car_name)

    # 插入到最前面
    if car_name in preferred_list:
        preferred_list.remove(car_name)  # 先删掉旧位置
    preferred_list.insert(0, car_name)

    # 保持长度，比如最多5辆
    if len(preferred_list) > 10:
        preferred_list = preferred_list[:10]

    current_user.preferred_cars = ','.join(preferred_list)
    db.session.commit()

    return jsonify({"message": "已更新偏好车型", "preferred_cars": preferred_list})

@app.route('/ranking', methods=['GET'])
def ranking():
    month = request.args.get('month')

    # 查询所有有数据的月份列表
    months = db.session.query(Car.month).distinct().order_by(Car.month.desc()).all()
    available_months = [m[0] for m in months if m[0]]  # 去空值

    cars = []
    if month:
        cars = Car.query.filter_by(month=month).order_by(Car.sales.desc()).all()

    return render_template('ranking.html', cars=cars, selected_month=month, available_months=available_months)

# 逻辑回归预测
# from flask import render_template, request
# from models import Car
# import numpy as np
# from scipy.optimize import curve_fit

# @app.route('/forecast', methods=['GET'])
# def forecast():
#     brand = request.args.get('brand')

#     brands = db.session.query(Car.brand).distinct().all()
#     available_brands = [b[0] for b in brands if b[0]]

#     months = []
#     sales = []
#     pred_months = []
#     pred_sales = []

#     if brand:
#         rows = Car.query.filter_by(brand=brand).order_by(Car.month.asc()).all()
#         sales_data = {}
#         for row in rows:
#             if row.month and row.sales is not None:
#                 sales_data[row.month] = sales_data.get(row.month, 0) + row.sales

#         if sales_data:
#             months = sorted(sales_data.keys())
#             sales = [sales_data[m] for m in months]

#             try:
#                 # Logistic函数定义
#                 def logistic(x, L, k, x0):
#                     return L / (1 + np.exp(-k * (x - x0)))

#                 x_data = np.arange(len(months))
#                 y_data = np.array(sales)

#                 # 给初始参数估计
#                 L_init = max(y_data) * 1.5
#                 k_init = 0.1
#                 x0_init = len(x_data) / 2

#                 popt, _ = curve_fit(logistic, x_data, y_data, p0=[L_init, k_init, x0_init], maxfev=10000)

#                 # 预测未来6个月
#                 future_x = np.arange(len(months), len(months) + 3)
#                 pred_sales = logistic(future_x, *popt)

#                 pred_sales = pred_sales.tolist()

#                 # 生成未来月份（真实年月）
#                 last_month = int(months[-1])
#                 pred_months = []
#                 year = last_month // 100
#                 month = last_month % 100
#                 for _ in range(3):
#                     month += 1
#                     if month > 12:
#                         month = 1
#                         year += 1
#                     pred_months.append(f"{year}{month:02d}")

#             except Exception as e:
#                 print("拟合失败:", e)
#                 pred_sales = []
#                 pred_months = []

#     return render_template('forecast.html',
#                            available_brands=available_brands,
#                            selected_brand=brand,
#                            months=months,
#                            sales=sales,
#                            pred_months=pred_months,
#                            pred_sales=pred_sales)

# ARIMA 预测
from flask import render_template, request
from models import Car
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

@app.route('/forecast', methods=['GET'])
def forecast():
    brand = request.args.get('brand')

    brands = db.session.query(Car.brand).distinct().all()
    available_brands = [b[0] for b in brands if b[0]]

    months = []
    sales = []
    pred_months = []
    pred_sales = []
    formula = None

    if brand:
        rows = Car.query.filter_by(brand=brand).order_by(Car.month.asc()).all()
        sales_data = {}
        for row in rows:
            if row.month and row.sales is not None:
                sales_data[row.month] = sales_data.get(row.month, 0) + row.sales

        if sales_data:
            months = sorted(sales_data.keys())
            sales = [sales_data[m] for m in months]

            try:
                # 将销量转成pandas时间序列
                start_year = int(months[0][:4])
                start_month = int(months[0][4:])
                index = pd.date_range(start=f'{start_year}-{start_month:02d}', periods=len(sales), freq='MS')
                ts = pd.Series(sales, index=index)

                # 自动选择ARIMA参数
                model = ARIMA(ts, order=(1,1,1))  # (p,d,q)可以进一步自动调参
                model_fit = model.fit()

                # 预测未来6个月
                forecast = model_fit.forecast(steps=6)

                pred_sales = forecast.tolist()

                # 生成未来月份
                last_month = int(months[-1])
                pred_months = []
                year = last_month // 100
                month = last_month % 100
                for _ in range(6):
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                    pred_months.append(f"{year}{month:02d}")

                formula = f"ARIMA(1,1,1) 模型"

            except Exception as e:
                print("ARIMA拟合失败:", e)
                pred_sales = []
                pred_months = []
                formula = "拟合失败"

    return render_template('forecast.html',
                           available_brands=available_brands,
                           selected_brand=brand,
                           months=months,
                           sales=sales,
                           pred_months=pred_months,
                           pred_sales=pred_sales,
                           formula=formula)

@app.route("/profile")
@login_required
def profile():
    # 用户喜欢的车型名列表
    preferred_names = current_user.preferred_cars.split(',') if current_user.preferred_cars else []
    liked_cars = Car.query.filter(Car.name.in_(preferred_names)).group_by(Car.name).all()
    return render_template('profile.html', user=current_user, cars=liked_cars)

@app.route('/unlike_car', methods=['POST'])
@login_required
def unlike_car():
    car_name = request.json.get('car_name')
    if not car_name:
        return jsonify({"error": "No car_name provided"}), 400

    preferred_list = current_user.preferred_cars.split(',') if current_user.preferred_cars else []

    if car_name in preferred_list:
        preferred_list.remove(car_name)
        current_user.preferred_cars = ','.join(preferred_list)
        db.session.commit()
        return jsonify({"message": "已取消喜欢", "preferred_cars": preferred_list})
    else:
        return jsonify({"error": "该车型不在偏好列表中"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)