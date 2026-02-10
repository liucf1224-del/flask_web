import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
from datetime import datetime


class KTVOrderScraper:
    def __init__(self, base_url="https://using.cavca.org"):
        self.base_url = base_url
        self.session = requests.Session()
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': f'{base_url}/vod/qr_code_orders',
            'Connection': 'keep-alive',
        }
        # 从您的curl命令中获取的Cookie
        self.cookies = {
            'cavca_using': 'eyJpdiI6IjFBYzR0VjBVY3E3WnNweTBJcVhhbFE9PSIsInZhbHVlIjoieDlWR0txZEhpVGUwTFBCdGt1Wmt1dTZvSm56UjlpdmI2VmhkQ1BqZTRFbENNY0tRRzZ1NDVhVVNMUjJMMk5RUE51YUNCOGRGVHdWNmtNdllYaTJ5SHc9PSIsIm1hYyI6IjY0NGY2N2FmYjI2YTllZWJjYjkxZGQwMjlmNzU4NjhmYjdiMGViNTQ0NjkzY2VmMGZhNTNhY2U1MjkyMGZlZGUifQ%3D%3D'
        }
        self.all_orders = []

    def fetch_page(self, year=2025, start_date="2025-07-20", end_date="2025-07-20", agent_id=9, page=1):
        """获取单页数据"""
        params = {
            'y': year,
            'start_date': start_date,
            'end_date': end_date,
            'agent_id': agent_id,
            'page': page
        }

        try:
            response = self.session.get(
                f'{self.base_url}/vod/qr_code_orders',
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=30
            )

            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"请求页面时出错: {e}")
            return None

    def parse_table(self, html_content):
        """解析HTML表格数据"""
        soup = BeautifulSoup(html_content, 'html.parser')
        orders = []

        # 查找订单表格
        table = soup.find('table', class_='table-float')
        if not table:
            return orders

        # 找到表格主体
        tbody = table.find('tbody')
        if not tbody:
            return orders

        # 遍历每一行
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 11:  # 确保有足够的列
                order_data = {
                    '订单号': cols[0].get_text(strip=True),
                    '场所名称': cols[1].get_text(strip=True),
                    '工商名称': cols[2].get_text(strip=True),
                    '省市区县': cols[3].get_text(strip=True).replace('\n', ' ').strip(),
                    '设备号': cols[4].get_text(strip=True),
                    '包房号': cols[5].get_text(strip=True),
                    '支付金额': cols[6].get_text(strip=True).replace('￥', '').strip(),
                    '支付方式': cols[7].get_text(strip=True),
                    '支付状态': cols[8].find('label').get_text(strip=True) if cols[8].find('label') else cols[
                        8].get_text(strip=True),
                    '套餐类型': cols[8].find('span', class_='label-success').get_text(strip=True) if cols[8].find(
                        'span', class_='label-success') else '',
                }

                # 提取套餐时间（开始和结束）
                time_labels = cols[9].find_all('label')
                if len(time_labels) >= 2:
                    order_data['套餐开始时间'] = time_labels[0].get('title') or time_labels[0].get_text(strip=True)
                    order_data['套餐结束时间'] = time_labels[1].get('title') or time_labels[1].get_text(strip=True)

                # 关台时间
                order_data['关台时间'] = cols[10].get_text(strip=True)

                orders.append(order_data)

        return orders

    def get_total_pages(self, html_content):
        """获取总页数"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 方法1: 从分页组件获取
        pagination = soup.find('ul', class_='pagination')
        if pagination:
            page_items = pagination.find_all('li', class_='page-item')
            if page_items:
                page_numbers = []
                for item in page_items:
                    a_tag = item.find('a')
                    if a_tag and a_tag.text.isdigit():
                        page_numbers.append(int(a_tag.text))
                if page_numbers:
                    return max(page_numbers)

        # 方法2: 从总数据条数推算（每页25条）
        total_info = soup.find('span', string=lambda x: x and '共计：' in x)
        if total_info:
            text = total_info.get_text(strip=True)
            import re
            match = re.search(r'共计：(\d+)', text)
            if match:
                total_records = int(match.group(1))
                return (total_records + 24) // 25  # 向上取整

        return 1

    def scrape_all_pages(self, year=2025, start_date="2025-07-20", end_date="2025-07-20", agent_id=9):
        """抓取所有页面数据"""
        print(f"开始抓取数据: {start_date} 到 {end_date}")

        # 先获取第一页，确定总页数
        first_page_html = self.fetch_page(year, start_date, end_date, agent_id, 1)
        if not first_page_html:
            print("无法获取第一页数据")
            return

        total_pages = self.get_total_pages(first_page_html)
        print(f"总计 {total_pages} 页需要抓取")

        all_orders = []

        for page in range(1, total_pages + 1):
            print(f"正在抓取第 {page}/{total_pages} 页...")

            if page == 1:
                html_content = first_page_html
            else:
                html_content = self.fetch_page(year, start_date, end_date, agent_id, page)
                time.sleep(1)  # 礼貌性延迟，避免被封

            if html_content:
                orders = self.parse_table(html_content)
                all_orders.extend(orders)
                print(f"第 {page} 页抓取到 {len(orders)} 条记录")
            else:
                print(f"第 {page} 页抓取失败")

            # 每5页保存一次进度
            if page % 5 == 0:
                self.save_progress(all_orders, page)

        self.all_orders = all_orders
        print(f"抓取完成！总计 {len(all_orders)} 条订单记录")
        return all_orders

    def save_to_file(self, data, format='csv', filename=None):
        """保存数据到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ktv_orders_{timestamp}"

        df = pd.DataFrame(data)

        if format.lower() == 'csv':
            filepath = f"{filename}.csv"
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"数据已保存到: {filepath}")

        elif format.lower() == 'excel':
            filepath = f"{filename}.xlsx"
            df.to_excel(filepath, index=False)
            print(f"数据已保存到: {filepath}")

        elif format.lower() == 'json':
            filepath = f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filepath}")

        elif format.lower() == 'txt':
            filepath = f"{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                # 写入表头
                headers = list(data[0].keys()) if data else []
                f.write('\t'.join(headers) + '\n')

                # 写入数据
                for order in data:
                    values = [str(order.get(h, '')) for h in headers]
                    f.write('\t'.join(values) + '\n')
            print(f"数据已保存到: {filepath}")

        return filepath

    def save_progress(self, data, current_page):
        """保存进度"""
        filename = f"progress_page_{current_page}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"进度已保存到: {filename}")

    def scrape_page_range(self, start_page, end_page, year=2025, start_date="2025-07-20", end_date="2025-07-20",
                          agent_id=9):
        """抓取指定页码范围的数据"""
        print(f"开始抓取第 {start_page} 页到第 {end_page} 页的数据")

        all_orders = []

        for page in range(start_page, end_page + 1):
            print(f"正在抓取第 {page}/{end_page} 页...")

            html_content = self.fetch_page(year, start_date, end_date, agent_id, page)

            if html_content:
                orders = self.parse_table(html_content)
                all_orders.extend(orders)
                print(f"第 {page} 页抓取到 {len(orders)} 条记录")
            else:
                print(f"第 {page} 页抓取失败")

            # 添加延迟避免请求过于频繁
            time.sleep(2)

            # 每10页保存一次进度
            if page % 10 == 0:
                self.save_progress(all_orders, page)

        print(f"抓取完成！总计 {len(all_orders)} 条订单记录")
        return all_orders

