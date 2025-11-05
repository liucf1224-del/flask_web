from flask import Flask, jsonify
import asyncio

app = Flask(__name__)


class AsyncUtils:
    """异步工具类，封装可复用的异步方法"""

    @staticmethod
    async def fetch_data(delay: float, data: str):
        """模拟异步IO操作（如数据库查询、HTTP请求）"""
        await asyncio.sleep(delay)
        return f"Processed: {data}"


@app.route("/process/<data>")
async def process_data(data):
    """异步视图函数，调用工具类方法"""
    result = await AsyncUtils.fetch_data(1.0, data)
    return jsonify({"status": "success", "result": result})


if __name__ == "__main__":
    app.run(debug=True)