import os.path
import re
import requests

# 创建图片存储目录
if not os.path.exists('photo/'):
    os.mkdir('photo/')

# 更新后的 headers（匹配浏览器请求）
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'connection': 'keep-alive',
    'cookie': 'trenvecookieinforecord=%2C19-35074%2C',
    'host': 'www.netbian.com',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}

def fetch_and_download_images():
    url = 'http://www.netbian.com'
    
    # 发起请求
    rsp = requests.get(url, headers=headers)
    rsp.encoding = rsp.apparent_encoding

    # 提取详情页链接
    url_list = re.findall('<a href="(.*?)"title="(.*?)" target="_blank"><img src=".*?" alt=".*?" />', rsp.text)

    for index in url_list:
        url_lis = index[0]
        title = index[1]
        new_url = url + url_lis

        # 请求详情页
        rsp1 = requests.get(new_url)
        rsp1.encoding = rsp1.apparent_encoding

        # 提取图片链接
        img_list = re.findall('<a href=".*?" target="_blank"><img src="(.*?)" alt="(.*?)" title=".*?"></a>', rsp1.text)

        for img in img_list:
            img_url = img[0]
            img_title = img[1].strip()  # 去除前后空格

            # 下载图片
            content_data = requests.get(img_url).content

            with open(f'photo/{img_title}.jpg', 'wb') as f:
                f.write(content_data)
                print(f'***************正在爬取{title}中****************')


# 主函数入口
if __name__ == "__main__":
    fetch_and_download_images()
