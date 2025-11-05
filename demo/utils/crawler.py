import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# MIME 类型到文件扩展名的映射
MIME_TYPE_MAP = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/bmp': '.bmp',
    'image/svg+xml': '.svg',
}
# 固定 token（用于测试）
FIXED_TOKEN = "5D13061A513AEAA3EC00441AA08F83FE"

def fetch_links(url):
    """获取页面中所有的链接"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取所有 a 标签的 href 属性
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

    # 过滤出包含 '/mobileViewLook/' 的链接（即壁纸详情页）
    wallpaper_links = [link for link in links if '/mobileViewLook/' in link]

    return wallpaper_links


def get_extension_from_url(image_url, response):
    """根据 URL 或响应头推断文件扩展名"""
    parsed = os.path.splitext(os.path.basename(image_url))
    if len(parsed) > 1 and parsed[1].lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
        return parsed[1]

    content_type = response.headers.get('Content-Type')
    if content_type in MIME_TYPE_MAP:
        return MIME_TYPE_MAP[content_type]
    return '.bin'

def login_and_get_token():
    """手动注入 Cookie 并提取 token"""
    session = requests.Session()

    # 手动设置已登录的 Cookie（从浏览器开发者工具复制）
    cookie_str = 'askId=ack%3A_17503919382262692978560235939; downEdit=true; _ga=GA1.1.1053425145.1750412777; Hm_lvt_3c3619543a455fffe6917f75aba0e02b=1750391924,1750927093; HMACCOUNT=BDCDD59EE55FAC7F; isWebsiteLog=ok; cropperHint=ok; isShowElNotice=ok; userData=%7B%22code%22%3A%221938424998733676546%22%2C%22userName%22%3A%22%E4%BD%99%E6%B8%A9%22%2C%22userImg%22%3A%2217162560999837056%22%2C%22token%22%3A%225D13061A513AEAA3EC00441AA08F83FE%22%7D; Hm_lpvt_3c3619543a455fffe6917f75aba0e02b=1750991589; _ga_XT96CDMYZB=GS2.1.s1750986920$o3$g1$t1750991589$j59$l0$h0'

    # 将 Cookie 字符串解析为字典
    cookies = {}
    for item in cookie_str.split('; '):
        key, value = item.split('=', 1)
        cookies[key] = value

    session.cookies.update(cookies)

    # 从 userData 中提取 token
    import urllib.parse
    import json

    user_data_str = urllib.parse.unquote(cookies['userData'])
    user_data = json.loads(user_data_str)
    token = user_data.get('token')

    if not token:
        raise Exception("未在 userData 中找到 token")

    return session, token



def extract_slider_data(session, detail_url, token):
    """模拟滑块验证流程并提取 data 参数"""
    base_api_url = 'https://haowallpaper.com'

    # 完整 headers（从 curl 命令复制而来）
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': detail_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'cache-control': 'no-cache',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'token': FIXED_TOKEN,
        'Cookie': '; '.join([f"{k}={v}" for k, v in session.cookies.get_dict().items()])
    }

    # Step 1: 获取缩略图信息
    thumbnail_url = f'{base_api_url}/link/pc/public/slider'
    response_thumbnail = session.get(thumbnail_url, headers=headers)

    if response_thumbnail.status_code != 200:
        print(f"❌ 缩略图接口返回状态码: {response_thumbnail.status_code}")
        print(f"响应内容前200字符: {response_thumbnail.text[:200]}")
        raise Exception("缩略图接口请求失败")

    content_type = response_thumbnail.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        print(f"❌ 返回非 JSON 内容，Content-Type: {content_type}")
        print(f"响应内容前200字符: {response_thumbnail.text[:200]}")
        raise Exception("缩略图接口返回非 JSON 数据")

    data = response_thumbnail.json().get('data')
    if not data:
        raise Exception("未在响应中找到 data 参数")

    # Step 2: 验证数据
    validate_url = f'{base_api_url}/link/pc/public/slider/validate?data={data}'
    validate_headers = headers.copy()
    validate_headers['Origin'] = 'https://haowallpaper.com'
    response_validate = session.post(validate_url, headers=validate_headers)

    if response_validate.status_code != 200:
        print(f"❌ 验证接口返回状态码: {response_validate.status_code}")
        print(f"响应内容前200字符: {response_validate.text[:200]}")
        raise Exception("验证接口请求失败")

    return data


def get_complete_image_url(session, data, detail_url, token):
    """获取完整的图片URL"""
    base_api_url = 'https://haowallpaper.com'
    complete_url = f'{base_api_url}/link/common/file/getCompleteUrl?data={data}'

    complete_headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': detail_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'cache-control': 'no-cache',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'token': FIXED_TOKEN,
        'Cookie': '; '.join([f"{k}={v}" for k, v in session.cookies.get_dict().items()])
    }

    response_complete = session.post(complete_url, headers=complete_headers)
    if response_complete.status_code != 200:
        raise Exception("获取完整图片URL失败")

    full_image_url = response_complete.json().get('url')
    if not full_image_url:
        raise Exception("未在响应中找到完整图片URL")

    return full_image_url


def download_image(image_url, folder_path='images'):
    """下载单张图片并保存到指定文件夹，并自动补全扩展名"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        file_name_base = os.path.splitext(os.path.basename(image_url))[0]
        ext = get_extension_from_url(image_url, response)
        file_name = os.path.join(folder_path, f"{file_name_base}{ext}")

        with open(file_name, 'wb') as out_file:
            for chunk in response.iter_content(1024):
                out_file.write(chunk)
        print(f"✅ 已下载: {file_name}")
    except Exception as e:
        print(f"❌ 下载失败: {image_url}, 错误: {e}")


def process_detail_page(session, detail_url, token):
    """处理详情页，依次调用 API 并下载图片"""
    try:
        data = extract_slider_data(session, detail_url, token)
        full_image_url = get_complete_image_url(session, data, detail_url, token)
        download_image(full_image_url, folder_path='downloaded_images')
    except Exception as e:
        print(f"❌ 处理详情页失败: {detail_url}, 错误: {e}")



def crawl_and_process_pages(list_url):
    """爬取列表页中的所有详情页链接并逐一处理"""
    detail_links = fetch_links(list_url)
    print(f"共找到 {len(detail_links)} 个详情页链接")

    for link in detail_links:
        print(f"正在处理详情页: {link}")
        process_detail_page(link)

if __name__ == "__main__":
    list_page_url = "https://haowallpaper.com/mobileView?isSel=true&page=1"

    # 初始化会话并登录一次获取 session 和 token
    session, token = login_and_get_token()

    # 获取详情页链接
    detail_links = fetch_links(list_page_url)
    print(f"共找到 {len(detail_links)} 个详情页链接")

    for link in detail_links:
        print(f"正在处理详情页: {link}")
        try:
            data = extract_slider_data(session, link, token)
            full_image_url = get_complete_image_url(session, data, link, token)
            download_image(full_image_url, folder_path='downloaded_images')
        except Exception as e:
            print(f"❌ 处理详情页失败: {link}, 错误: {e}")
