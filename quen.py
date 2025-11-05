import threading
import queue
import time
import random


# 模拟耗时操作的处理函数
def process_item(item):
    # 随机生成处理时间 (0.5-2秒)
    process_time = random.uniform(0.5, 2.0)
    time.sleep(process_time)
    return f"处理完成：{item}，耗时 {process_time:.2f} 秒"


# 工作线程函数 - 从队列获取任务并处理
def worker(q, result_queue):
    while True:
        item = q.get()  # 从队列获取任务
        if item is None:  # 接收到终止信号
            q.task_done()  # 标记任务完成
            break

        print(f"[线程-{threading.current_thread().name}] 开始处理: {item}")
        result = process_item(item)  # 执行耗时操作
        result_queue.put(result)  # 将结果放入结果队列
        q.task_done()  # 标记任务完成


if __name__ == "__main__":
    # 准备任务列表
    tasks = ["任务A", "任务B", "任务C", "任务D", "任务E", "任务F", "任务G", "任务H"]

    # 创建任务队列和结果队列
    task_queue = queue.Queue()
    result_queue = queue.Queue()

    # 将任务放入队列
    for task in tasks:
        task_queue.put(task)

    # 记录开始时间
    start_time = time.time()

    # 创建工作线程 (创建4个线程)
    threads = []
    for i in range(4):  # 4个工作线程
        t = threading.Thread(target=worker, args=(task_queue, result_queue))
        t.start()
        threads.append(t)

    # 添加终止信号 (每个线程一个None)
    for _ in range(len(threads)):
        task_queue.put(None)

    # 等待所有任务完成
    task_queue.join()

    # 收集结果
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    # 等待所有线程结束
    for t in threads:
        t.join()

    # 计算总耗时
    total_time = time.time() - start_time

    # 输出结果
    print("\n===== 处理结果 =====")
    for result in results:
        print(result)

    print(f"\n总任务数: {len(tasks)}")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均每个任务耗时: {total_time / len(tasks):.2f} 秒")