# # -*-coding:utf-8 -*-
# '''
# @File    :   crawler.py
# @Modify  :   2025/04/29 00:52:30
# @Author  :   Zhouqi Hua 
# @Version :   1.0
# @Desc    :   超级爬虫代码，包含图片
# '''

# import time
# import pandas as pd
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from urllib.parse import urljoin

# # 启动Chrome（无头模式）
# options = webdriver.ChromeOptions()
# options.add_argument('--headless=new')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
# driver = webdriver.Chrome(options=options)

# # 要爬取的年月，比如 '202212'
# TARGET_MONTH = '202212'
# BASE_URL = f"https://xl.16888.com/ev-{TARGET_MONTH}-{TARGET_MONTH}-1.html"

# # 最终保存的数据
# data_list = []

# def get_html(url):
#     driver.get(url)
#     time.sleep(2)
#     return driver.page_source

# def get_model_info(page_source):
#     soup = BeautifulSoup(page_source, "lxml")
#     table_rows = soup.select('table.xl-table-def tr')[1:]  # 第一行是表头，跳过
#     for row in table_rows:
#         cols = row.find_all('td')
#         if len(cols) < 6:
#             continue
#         # 排名不用
#         model_name = cols[1].text.strip()
#         model_link = urljoin("https://xl.16888.com", cols[1].find('a')['href'])
#         sales = cols[2].text.strip()
#         factory = cols[3].text.strip()
#         price = cols[4].text.strip()
        
#         # 去详情页爬取图片
#         model_image_url = get_model_image(model_link)
        
#         data_list.append({
#             '车型': model_name,
#             '销量': sales,
#             '厂商': factory,
#             '售价区间': price,
#             '车型链接': model_link,
#             '图片链接': model_image_url
#         })

# def get_model_image(detail_url):
#     # print(f"抓取图片：{detail_url}")
#     # 提取最后两个斜杠之间的部分
#     detail_url = detail_url.split('/')[-2]

#     if not detail_url.startswith('http'):
#         full_url = urljoin("https://www.16888.com", detail_url)
#     else:
#         full_url = detail_url
#     try:
#         driver.get(full_url)
#         time.sleep(1)
#         soup = BeautifulSoup(driver.page_source, 'lxml')

#         # 只找 cars_info 区域下面的图片
#         cars_info = soup.select_one('div.cars_info div.cars_show div.imgbox img')
#         if cars_info:
#             img_src = cars_info.get('src')
#             if img_src:
#                 if img_src.startswith('//'):
#                     img_src = 'https:' + img_src
#                 elif img_src.startswith('/'):
#                     img_src = urljoin('https://www.16888.com', img_src)
#                 return img_src
#             else:
#                 print(f"[警告] {full_url} 找到img但没有src")
#         else:
#             print(f"[警告] {full_url} 没有找到 cars_info 区域的图片")
#     except Exception as e:
#         print(f"[图片抓取失败] {full_url}: {e}")
#     return ""

# def get_total_pages(page_source):
#     soup = BeautifulSoup(page_source, 'lxml')
#     page_links = soup.select('div.xl-data-pageing a.num')
#     return len(page_links)

# def run():
#     first_page_html = get_html(BASE_URL)
#     total_pages = get_total_pages(first_page_html)
#     print(f"总页数：{total_pages}")
    
#     # 先处理首页
#     get_model_info(first_page_html)
    
#     # 再处理后续页
#     for page in range(2, total_pages + 1):
#         next_url = f"https://xl.16888.com/ev-{TARGET_MONTH}-{TARGET_MONTH}-{page}.html"
#         print(f"抓取：{next_url}")
#         html = get_html(next_url)
#         get_model_info(html)

#     # 保存数据
#     df = pd.DataFrame(data_list)
#     df.to_csv(f"新能源汽车销量_{TARGET_MONTH}.csv", index=False, encoding='utf-8-sig')
#     print("✅ 已保存 CSV 文件！")

