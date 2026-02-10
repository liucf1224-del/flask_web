import io
import os
import sys
import time
from pathlib import Path

from PIL import Image
from rembg import remove, new_session

""" 本地模型抠图"""
# 定义使用模型的地址
# CURRENT_DIR = Path(__file__).parent
# print(CURRENT_DIR)
# MODEL_PATH = CURRENT_DIR / "remove_model" / "u2net.onnx"

# MODEL_PATH = r"D:/py_work/flask_demo/remove_model/u2net.onnx"
# 如果不存在就创建模型地址
# os.makedirs(MODEL_PATH, exist_ok=True)
# 设置环境变量 告诉模型的存储地址
# os.environ["REMOVE_MODEL_PATH"] = MODEL_PATH

# ===================== 核心优化：适配本地+打包后的模型路径 =====================
def get_model_path():
    """
    兼容本地运行和打包后的模型路径（比如pyinstaller打包）
    """
    # 打包后的exe运行时，__file__ 指向临时目录，需用 sys._MEIPASS 获取真实路径
    if getattr(sys, 'frozen', False):
        # 打包后：exe所在目录/remove_model/u2net.onnx
        base_dir = Path(sys.executable).parent
    else:
        # 本地运行：当前脚本所在目录/remove_model/u2net.onnx
        base_dir = Path(__file__).parent

    model_dir = base_dir / "remove_model"
    model_path = model_dir / "u2net.onnx"

    # 创建模型目录（仅创建文件夹，不是文件）
    os.makedirs(model_dir, exist_ok=True)
    return model_path


# 获取模型路径（兼容本地/打包）
MODEL_PATH = get_model_path()


def deal_image(input_path, out_path):
    print(f"处理图片路径：{input_path}")
    print(f"处理后的图片路径：{out_path}")
    print(f"模型地址：{MODEL_PATH}")

    # 检测模型存在是否
    if not MODEL_PATH.exists():
        print(f"模型文件不存在: {MODEL_PATH}")
        return False

    try:
        session = new_session(model_path=str(MODEL_PATH))
        # 读取图片 打开保留原始的画质
        with open(input_path, 'rb') as f:
            img = f.read()

        # 处理图片 抠图使用rembg
        output_data =remove(
             img,
            # 使用alpha_matting 抠图画质优化参数(保证边缘清晰，无锯齿)
             alpha_matting=True, #边缘精细细节
             session=session,  # 传入本地模型会话（核心修改）
            #通用版
             # alpha_matting_foreground_threshold=200,#240 前景阈值
             # alpha_matting_background_threshold=15,#10 背景阈值
             # alpha_matting_erode_size=5,#10  腐蚀尺寸
            #绝对版
            alpha_matting_foreground_threshold=240,  # 240 前景阈值
            alpha_matting_background_threshold=10,  # 10 背景阈值
            alpha_matting_erode_size=8,  # 10  腐蚀尺寸
             # model=MODEL_PATH,
             # alpha_matting_base_size=1000,
             # output_path=out_path
        )

        # 将抠图数据转为pil图像，保证透明的通道
        # img_output = Image.open(io.BytesIO(output_data)).convert("RGBA")
        image_output = Image.open(io.BytesIO(output_data)).convert("RGBA")

        #保存并且不压缩
        image_output.save(out_path, "PNG", optimize=False,quality=95)

        print(f"✅ 抠图完成！透明PNG已保存至：{out_path}")
        print(f"💡 图片尺寸：{image_output.size}（宽x高），保留完整透明通道")
        return True
    except Exception as e:
        print(f"处理图片失败：{str(e)}")
        return False
if __name__ == "__main__":
    print("开始处理ing...")
    INPUT_IMAGE_PATH = "D:/Ai/模型/a.jpg"
    # INPUT_IMAGE_PATH = "D:/Ai/模型/ddd.jpg"
    # INPUT_IMAGE_PATH = "D:/Ai/模型/640.webp"
    # 随机时间的图片名
    OUTPUT_IMAGE_PATH = f"D:/py_work/flask_demo/{time.strftime('%Y%m%d%H%M%S', time.localtime())}.png"

    deal_image(INPUT_IMAGE_PATH, OUTPUT_IMAGE_PATH)