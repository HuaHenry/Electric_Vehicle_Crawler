import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
import time
import random

# 设置Chrome选项以避免被检测为爬虫
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--incognito")

# 设置User-Agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f'user-agent={user_agent}')



def get_url(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)  # 加载网页
    # 随机延时，防止被反爬虫机制检测
    time.sleep(random.uniform(3, 7))
    # 等待加载完毕
    driver.implicitly_wait(10)
    # 获取网页信息
    source = driver.page_source
    driver.quit()
    return source
    
# https://www.ultrasoundcases.info/cases
html_url = "https://www.ultrasoundcases.info/cases"
html = get_url(html_url)
soup = BeautifulSoup(html, "html.parser")

from pprint import pprint

def get_body_part_url(
        soup,
        web_url="https://www.ultrasoundcases.info"
):
    body_part_url = {} 
    for body_part in soup.find_all("a", {"data-type": "cat"}):
        cat_url = body_part.get("href")
        sub_url = []
        for sub_part in body_part.find_next("ul").find_all("a", {"data-type": "subcat"}):
            sub_url.append(web_url + sub_part.get("href"))
        body_part_url[web_url + cat_url] = sub_url
    return body_part_url

def get_subtype_page_url(
        soup,
        web_url="https://www.ultrasoundcases.info"
):
    subtype_page = {}
    for subtype in soup.find_all("div", {"data-type": "subsubcat"}):
        subtype_page[web_url + subtype.get("href")] = subtype.get_text()
    return subtype_page

def get_subtype_page_url(
        soup,
        web_url="https://www.ultrasoundcases.info"
):
    subtype_page = {}
    for subtype in soup.find_all("div", {"data-type": "subsubcat"}):
        subtype_page[web_url + subtype.get("href")] = subtype.get_text()
    return subtype_page

def get_case_url(
        soup,
        web_url="https://www.ultrasoundcases.info"
):
    case_url = {}
    # img
    for case in soup.find_all("a", {"data-fancybox": "gallery"}):
        case_url[web_url + case.get("href")] = case.get("data-caption")
    # video: <source src="https://www.ultrasoundcases.info/clients/ultrasoundcases/videos/55092-Mijn_Film_1.mp4" type="video/mp4">
    for case in soup.find_all("source", {"type": "video/mp4"}):
        case_url[case.get("src")] = case.get("src")
    # case caption: <div class="info">Nearly isoechoic focal nodular hyperplasia (FNH)</div>
    case_caption = soup.find("div", {"class": "info"})
    caption = case_caption.get_text() if case_caption else None
    return caption, case_url

# soup = BeautifulSoup(get_url("https://www.ultrasoundcases.info/focal-nodular-hyperplasia-6893/"))
# get_case_url(soup)

import json
from tqdm import tqdm
med_data = {} # {body_part: {sub_part: {subtype: {case_url: case_name}}}}
json.dump(med_data, open("med_data.json", "w", encoding="utf-8"))
body_part_url = get_body_part_url(soup)
for body_part, sub_part in tqdm(body_part_url.items()):
    med_data[body_part] = {}
    print(body_part)
    for sub in tqdm(sub_part):
        print(f'Loading {sub}')
        subtype_page = get_subtype_page_url(BeautifulSoup(get_url(sub)))
        med_data[body_part][sub] = {}
        for subtype, subtype_name in tqdm(subtype_page.items()):
            # med_data[body_part][sub][subtype_name] = get_case_url(BeautifulSoup(get_url(subtype)))
            caption, case_url = get_case_url(BeautifulSoup(get_url(subtype)))
            med_data[body_part][sub][subtype_name] = {"caption": caption, "case_url": case_url}
            json.dump(med_data, open("med_data.json", "w", encoding="utf-8"))