# 使用示例
def main():
    scraper = KTVOrderScraper()
    # 抓取第1页到第44页的数据
    all_orders = scraper.scrape_page_range(1, 44, year=2025, start_date='2025-07-20', end_date='2025-07-20', agent_id=9)

    if all_orders:
        # 保存所有数据到CSV
        scraper.save_to_file(all_orders, format='csv',
                             filename=f'ktv_orders_pages_1_to_44_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

        print("\n数据预览:")
        for i, order in enumerate(all_orders[:5]):  # 显示前5条
            print(f"{i + 1}. {order}")

    # 设置查询参数
    # params = {
    #     'year': 2025,
    #     'start_date': '2025-07-20',
    #     'end_date': '2025-07-20',
    #     'agent_id': 9
    # }
    #
    # try:
    #     # 抓取所有数据
    #     all_orders = scraper.scrape_all_pages(**params)
    #
    #     if all_orders:
    #         # 保存为CSV（推荐）
    #         scraper.save_to_file(all_orders, format='csv')
    #
    #         # 或者保存为Excel
    #         # scraper.save_to_file(all_orders, format='excel')
    #
    #         # 或者保存为JSON
    #         # scraper.save_to_file(all_orders, format='json')
    #
    #         # 或者保存为TXT
    #         # scraper.save_to_file(all_orders, format='txt')
    #
    #         # 打印前几条数据预览
    #         print("\n数据预览:")
    #         for i, order in enumerate(all_orders[:3]):
    #             print(f"{i + 1}. {order}")
    #
    # except Exception as e:
    #     print(f"抓取过程中出错: {e}")


if __name__ == "__main__":
    main()