import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# 此函数用于加载网页，并返回无头浏览器全部渲染过的数据，即所见即所得
def get_url(url):
    driver.get(url)  # 加载网页
    driver.implicitly_wait(5)  # 隐式等待5秒钟，智能等待网页加载
    source = driver.page_source  # 获取网页信息
    return source

if __name__ == '__main__':
    driver = webdriver.Chrome(options=chrome_options)
    html_url = "https://www.ultrasoundcases.info/benign-cysts-with-non-mass-lesions-1032/"
    html = get_url(html_url)  # 获取网页信息
    soup = BeautifulSoup(html, "html.parser")  # 使用BeautifulSoup解析网页
    # 保存html信息
    with open("ultrasoundcases_benign-lesions_benign-cysts-with-non-mass-lesions_1032.html", "w") as f:
        f.write(soup.prettify())
