#!/usr/bin/env python3
import socket
import json
import sys
import time


def send_udp_message(host, port, message):
    print(f"尝试发送到 {host}:{port}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)

            # 设置超时更短，便于调试
            sock.settimeout(2)

            if isinstance(message, dict):
                message = json.dumps(message)

            print(f"发送的消息: {message}")

            # 发送消息
            sock.sendto(message.encode('utf-8'), (host, port))
            print("消息已发送")

            # 等待响应
            try:
                response, addr = sock.recvfrom(1024)
                print(f"收到来自 {addr} 的响应: {response.decode('utf-8')}")
                return response.decode('utf-8')
            except socket.timeout:
                print("发送成功，但未收到响应（可能是正常的）")
                return None

    except Exception as e:
        print(f"发送失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    HOST = "36.111.156.180"  # 你的服务器IP
    PORT = 2349  # 注意是2349，不是2348

    json_message = {"account": "6256595"}

    print("开始UDP测试...")
    result = send_udp_message(HOST, PORT, json_message)
    print(f"测试完成，结果: {result}")