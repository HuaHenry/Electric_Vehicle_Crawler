import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
import time
import random
import os
from selenium.webdriver.common.keys import Keys
from msedge.selenium_tools import Edge, EdgeOptions
import requests
import shutil
import json


def get_video_from_url(video_url, save_path):
    response = requests.get(video_url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def get_image_from_url(image_url, save_path):
    response = requests.get(image_url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def get_file_from_url(file_url, save_root):
    file_name = os.path.basename(file_url)
    # 若失败则重试，最大重试次数为5
    if 'mp4' in file_url:
        for _ in range(5):
            try:
                get_video_from_url(
                    file_url,
                    os.path.join(save_root, file_name)
                )
                break
            except:
                print('retry')
    else:
        for _ in range(5):
            try:
                get_image_from_url(
                    file_url,
                    os.path.join(save_root, file_name)
                )
                break
            except:
                print('retry')


med_data = json.load(open('med_data_breast.json'))
us_data_file = 'ultrasoundcases_data.json'
ultrasoundcases_data = json.load(open(us_data_file)) if os.path.exists(us_data_file) else {}
download_root = 'download'
os.makedirs(download_root, exist_ok=True)
for body_part_url, sub_part_info in med_data.items():
    if 'breast-and-axilla' not in body_part_url.lower(): continue
    body_part_name = body_part_url.split('/')[-2]
    os.makedirs(os.path.join(download_root, body_part_name), exist_ok=True)

    if body_part_name not in ultrasoundcases_data: ultrasoundcases_data[body_part_name] = {}
    for sub_url, sub_info in tqdm(sub_part_info.items()):
        sub_name = sub_url.split('/')[-2]
        os.makedirs(os.path.join(download_root, body_part_name, sub_name), exist_ok=True)

        if sub_name not in ultrasoundcases_data[body_part_name]: ultrasoundcases_data[body_part_name][sub_name] = {}
        for subtype_url, subtype_info in tqdm(sub_info.items()):
            subtype_name = subtype_url.split('/')[-2]
            os.makedirs(os.path.join(download_root, body_part_name, sub_name, subtype_name), exist_ok=True)

            if subtype_name not in ultrasoundcases_data[body_part_name][sub_name]: ultrasoundcases_data[body_part_name][sub_name][subtype_name] = {}
            json.dump(ultrasoundcases_data, open(us_data_file, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
            for cases_url, case_info in subtype_info.items():
                cases_name = cases_url.split('/')[-2].split('-')[-1]
                os.makedirs(os.path.join(download_root, body_part_name, sub_name, subtype_name, cases_name), exist_ok=True)

                if cases_name not in ultrasoundcases_data[body_part_name][sub_name][subtype_name]: ultrasoundcases_data[body_part_name][sub_name][subtype_name][cases_name] = {}
                
                caption = case_info['caption']
                case_url = case_info['case_url']

                ultrasoundcases_data[body_part_name][sub_name][subtype_name][cases_name]['caption'] = caption
                if 'case_info' not in ultrasoundcases_data[body_part_name][sub_name][subtype_name][cases_name]:
                    ultrasoundcases_data[body_part_name][sub_name][subtype_name][cases_name]['case_info'] = []
                json.dump(ultrasoundcases_data, open(us_data_file, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                for url, case_caption in case_url.items():
                    file_name = os.path.basename(url)
                    save_path = os.path.join(download_root, body_part_name, sub_name, subtype_name, cases_name)
                    
                    save_file_path = os.path.join(save_path, file_name)

                    ultrasoundcases_data[body_part_name][sub_name][subtype_name][cases_name]['case_info'].append({
                        'ori_file': save_file_path,
                        'url_file': url,
                        'caption': case_caption,
                        'file_type': 'video' if 'mp4' in url else 'image'
                    })
                    json.dump(ultrasoundcases_data, open(us_data_file, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                    if not os.path.exists(save_file_path):
                        get_file_from_url(url, save_path)
                    print(f"Downloaded {save_file_path}")

json.dump(ultrasoundcases_data, open(us_data_file, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