# if __name__ == '__main__':
#     run()
#     driver.quit()

# -*-coding:utf-8 -*-
'''
@File    :   crawler.py
@Modify  :   2025/04/29
@Author  :   Zhouqi Hua 
@Version :   2.0
@Desc    :   超级爬虫代码，支持多年月，包含车型图片
'''

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin

# 启动Chrome（无头模式）
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# 配置：起始年月，结束年月（包含）
START_MONTH = '202301'
END_MONTH = '202312'

# 最终保存的数据
data_list = []

def get_html(url):
    driver.get(url)
    time.sleep(2)
    return driver.page_source

def get_model_info(page_source, month):
    soup = BeautifulSoup(page_source, "lxml")
    table_rows = soup.select('table.xl-table-def tr')[1:]  # 第一行是表头，跳过
    for row in table_rows:
        cols = row.find_all('td')
        if len(cols) < 6:
            continue
        model_name = cols[1].text.strip()
        model_link = urljoin("https://xl.16888.com", cols[1].find('a')['href'])
        sales = cols[2].text.strip()
        factory = cols[3].text.strip()
        price = cols[4].text.strip()
        
        # 去详情页爬取图片
        model_image_url = get_model_image(model_link)
        
        data_list.append({
            '月份': month,
            '车型': model_name,
            '销量': sales,
            '厂商': factory,
            '售价区间': price,
            '车型链接': model_link,
            '图片链接': model_image_url
        })

def get_model_image(detail_url):
    # 从类似 https://xl.16888.com/s/123456/ 提取 123456
    try:
        model_id = detail_url.strip('/').split('/')[-1]
        full_url = urljoin("https://www.16888.com", model_id + "/")
    except Exception as e:
        print(f"[构建车型URL失败] {detail_url}: {e}")
        return ""

    try:
        driver.get(full_url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # 找 cars_info 区域的图片
        cars_info_img = soup.select_one('div.cars_info div.cars_show div.imgbox img')
        if cars_info_img:
            img_src = cars_info_img.get('src')
            if img_src:
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = urljoin('https://www.16888.com', img_src)
                return img_src
    except Exception as e:
        print(f"[图片抓取失败] {full_url}: {e}")
    return ""

def get_total_pages(page_source):
    soup = BeautifulSoup(page_source, 'lxml')
    page_links = soup.select('div.xl-data-pageing a.num')
    return len(page_links) if page_links else 1

def month_range(start, end):
    """生成从 start 到 end 的年月列表"""
    start_year = int(start[:4])
    start_month = int(start[4:])
    end_year = int(end[:4])
    end_month = int(end[4:])
    months = []
    year, month = start_year, start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        months.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months

def run():
    all_months = month_range(START_MONTH, END_MONTH)
    print(f"需要爬取的月份：{all_months}")

    for month in all_months:
        print(f"\n==== 开始爬取 {month} ====")
        BASE_URL = f"https://xl.16888.com/ev-{month}-{month}-1.html"
        first_page_html = get_html(BASE_URL)
        total_pages = get_total_pages(first_page_html)
        print(f"{month} 总页数：{total_pages}")
        
        # 先处理首页
        get_model_info(first_page_html, month)
        
        # 后续页
        for page in range(2, total_pages + 1):
            next_url = f"https://xl.16888.com/ev-{month}-{month}-{page}.html"
            print(f"抓取：{next_url}")
            html = get_html(next_url)
            get_model_info(html, month)

    # 保存数据
    df = pd.DataFrame(data_list)
    df.to_csv(f"新能源汽车销量_{START_MONTH}_{END_MONTH}.csv", index=False, encoding='utf-8-sig')
    print(f"\n✅ 全部完成，已保存 CSV：新能源汽车销量_{START_MONTH}_{END_MONTH}.csv")

if __name__ == '__main__':
    run()
    driver.quit()