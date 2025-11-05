from flask import Blueprint, request, jsonify, current_app
from demo.controller.yolo_controller import YOLOController
import os
from werkzeug.utils import secure_filename

yolo_bp = Blueprint('yolo', __name__, url_prefix='/yolo')

@yolo_bp.route('/detect_image', methods=['POST'])
def detect_image():
    """
    对上传的图片进行目标检测
    
    请求参数：
    - image: 图片文件 (multipart/form-data)
    
    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "message": "检测结果信息",
        "image_path": "结果图片路径",
        "detections": [         # 检测到的目标列表
            {
                "class": "类别名称",
                "confidence": 0.95,  # 置信度
                "bbox": {           # 边界框坐标
                    "x1": 100,
                    "y1": 120,
                    "x2": 300,
                    "y2": 400
                }
            }
        ]
    }
    """
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'code': -1,
                'message': '没有上传图片文件'
            }), 400
        
        file = request.files['image']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'code': -1,
                'message': '没有选择图片文件'
            }), 400
        
        # 保存上传的文件
        if file:
            # 创建上传目录
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 确保文件有扩展名
            if '.' not in filename:
                filename += '.jpg'
            
            # 保存文件
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # 执行目标检测
            result = YOLOController.detect_image(file_path)
            
            return jsonify(result)
        
        return jsonify({
            'code': -1,
            'message': '文件上传失败'
        }), 400
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@yolo_bp.route('/detect_safety_helmet', methods=['POST'])
def detect_safety_helmet():
    """
    对上传的图片进行安全帽检测
    
    请求参数：
    - image: 图片文件 (multipart/form-data)
    
    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "message": "检测结果信息",
        "image_path": "结果图片路径",
        "detections": [         # 检测到的目标列表
            {
                "class": "类别名称",
                "confidence": 0.95,  # 置信度
                "bbox": {           # 边界框坐标
                    "x1": 100,
                    "y1": 120,
                    "x2": 300,
                    "y2": 400
                }
            }
        ],
        "person_count": 3,      # 检测到的人员数量
        "helmet_count": 2       # 佩戴安全帽的数量
    }
    """
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'code': -1,
                'message': '没有上传图片文件'
            }), 400
        
        file = request.files['image']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'code': -1,
                'message': '没有选择图片文件'
            }), 400
        
        # 保存上传的文件
        if file:
            # 创建上传目录
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 确保文件有扩展名
            if '.' not in filename:
                filename += '.jpg'
            
            # 保存文件
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # 执行安全帽检测
            result = YOLOController.detect_safety_helmet(file_path)
            
            return jsonify(result)
        
        return jsonify({
            'code': -1,
            'message': '文件上传失败'
        }), 400
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@yolo_bp.route('/detect_camera', methods=['POST'])
def detect_camera():
    """
    实时摄像头目标检测
    
    请求参数：无
    
    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "message": "检测结果信息",
        "image_path": "结果图片路径",
        "detections": [         # 检测到的目标列表
            {
                "class": "类别名称",
                "confidence": 0.95,  # 置信度
                "bbox": {           # 边界框坐标
                    "x1": 100,
                    "y1": 120,
                    "x2": 300,
                    "y2": 400
                }
            }
        ]
    }
    """
    try:
        # 执行摄像头检测
        result = YOLOController.detect_camera()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@yolo_bp.route('/model_info', methods=['GET'])
def model_info():
    """
    获取安全帽检测模型信息
    
    返回：
    {
        "code": 0,              # 0表示成功，-1表示失败
        "model_path": "模型路径",
        "model_names": {},      # 模型类别映射
        "model_config": {},     # 模型配置
        "model_type": "模型类型"
    }
    """
    try:
        # 加载安全帽检测模型
        model = YOLOController.load_safety_helmet_model()
        
        return jsonify({
            'code': 0,
            'model_path': 'best_model_8n.pth',
            'model_names': model.names,
            'model_config': model.overrides,
            'model_type': str(type(model))
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取模型信息失败: {str(e)}'
        }), 500
