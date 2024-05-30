import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
import time
import random

from selenium.webdriver.common.keys import Keys
from msedge.selenium_tools import Edge, EdgeOptions
# 设置User-Agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
options = EdgeOptions()
options.use_chromium = True
# options.add_argument("headless")  # 静默模式
options.add_argument("disable-gpu")


options.binary_location = r"C:/Program Files (x86)/Microsoft/EdgeCore/125.0.2535.67/msedge.exe"

driver = Edge(options=options, executable_path=r"E:/personal_project/Electric_Vehicle_Crawler/edgedriver_win64/msedgedriver.exe")

def get_url(url):
    driver.get(url)  # 加载网页
    # 随机延时，防止被反爬虫机制检测
    time.sleep(random.uniform(3, 7))
    # 等待加载完毕
    driver.implicitly_wait(5)
    # 获取网页信息
    source = driver.page_source
    # driver.quit()
    return source


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

def get_case_page_url(
        soup,
        web_url="https://www.ultrasoundcases.info"
):
    case_page = {}
    for case in soup.find_all("div", {"class": "candidate half-grid"}):
        case_page[web_url + case.find("a", {"class": "blank"}).get("href")] = case.find("span").get_text()
    return case_page

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

json_path = "med_data.json"
# med_data = {} # {body_part: {sub_part: {subtype: {case_url: case_name}}}}
med_data = json.load(open(json_path, "r", encoding="utf-8"))
json.dump(med_data, open(json_path, "w", encoding="utf-8"))
body_part_url = get_body_part_url(BeautifulSoup(get_url("https://www.ultrasoundcases.info/cases")))
for body_part, sub_part in tqdm(body_part_url.items()):
    if body_part not in med_data:
        med_data[body_part] = {}
    print(body_part)
    for sub in tqdm(sub_part):
        # if 'breast' not in sub.lower(): continue
        print(f'Loading subpart {sub}')
        subtype_page = get_subtype_page_url(BeautifulSoup(get_url(sub)))
        if sub not in med_data[body_part]:
            med_data[body_part][sub] = {}
        json.dump(med_data, open(json_path, "w", encoding="utf-8"))
        for subtype, subtype_name in tqdm(subtype_page.items()):
            print(f'Loading subtype {subtype}')
            case_page = get_case_page_url(BeautifulSoup(get_url(subtype)))
            if subtype not in med_data[body_part][sub]:
                med_data[body_part][sub][subtype] = {}
            json.dump(med_data, open(json_path, "w", encoding="utf-8"))
            for case, case_name in tqdm(case_page.items()):
                print(f'Loading case {case}')
                if case in med_data[body_part][sub][subtype]: continue
                caption, case_url = get_case_url(BeautifulSoup(get_url(case)))
                med_data[body_part][sub][subtype][case] = {"case_name": case_name, "caption": caption, "case_url": case_url}
                json.dump(med_data, open(json_path, "w", encoding="utf-8"))
                time.sleep(random.uniform(3, 7))
                print(f'Loaded case {case}')
            print(f'Loaded subtype {subtype}')
