import os
from ultralytics import YOLO

def test_model(model_path):
    """测试模型"""
    print(f"检查模型文件: {model_path}")
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return False
    
    print(f"文件大小: {os.path.getsize(model_path)} 字节")
    
    try:
        print("尝试加载模型...")
        model = YOLO(model_path)
        print("模型加载成功!")
        print(f"模型类别: {model.names}")
        print(f"模型配置: {model.overrides}")
        return True
    except Exception as e:
        print(f"模型加载失败: {e}")
        import traceback
        traceback.print_exc()  # 添加详细错误堆栈
        return False

if __name__ == "__main__":
    # 测试可能的模型文件
    models_to_test = [
        'yolov8x_person_face.pt'
    ]
    
    for model_path in models_to_test:
        print(f"\n{'=' * 60}")
        print(f"开始测试: {model_path}")
        print(f"{'=' * 60}")
        test_model(model_path)
        print("-" * 50)