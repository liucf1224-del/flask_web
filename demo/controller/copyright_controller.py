import os
import pandas as pd
import time
import uuid
import logging
from flask import jsonify
from ..model import Copyright
from demo.utils.respose_utils import success_response, error_response
from demo import  db
from concurrent.futures import ThreadPoolExecutor,as_completed #线程



# 创建日志目录
LOG_DIR = os.path.join(os.getcwd(), 'logs') #定义日志目录路径为当前工作目录下的 logs 文件夹。
os.makedirs(LOG_DIR, exist_ok=True) # 创建日志目录，如果目录已存在则不会报错。

# 配置日志
logger = logging.getLogger('export_logger') # 创建日志记录器
logger.setLevel(logging.INFO) # 设置日志级别为 INFO  设置日志级别为 INFO，即只记录 INFO 级别及以上（如 WARNING, ERROR）的日志。

# 防止重复添加 handler
if not logger.handlers:
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'export.log'), encoding='utf-8') # 创建一个文件处理器，将日志写入 logs/export.log 文件中，编码格式为 UTF-8。
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') #定义日志输出格式：时间戳、日志级别、日志信息。
    file_handler.setFormatter(formatter) # 将格式设置到文件处理器上
    logger.addHandler(file_handler) # 将文件处理器添加到日志记录器中。

