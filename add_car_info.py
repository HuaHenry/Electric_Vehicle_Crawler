import random
from app import app, db
from models import Car

sizes = ['小型车', '紧凑型SUV', '中型轿车', '中大型SUV', '大型车']
battery_types = ['三元锂电池', '磷酸铁锂电池', '固态电池']
autopilot_levels = ['L2', 'L2+', 'L3', 'L4']

with app.app_context():
    # 按车型名聚合
    cars = Car.query.all()
    car_groups = {}
    for car in cars:
        car_groups.setdefault(car.name, []).append(car)

    for name, group in car_groups.items():
        rand_size = random.choice(sizes)
        rand_battery = random.choice(battery_types)
        rand_range = random.randint(350, 750)
        rand_autopilot = random.choice(autopilot_levels)

        for car in group:
            car.size = rand_size
            car.battery_type = rand_battery
            car.range_km = rand_range
            car.autopilot_level = rand_autopilot
            db.session.add(car)

    db.session.commit()
    print(f"已填充 {len(car_groups)} 个车型的静态信息")