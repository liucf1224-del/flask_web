import os
import cv2
import numpy as np
from flask import jsonify, request, current_app
from ultralytics import YOLO
import uuid
import base64
from io import BytesIO


class YOLOController:
    # 初始化模型
    safety_helmet_model = None
    model = None

    @classmethod
    def load_model(cls):
        """加载YOLOv8模型"""
        if cls.model is None:
            # 使用yolov8n.pt模型，适用于CPU
            cls.model = YOLO('yolov8n.pt')
            # 设置为CPU模式
            cls.model.to('cpu')
        return cls.model

    @classmethod
    def load_safety_helmet_model(cls):
        """加载安全帽检测模型-这个是一个测试的模型名字"""
        # 这里我们先使用yolov8n.pt作为示例
        # 在实际应用中，应该使用专门训练过的安全帽检测模型
        if cls.safety_helmet_model is None:
            # print(f"正在加载安全帽检测模型: yolo8_helm_best.pt")
            # cls.safety_helmet_model = YOLO('yolo8_helm_best.pt')  # 实际应使用 custom_safety_helmet.pt
            # print(f"音乐器材检测模型")
            # cls.safety_helmet_model = YOLO('yolo8s_best_best.onnx ')
            print(f"人脸人体检测模型")
            cls.safety_helmet_model = YOLO('yolov8x_person_face.pt')

            # 设置为CPU模式
            cls.safety_helmet_model.to('cpu')
            print(f"模型类名: {cls.safety_helmet_model.__class__}")
            print(f"模型配置: {cls.safety_helmet_model.overrides}")
        return cls.safety_helmet_model

    @staticmethod
    def detect_image(image_path):
        """
        对单张图片进行目标检测
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            dict: 检测结果
        """
        try:
            # 加载模型
            model = YOLOController.load_model()

            # 执行检测，设置为CPU模式并降低图像大小以提高速度
            results = model(image_path, imgsz=640, device='cpu', verbose=False)

            # 获取原图
            img = cv2.imread(image_path)

            # 绘制检测结果
            annotated_frame = results[0].plot()

            # 生成输出路径
            output_dir = os.path.join(current_app.root_path, 'static', 'yolo_results')
            os.makedirs(output_dir, exist_ok=True)

            # 生成唯一文件名
            filename = f"result_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(output_dir, filename)

            # 保存结果图片
            cv2.imwrite(output_path, annotated_frame)

            # 获取相对路径用于URL访问
            relative_path = os.path.join('static', 'yolo_results', filename)

            # 提取检测信息
            result_data = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0].tolist()  # 获取框坐标
                    cls_id = int(box.cls[0].item())  # 获取类别ID
                    class_name = model.names[cls_id]  # 获取类别名称
                    conf = float(box.conf[0].item())  # 获取置信度

                    result_data.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': {
                            'x1': b[0],
                            'y1': b[1],
                            'x2': b[2],
                            'y2': b[3]
                        }
                    })

            return {
                'code': 0,
                'message': '检测完成',
                'image_path': relative_path,
                'detections': result_data
            }

        except Exception as e:
            return {
                'code': -1,
                'message': f'检测失败: {str(e)}'
            }

    @staticmethod
    def detect_camera():
        """
        实时摄像头检测
        
        Returns:
            dict: 操作结果
        """
        try:
            # 加载模型
            model = YOLOController.load_model()

            # 打开摄像头
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                return {
                    'code': -1,
                    'message': '无法打开摄像头'
                }

            # 读取一帧进行测试
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return {
                    'code': -1,
                    'message': '无法读取摄像头画面'
                }

            # 对帧进行检测，设置为CPU模式并降低图像大小以提高速度
            results = model(frame, imgsz=640, device='cpu', verbose=False)

            # 绘制检测结果
            annotated_frame = results[0].plot()

            # 生成输出路径
            output_dir = os.path.join(current_app.root_path, 'static', 'yolo_results')
            os.makedirs(output_dir, exist_ok=True)

            # 生成唯一文件名
            filename = f"camera_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(output_dir, filename)

            # 保存结果图片
            cv2.imwrite(output_path, annotated_frame)

            # 获取相对路径用于URL访问
            relative_path = os.path.join('static', 'yolo_results', filename)

            # 释放摄像头
            cap.release()

            # 提取检测信息
            result_data = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0].tolist()  # 获取框坐标
                    cls_id = int(box.cls[0].item())  # 获取类别ID
                    class_name = model.names[cls_id]  # 获取类别名称
                    conf = float(box.conf[0].item())  # 获取置信度

                    result_data.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': {
                            'x1': b[0],
                            'y1': b[1],
                            'x2': b[2],
                            'y2': b[3]
                        }
                    })

            return {
                'code': 0,
                'message': '摄像头检测完成',
                'image_path': relative_path,
                'detections': result_data
            }

        except Exception as e:
            return {
                'code': -1,
                'message': f'摄像头检测失败: {str(e)}'
            }

    @staticmethod
    def detect_safety_helmet(image_path):
        """
        对图片进行安全帽检测
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            dict: 检测结果
        """
        try:
            # 加载安全帽检测模型
            model = YOLOController.load_safety_helmet_model()
            print(f"使用的模型: {model}")
            print(f"模型名称列表: {model.names}")

            # 执行检测，设置为CPU模式并降低图像大小以提高速度
            print(f"开始对图片进行安全帽检测: {image_path}")
            results = model(image_path, imgsz=640, device='cpu', verbose=False)
            print(f"检测完成，结果数量: {len(results)}")

            # 获取原图
            img = cv2.imread(image_path)

            # 绘制检测结果
            annotated_frame = results[0].plot()

            # 生成输出路径
            output_dir = os.path.join(current_app.root_path, 'static', 'yolo_results')
            os.makedirs(output_dir, exist_ok=True)

            # 生成唯一文件名
            filename = f"helmet_result_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(output_dir, filename)

            # 保存结果图片
            cv2.imwrite(output_path, annotated_frame)

            # 获取相对路径用于URL访问
            relative_path = os.path.join('static', 'yolo_results', filename)

            # 提取检测信息
            result_data = []
            # helmet_count = 0
            person_count = 0
            face_count = 0

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0].tolist()  # 获取框坐标
                    cls_id = int(box.cls[0].item())  # 获取类别ID
                    class_name = model.names[cls_id]  # 获取类别名称
                    conf = float(box.conf[0].item())  # 获取置信度

                    # 统计人员和安全帽数量
                    # if class_name == 'person':
                    #     person_count += 1
                    # elif class_name == 'helmet' or class_name == 'head_with_helmet'or class_name == 'pakai helm':
                    #     helmet_count += 1
                    # elif class_name == 'tanpa helm':  # 无头盔，算作人员但未佩戴安全帽
                    #     person_count += 1

                    # 安全帽的模型 yolo8_helm_best.pt
                    # if class_name == 'pakai helm':  # 戴头盔
                    #     person_count += 1
                    #     helmet_count += 1
                    # elif class_name == 'tanpa helm':  # 无头盔
                    #     person_count += 1
                    # print(f"检测到类别: {class_name} 置信度: {conf}")

                    # 统计人体和人脸数量
                    if class_name == 'person':
                        person_count += 1
                    elif class_name == 'face':
                        face_count += 1
                    print(f"检测到类别: {class_name} 置信度: {conf}")

                    result_data.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': {
                            'x1': b[0],
                            'y1': b[1],
                            'x2': b[2],
                            'y2': b[3]
                        }
                    })

                # 分析安全帽佩戴情况
                # safety_message = f"检测到{person_count}个人，其中{helmet_count}人佩戴安全帽"
                # return {
                #     'code': 0,
                #     'message': '安全帽检测完成 - ' + safety_message,
                #     'image_path': relative_path,
                #     'detections': result_data,
                #     'person_count': person_count,
                #     'helmet_count': helmet_count
                # }
                # 分析检测情况
                safety_message = f"检测到{person_count}个人体，{face_count}个人脸"
                return {
                    'code': 0,
                    'message': '人体人脸检测完成 - ' + safety_message,
                    'image_path': relative_path,
                    'detections': result_data,
                    'person_count': person_count,
                    'face_count': face_count
                }
            return None


        except Exception as e:
            return {
                'code': -1,
                # 'message': f'安全帽检测失败: {str(e)}'
                'message': f'人体人脸检测失败: {str(e)}'
            }
