import asyncio
import random
import time

# "协程"（coroutine)
async def process_item(item):
    print(f"处理中：{item}")
    # async 定义的函数变成了协程
    process_time = random.uniform(0.5, 2.0)
    # time.sleep() 换成 asyncio.sleep()
    await asyncio.sleep(process_time)  # await 等待异步操作完成
    return f"处理完成：{item}，耗时 {process_time:.2f} 秒"


async def process_all_items():
    items = ["任务A", "任务B", "任务C", "任务D"] # 模拟数据 理论上跑100-500 的4核8g这种
    # 创建任务列表
    tasks = [
        asyncio.create_task(process_item(item))
        for item in items
    ]
    print("开始处理")
    results = await asyncio.gather(*tasks) # 返回结果以最后的结果为准 其实可以完成的时候自己去修改对应的操作就完事了
    return results


async def main():
    start = time.time()
    results = await process_all_items()
    end = time.time()

    print("\n".join(results))
    print(f"总耗时：{end - start:.2f} 秒")


if __name__ == "__main__":
    asyncio.run(main())