class CopyrightController:
    # 你可以看到我现在的项目已经安装了 Flask-SocketIO
    @staticmethod
    def export(facilitator_ids, app=None): # 实例化线程池
        if not isinstance(facilitator_ids, list) or not facilitator_ids:
            return error_response(message="缺少 facilitator_ids 参数")

        EXPORT_FOLDER = os.path.join(app.root_path, 'exports') #构建导出文件的存储路径，基于 Flask 应用的根目录。
        os.makedirs(EXPORT_FOLDER, exist_ok=True) # 创建导出文件的存储目录，如果目录不存在则创建。

        results = {} #字典

        def _export_single(fid):
            start_time = time.time()
            logger.info(f"[{fid}] 开始导出任务")

            # 进入 Flask 应用上下文，确保在多线程环境下能安全访问 Flask 资源。
            with app.app_context():
                try:
                    query = Copyright.query.filter(Copyright.facilitator_id == fid).all()
                    if not query:
                        results[fid] = "失败: 数据为空"
                        return
                    # 将查询结果转换为 pandas.DataFrame 对象，准备导出。
                    df = pd.DataFrame([
                        {
                            "ID": item.id,
                            "场所号": item.shop_id,
                            "云账号": item.device_id,
                            "订单号": item.order_no,
                            "服务商ID": item.facilitator_id,
                            "金额": float(item.total) if item.total else None,
                            "支付时间": item.payment_time,
                        } for item in query
                    ])

                    filename = f"export_facilitator_{fid}_{uuid.uuid4()}_test.csv" # 构建文件名
                    file_path = os.path.join(EXPORT_FOLDER, filename) # 构建文件路径
                    df.to_csv(file_path, index=False, encoding='utf-8-sig') # 保存为 CSV 文件

                    # 记录导出完成
                    duration = time.time() - start_time
                    logger.info(f"[{fid}] 导出完成，共 {len(query)} 条记录，耗时 {duration:.2f} 秒，文件：{filename}")
                    results[fid] = filename #放入字典

                except Exception as e:
                    # 记录异常
                    logger.error(f"[{fid}] 导出失败: {e}", exc_info=True)
                    results[fid] = f"失败: {e}"
                finally:
                    db.session.remove()  # 确保每个线程结束后会话被清理

        # 启动线程池
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务到线程池
            futures = [executor.submit(_export_single, fid) for fid in facilitator_ids]
            # 等待所有任务完成，确保异常被捕获。
            for future in as_completed(futures):
                future.result()  # 确保异常被捕获

        return success_response(data=
                                {
                                    "message": "已完成多个导出任务",
                                    "results": results,
                                    "export_folder": EXPORT_FOLDER
                                })
    @staticmethod
    def export_base(params):
        facilitator_id = params.get('facilitator_id')

        if not facilitator_id:
            return jsonify({"code": -1, "message": "缺少 facilitator_id 参数"})

        # 查询最多 1000 条数据
        query = Copyright.query \
            .filter(Copyright.facilitator_id == facilitator_id) \
            .all()
            # .limit(1000) \


        if not query:
            return jsonify({"code": 0, "message": "没有找到对应数据"})

        # 转成 DataFrame
        data = [{
            "ID": item.id,
            "场所号": item.shop_id,
            "云账号": item.device_id,
            "订单号": item.order_no,
            "服务商ID": item.facilitator_id,
            "金额": float(item.total) if item.total else None,
            "支付时间": item.payment_time,
        } for item in query]

        df = pd.DataFrame(data)

        # 创建 exports 文件夹（如果不存在）
        EXPORT_FOLDER = os.path.join(os.getcwd(), 'exports')
        os.makedirs(EXPORT_FOLDER, exist_ok=True)
        print(time.time())
        # 构造文件名
        filename = f"export_facilitator_{uuid.uuid4()}_test.csv"
        file_path = os.path.join(EXPORT_FOLDER, filename)

        # 保存为 CSV
        df.to_csv(file_path, index=False, encoding='utf-8-sig')

        # 返回提示信息
        return jsonify({
            "code": 0,
            "message": f"导出成功，文件已保存至：{file_path}",
            "filename": filename
        })

    @staticmethod
    def export_all_data(facilitator_id, page=1, per_page=1000):
        all_data = []

        while True:
            pagination = Copyright.query \
                .filter(Copyright.facilitator_id == facilitator_id) \
                .paginate(page=page, per_page=per_page)

            items = pagination.items
            if not items:
                break

            data = [{
                "ID": item.id,
                "场所号": item.shop_id,
                "云账号": item.device_id,
                "订单号": item.order_no,
                "服务商ID": item.facilitator_id,
                "金额": float(item.total) if item.total else None,
                "支付时间": item.payment_time,
            } for item in items]

            all_data.extend(data)
            if len(items) < per_page:
                break
            page += 1

        return all_data

    # @staticmethod
    # def export01(params):
    #     facilitator_ids = params.get('facilitator_ids', [])
    #
    #     if not isinstance(facilitator_ids, list) or len(facilitator_ids) == 0:
    #         return error_response(message=f"缺少 facilitator_ids 参")
    #
    #     EXPORT_FOLDER = os.path.join(os.getcwd(), 'exports')
    #     os.makedirs(EXPORT_FOLDER, exist_ok=True)
    #
    #     results = {}
    #
    #     def _export_single(fid,demo):
    #         start_time = time.time()
    #         logger.info(f"[{fid}] 开始导出任务")
    #
    #         # 获取当前 Flask 应用实例，并手动推入上下文
    #         # app = current_app._get_current_object()
    #
    #         with demo.app_context():  # 手动创建应用上下文
    #             try:
    #                 # 查询数据
    #                 query = Copyright.query \
    #                     .filter(Copyright.facilitator_id == fid) \
    #                     .all()
    #
    #                 if not query:
    #                     msg = f"[{fid}] 数据为空"
    #                     logger.warning(msg)
    #                     results[fid] = "失败: 数据为空"
    #                     return
    #
    #                 # 转成 DataFrame
    #                 data = [{
    #                     "ID": item.id,
    #                     "场所号": item.shop_id,
    #                     "云账号": item.device_id,
    #                     "订单号": item.order_no,
    #                     "服务商ID": item.facilitator_id,
    #                     "金额": float(item.total) if item.total else None,
    #                     "支付时间": item.payment_time,
    #                 } for item in query]
    #
    #                 df = pd.DataFrame(data)
    #
    #                 # 构造文件名
    #                 filename = f"export_facilitator_{fid}_{uuid.uuid4()}_test.csv"
    #                 file_path = os.path.join(EXPORT_FOLDER, filename)
    #
    #                 # 保存为 CSV
    #                 df.to_csv(file_path, index=False, encoding='utf-8-sig')
    #
    #                 duration = time.time() - start_time
    #                 msg = f"[{fid}] 导出完成，共 {len(data)} 条记录，耗时 {duration:.2f} 秒，文件：{filename}"
    #                 logger.info(msg)
    #                 results[fid] = filename
    #
    #             except Exception as e:
    #                 duration = time.time() - start_time
    #                 msg = f"[{fid}] 导出失败: {str(e)}，耗时 {duration:.2f} 秒"
    #                 logger.error(msg, exc_info=True)
    #                 results[fid] = f"失败: {str(e)}"
    #
    #     # 开启线程池并发处理
    #
    #     with ThreadPoolExecutor(max_workers=5) as executor:
    #         futures = [
    #             executor.submit(_export_single, fid, demo)  # ✅ 传入 app 实例
    #             for fid in facilitator_ids
    #         ]
    #
    #         for future in as_completed(futures):
    #             try:
    #                 future.result()
    #             except Exception as e:
    #                 logger.error(f"导出任务发生异常: {e}", exc_info=True)
    #         return success_response(data={"message": f"已完成多个导出任务", "results": results})
    #
    #
    #
    #     # with ThreadPoolExecutor(max_workers=5) as executor:
    #     #     list(executor.map(_export_single, facilitator_ids))
    #     #     return success_response(data={"message": f"已完成多个导出任务", "results": results})
    #         # executor.map(_export_single, facilitator_ids)
    #         # return success_response(data={"message": f"已完成多个导出任务"})
    #
    #     from flask import current_app  # ✅ 正确导入 current_app
    #     from your_project import create_app  # ✅ 假设你有一个 create_app 函数生成 app 实例
    #
    #     # 在 export 方法中，获取真实的 Flask 应用实例
    #     app = create_app()  # ✅ 替换为你的实际创建方式
    #
    #     @staticmethod
    #     def export(params):
    #         facilitator_ids = params.get('facilitator_ids', [])
    #
    #         if not isinstance(facilitator_ids, list) or len(facilitator_ids) == 0:
    #             return error_response(message=f"缺少 facilitator_ids 参")
    #
    #         EXPORT_FOLDER = os.path.join(os.getcwd(), 'exports')
    #         os.makedirs(EXPORT_FOLDER, exist_ok=True)
    #
    #         results = {}
    #
    #         def _export_single(fid):
    #             start_time = time.time()
    #             logger.info(f"[{fid}] 开始导出任务")
    #
    #             # 获取真实的 Flask 应用实例
    #             real_app = current_app._get_current_object()  # ✅ 从 current_app 获取真实 app
    #
    #             with real_app.app_context():  # ✅ 使用真实 app 的上下文
    #                 try:
    #                     # 查询数据
    #                     query = Copyright.query \
    #                         .filter(Copyright.facilitator_id == fid) \
    #                         .all()
    #
    #                     if not query:
    #                         msg = f"[{fid}] 数据为空"
    #                         logger.warning(msg)
    #                         results[fid] = "失败: 数据为空"
    #                         return
    #
    #                     # 转成 DataFrame
    #                     data = [{
    #                         "ID": item.id,
    #                         "场所号": item.shop_id,
    #                         "云账号": item.device_id,
    #                         "订单号": item.order_no,
    #                         "服务商ID": item.facilitator_id,
    #                         "金额": float(item.total) if item.total else None,
    #                         "支付时间": item.payment_time,
    #                     } for item in query]
    #
    #                     df = pd.DataFrame(data)
    #
    #                     # 构造文件名
    #                     filename = f"export_facilitator_{fid}_{uuid.uuid4()}_test.csv"
    #                     file_path = os.path.join(EXPORT_FOLDER, filename)
    #
    #                     # 保存为 CSV
    #                     df.to_csv(file_path, index=False, encoding='utf-8-sig')
    #
    #                     duration = time.time() - start_time
    #                     msg = f"[{fid}] 导出完成，共 {len(data)} 条记录，耗时 {duration:.2f} 秒，文件：{filename}"
    #                     logger.info(msg)
    #                     results[fid] = filename
    #
    #                 except Exception as e:
    #                     duration = time.time() - start_time
    #                     msg = f"[{fid}] 导出失败: {str(e)}，耗时 {duration:.2f} 秒"
    #                     logger.error(msg, exc_info=True)
    #                     results[fid] = f"失败: {str(e)}"
    #
    #         # 开启线程池并发处理
    #         with ThreadPoolExecutor(max_workers=5) as executor:
    #             futures = [
    #                 executor.submit(_export_single, fid)  # ✅ 不需要传递 app 实例
    #                 for fid in facilitator_ids
    #             ]
    #
    #             for future in as_completed(futures):
    #                 try:
    #                     future.result()
    #                 except Exception as e:
    #                     logger.error(f"导出任务发生异常: {e}", exc_info=True)
    #             return success_response(data={"message": f"已完成多个导出任务", "results": results})



