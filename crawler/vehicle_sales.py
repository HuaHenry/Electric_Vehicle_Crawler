import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


#
# 1.卸载旧版本
# apt purge phantomjs    或者  sudo apt-get autoremove phantomjs
# 2.通过Wget下载phantomjs
# wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
# 3.解压
# tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2
# 4.将phantomjs文件移动到/usr/bin/
# sudo cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin/


# 此函数用于加载网页，并返回无头浏览器全部渲染过的数据，即所见即所得
def get_url(url):
    driver.get(url)  # 加载网页
    driver.implicitly_wait(5)  # 隐式等待5秒钟，智能等待网页加载
    source = driver.page_source  # 获取网页信息
    return source

def get_info(source, debug_url=""):
    soup = BeautifulSoup(source, "lxml")

    # 提取车辆基本信息
    car_info = soup.select('table > tbody > tr > td')
    car_info_ = [i.get_text(strip=True) for i in car_info]

    car_info__ = []
    for i in range(0, len(car_info_), 6):
        car_info_i = car_info_[i:i + 5]
        if len(car_info_i) < 5:
            continue
        price = car_info_i[-1]
        if " - " in price:
            min_price = price.split(" - ")[0]
            max_price = price.split(" - ")[1]
        else:
            min_price = max_price = price
        car_info_i[-1] = min_price
        car_info_i.append(max_price)
        car_info__.append(car_info_i)

    # 提取跳转链接（参数页链接）
    option_link = soup.select('table > tbody > tr > td > div > a')
    option_link = [i.get('href') for i in option_link if i.get('href') is not None]
    option_link = [option_link[i] for i in range(2, len(option_link), 6)]

    # 对齐长度，避免拼接错误
    min_len = min(len(car_info__), len(option_link))
    if min_len == 0:
        print(f"[警告] 页面无有效数据: {debug_url}")
        return np.array([])

    if len(car_info__) != len(option_link):
        print(f"[提示] 数据长度不一致（已对齐）: {debug_url}")
        print(f"车辆信息数量: {len(car_info__)}, 参数链接数量: {len(option_link)}")

    car_info__ = car_info__[:min_len]
    option_link = option_link[:min_len]

    all_info = np.c_[np.array(car_info__), np.array(option_link)]
    return all_info


def links(month):
    # https://xl.16888.com/ev-201903-201903-1.html
    # https://xl.16888.com/ev-202212-202212-1.html
    links = []
    month_ = [i + j
              for i in ['2021', '2022','2023','2024']
              for j in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
              if i + j <= month]
    for i in month_:
        page_num = get_url('https://xl.16888.com/ev-%s-%s-1.html' % (i, i))
        soup = BeautifulSoup(page_num, "lxml")
        page_num_ = re.findall(r"\d+", soup.select('div.xl-data-page-r > div > span')[0].get_text())[0]
        # print(page_num_)
        if int(page_num_) % 50 == 0:
            page_number = int(int(page_num_) / 50)
        else:
            page_number = int(int(page_num_) / 50) + 1
        for j in range(page_number):
            links.append('https://xl.16888.com/ev-%s-%s-%s.html' % (i, i, j + 1))
    return links


if __name__ == '__main__':
    driver = webdriver.PhantomJS(
        executable_path="../phantomjs-2.1.1-macosx/bin/phantomjs"
    )  # 加载无头浏览器，具体查看selenium文档，可换成火狐或者谷歌浏览器
    month = '202212'
    url = links(month)
    all_info_ = pd.DataFrame()
    for i in tqdm(url):
        print(i)
        source = get_url(i)
        all_info = get_info(source, debug_url=i)
        if all_info.size == 0:
            continue  # 没有有效数据，跳过
        date_month = i[24:30]
        date = np.array([date_month for i in range(len(all_info))])
        all_info = np.c_[all_info, date]
        all_info = pd.DataFrame(all_info)
        all_info_ = pd.concat([all_info_, all_info])
    print(all_info_)
    # all_info.columns = ["序号","车型","销量","厂商","最低售价","最高售价","参数","日期"] # csv文件没有表头，这里只是参考一下
    all_info_.to_csv("2101_2412新能源汽车总体销量数据.csv")
    print("Finished")
