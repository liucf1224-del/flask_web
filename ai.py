# import requests
# #
# # url = "http://110.40.188.181:11434/api/generate"
# # data = {
# #     "model": "deepseek-r1:7b",
# #     "prompt": "Hello, how can I help you today?"
# # }
# #
# # try:
# #     response = requests.post(url, json=data, timeout=10,verify= False)
# #     print(response.status_code)
# #     print(response.json())
# # except requests.exceptions.ConnectionError as e:
# #     print("连接失败:", e)
# # except requests.exceptions.Timeout as e:
# #     print("请求超时:", e)
# # except Exception as e:
# #     print("发生其他错误:", e)


# import requests
#
# url = "http://110.40.188.181:11434/api/generate"
# data = {
#     "model": "deepseek-r1:7b",
#     "prompt": "你好，你是谁?",
#     "stream": True  # 启用流式响应
# }
#
# try:
#     with requests.post(url, json=data, stream=True) as response:
#         response.raise_for_status()  # 检查 HTTP 错误
#         for line in response.iter_lines():
#             if line:
#                 print(line.decode('utf-8'))  # 输出每一行的原始字节流
# except requests.exceptions.RequestException as e:
#     print("请求失败:", e)



import requests

url = "http://110.40.188.181:11434/api/chat"

data = {
    "model": "deepseek-r1:7b",
    "messages": [
        {"role": "system", "content": "你是 Python 开发助手"},
        {"role": "user", "content": "帮我写一个爬虫脚本"},
    ],
    "stream": True
}

with requests.post(url, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
