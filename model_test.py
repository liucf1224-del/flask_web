import os
import torch
from ultralytics import YOLO

def test_model_info(model_path):
    """测试模型信息"""
    print(f"测试模型: {model_path}")
    print(f"文件是否存在: {os.path.exists(model_path)}")
    print(f"文件大小: {os.path.getsize(model_path) if os.path.exists(model_path) else 'N/A'} bytes")
    
    try:
        # 尝试加载模型
        print("\n尝试加载模型...")
        model = YOLO(model_path)
        print("模型加载成功!")
        
        # 输出模型信息
        print(f"\n模型信息:")
        print(f"- 模型类型: {type(model)}")
        print(f"- 模型配置: {model.overrides}")
        print(f"- 模型类别: {model.names}")
        print(f"- 模型任务: {getattr(model, 'task', 'Unknown')}")
        
        # 尝试获取模型结构信息
        if hasattr(model, 'model'):
            print(f"- 模型结构类型: {type(model.model)}")
        
        return True
        
    except Exception as e:
        print(f"模型加载失败: {str(e)}")
        # 尝试直接加载为PyTorch模型
        try:
            print("\n尝试直接加载为PyTorch模型...")
            checkpoint = torch.load(model_path, map_location='cpu')
            print("PyTorch模型加载成功!")
            print(f"Checkpoint类型: {type(checkpoint)}")
            
            if isinstance(checkpoint, dict):
                print("Checkpoint keys:", list(checkpoint.keys()))
                if 'model' in checkpoint:
                    print(f"Model类型: {type(checkpoint['model'])}")
                if 'epoch' in checkpoint:
                    print(f"Epoch: {checkpoint['epoch']}")
                if 'best_fitness' in checkpoint:
                    print(f"Best fitness: {checkpoint['best_fitness']}")
                    
            return True
        except Exception as e2:
            print(f"PyTorch模型加载也失败: {str(e2)}")
            return False

if __name__ == "__main__":
    # 测试几个可能的模型文件
    model_files = [
        'best_model_8n.pth',
        'yolo8_helm_best.pt',
        'yolov8n.pt'
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            test_model_info(model_file)
            print("\n" + "="*50 + "\n")
        else:
            print(f"模型文件 {model_file} 不存在\n")