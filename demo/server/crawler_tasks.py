import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from demo.celery import app
from concurrent.futures import ThreadPoolExecutor

# 添加随机 User-Agent 池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/607.1.12 EDG/127.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
]

import random

# MIME 类型到扩展名映射
MIME_TYPE_MAP = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
}

def get_extension_from_url(image_url, response):
    parsed = os.path.splitext(os.path.basename(image_url))
    if len(parsed) > 1 and parsed[1].lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
        return parsed[1]

    content_type = response.headers.get('Content-Type')
    if content_type in MIME_TYPE_MAP:
        return MIME_TYPE_MAP[content_type]
    return '.bin'

def download_image(img_info):
    img_url, img_title, folder_path = img_info
    try:
        content_data = requests.get(img_url).content
        ext = get_extension_from_url(img_url, requests.head(img_url))
        with open(f'{folder_path}/{img_title}{ext}', 'wb') as f:
            f.write(content_data)
        print(f"✅ 已保存: {img_title}")
    except Exception as e:
        print(f"❌ 下载失败: {img_title}, 错误: {e}")

def process_page(page_url, folder_path):
    print(f"正在处理页面: {page_url}")
    
    # 每次请求随机选择 User-Agent
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'cookie': 'trenvecookieinforecord=%2C19-35074%2C',
        'host': 'www.netbian.com',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(USER_AGENTS)
    }
    
    rsp = requests.get(page_url, headers=headers, timeout=2)
    
    # 添加随机延迟以避免触发反爬机制
    time.sleep(random.uniform(0.5, 2))
    
    soup = BeautifulSoup(rsp.text, 'html.parser')

    # 提取详情页链接
    links = [urljoin(page_url, a['href']) for a in soup.find_all('a', href=True)]
    detail_links = [link for link in links if '/desk/' in link]

    all_images = []

    for link in detail_links:
        rsp1 = requests.get(link)
        soup1 = BeautifulSoup(rsp1.text, 'html.parser')
        img_tags = soup1.find_all('img', src=True)
        for img in img_tags:
            img_url = img['src']
            img_title = img.get('alt', 'image')
            all_images.append((img_url, img_title, folder_path))

    # 使用线程池并发下载图片
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_image, all_images)

@app.task
def start_crawler_task():
    base_url = 'http://www.netbian.com'

    folder_path = 'photo/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    page_queue = [f'{base_url}/index_{i}.htm' for i in range(2, 10)]
    page_queue.insert(0, base_url)

    for page_url in page_queue:
        process_page(page_url, folder_path)
