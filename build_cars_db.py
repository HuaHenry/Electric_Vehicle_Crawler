# build_cars_db.py
import pandas as pd
from app import app
from models import db, Car

def import_car_data(csv_path):
    data = pd.read_csv(csv_path)
    # 确保列名正确
    assert all(col in data.columns for col in ['月份', '车型', '销量', '厂商', '售价区间', '车型链接', '图片链接'])

    with app.app_context():
        for _, row in data.iterrows():
            min_p, max_p = parse_price_range(row['售价区间'])
            # 图片
            img_url = row['图片链接']
            if pd.isna(img_url) or img_url == '':
                print("图片链接为空，使用默认图片")
                img_url = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxEPDw4OEA0PDQ4NDQ8NDw0NDQ8PDw0OFhEWFhURFRUYHSggGBolGxUVITEhJSkrLi4uFx8zODMsNygtLisBCgoKBQUFDgUFDisZExkrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIALcBEwMBIgACEQEDEQH/xAAaAAEBAQEBAQEAAAAAAAAAAAAAAQMCBAcF/8QAMxABAQABAgUCBQIEBgMAAAAAAAECAxESITFBUXGRBCIyYYGhsRNSYsEzkpPR4fAUI1P/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8A+zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoIKAgoCCgIKAgoCCgIKgAAAAAAAAAAAAAAAAAAAACooAAAAAsxt7e7SacnWWgyG8vLp+OjHg/H4BB1cPHP2S4Xry9wQAAAEAAAAAAAAAAAAAAAAAAAAVFACfo9HDJOUBzNKf9rrCbe6wx7+oF6wp3/Bf+QeX4jLnt4jnHWynff1c53e2+aunp3Lp7g1x153m3o0xzl7z0vJnPhvv+jjU0LPvAenhn8rDLrfDLHOzpa0mv5koKLlty2m2/7ICAAAAAAAAAAAAAAAAAAAAAoDfSy3npyYO9LLa+oNsehO5j39SdaB3Z62W0vs0nd5/ib0n5oMMZvZPL3447TaPHofVHtBnrZbR1hvtN+rPW53GflsDyfE4bXftf3ZSdvPJ6Pi+k9WWhOe/bGbg0z6+kkRJ+/NQQAAAAAAAAAAAAAAAAAAABUUAAG+GW/PzI6nWsdG89vMbd/wAAnn1eTWy3yvs9PExzxw8zH8gxle3S1JlPv3jy/wALf6cpl6VzcbO1n3B7MZd7v07OrdudeOa+Xlzlnb1u4OtbU4r9uzrCfLf6rt+O7F6MptwzxN/zQQAEAAAAAAAAAAAAAAAAAAAAVAFAAl25xplnPO/2kjNALz+361JhJ2ns6ATaeI6mVnf35uVBbteuM9Zyc3Sl6ZbfaqgGOjd5436xbd7b5p+nokBQAQAAAAAAAAAAAAAAAAAAAAAAEzy2m+1u3jqCjzafxe+94Mtt/l2m++Pl3/5HOyYZZbXa7bQGwz/ibY73Gz+mc6zy+Lk645zfl9HcHoGM+Jn8mp/kNTWsy4ZhcrJLysgNh58fiMrvtpW7Xa/NjyrrHXvFMbp3Hi32tsoNhnlqbZY47fVMrv42NfU4ZLtvvlMfcGgAAAAAAAAAAAAAAAAAAAAAAADjVm+Nm1u822l2rsB+bMbM+tm2G3+LOXPpv/Z3Zvjnnx3HLK7zHHU295HMs4tTnhP/AGZfVp3K+7nXs4b82neXbTsvvuD27ZYycMue/Xiz6e7DX1M7lhLhJteLbjnOR6dXWmElvfpJ1t8Rjjp5WZ55T5ssbJj/AC4+PUHc1NT/AOc/1Iy1Mrx5c+C3DGcpxWc70XT+JxmnPm+aYdO++3RzNXbLfK8OWWljz4d9rz7Ax/hznJhMpv8AVl9c/Hdtp8Muljjvtjcvqll32ZZ5zrvp5/fLSzxv6NprTLPS8zfebXacvuDr4r/E0/m4OWfzcv7pnpcXK6++1l6YdYsk1NS2zfHTx4ec5XK1PjdHGaedmGMsnWSeQb6eGUvPUuU8XHGfs0THpPRQAAAAAAAAAAAAAAAAAAAAAAAAJP8AcoAbfoACbTxPZdu/fyABZ+gAFm/K84AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/Z'
            car = Car(
                name=row['车型'],
                brand=row['厂商'],
                min_price=min_p,
                max_price=max_p,
                month=str(row['月份']),
                url=row['车型链接'],
                image_url=img_url,
                sales=int(row['销量'])
            )
            db.session.add(car)
        db.session.commit()

def parse_price_range(price_range):
    # peice_range的格式：xxx - xxx
    # 首先分成 - 左右两部分
    price_range = price_range.split('-')
    # 然后取出左右两部分的数字，去除首尾空格
    min_price = price_range[0].strip()
    max_price = price_range[1].strip()
    # print(min_price, max_price)
    return min_price, max_price

def parse_sales(sales_str):
    try:
        return int(sales_str.replace(',', '').strip())
    except:
        return None

if __name__ == '__main__':
    # 首先删除数据库这一张表的所有数据
    import_car_data('crawler/新能源汽车销量_202301_202312.csv')
    print("✅ 车辆数据导入完成")