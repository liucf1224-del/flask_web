import io
import os
import time

from PIL import Image

"""处理格式切换"""

def deal_image(input_path, out_path, target_format=None):
    print(f"处理图片路径：{input_path}")
    print(f"处理后的图片路径：{out_path}")
    
    # 如果指定了目标格式，则使用目标格式，否则保持原格式
    if target_format:
        target_format = target_format.upper()
    # 如果未指定目标格式，默认保持原格式

    try:
        with open(input_path, 'rb') as f:
            image_data = f.read()
        img = Image.open(io.BytesIO(image_data))

        actual_format = img.format
        if not actual_format:
            print("图片格式未知，无法处理")
            return False
        actual_format = actual_format.upper()
        print(f"图片格式：{actual_format}")

        if actual_format == "GIF":
            print("gif图片不做处理")
            return False  # 添加return语句

        supported_formats = [
            "JPEG",
            "JPG",
            "PNG",
            "WEBP",
         ]
        if actual_format not in supported_formats:
            print(f"不支持的图片格式：{actual_format}")
            return False
            
        # 如果未指定目标格式，默认使用原格式
        if target_format is None:
            save_format = actual_format
            if actual_format == "JPEG":
                ext = "jpg"
            else:
                ext = actual_format.lower()
        else:
            # 根据目标格式确定扩展名
            if target_format in ["JPEG", "JPG"]:
                ext = "jpg"
                save_format = "JPEG"
            elif target_format == "PNG":
                ext = "png"
                save_format = "PNG"
            elif target_format == "WEBP":
                ext = "webp"
                save_format = "WEBP"
            else:
                # 如果指定了不支持的格式，默认使用原格式
                save_format = actual_format
                if actual_format == "JPEG":
                    ext = "jpg"
                else:
                    ext = actual_format.lower()

        base_name = os.path.splitext(out_path)[0]
        final_out_path = f"{base_name}.{ext}"

        if out_path != final_out_path:
            print(f"⚠️  扩展名修正：{os.path.basename(out_path)} -> {os.path.basename(final_out_path)}")

        # 对于JPEG格式，需要转换模式以避免透明度问题
        if save_format == "JPEG" and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        # 对于WEBP格式的特殊处理
        elif actual_format == "WEBP" and img.mode in ('RGBA', 'LA', 'P') and save_format != "WEBP":
            # 如果从WEBP转为其他格式且原图有透明度，则转换为RGB
            if save_format == "JPEG":
                img = img.convert('RGB')
        
        img.save(final_out_path, save_format, optimize=True, quality=95)

        print(f"✅ 处理完成！")
        print(f"✅ 原始格式：{actual_format}")
        print(f"✅ 保存格式：{save_format}")
        print(f"✅ 保存路径：{final_out_path}")
        print(f"✅ 文件大小：{os.path.getsize(final_out_path)}字节")

        return True
    except Exception as e:
        print(f"处理图片失败：{str(e)}")
        return False


def get_image_info(input_path):
    """
    获取图片信息：格式、大小、模式等
    """
    try:
        with open(input_path, 'rb') as f:
            image_data = f.read()

        img = Image.open(io.BytesIO(image_data))

        info = {
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'binary_size': len(image_data)
        }

        print(f"📊 图片信息：")
        print(f"   格式：{img.format}")
        print(f"   尺寸：{img.size[0]}x{img.size[1]}")
        print(f"   模式：{img.mode}")
        print(f"   二进制大小：{len(image_data)}字节")

        return info
    except Exception as e:
        print(f"❌ 获取图片信息失败：{str(e)}")
        return None


if __name__ == "__main__":
    print("开始处理ing...")
    # INPUT_IMAGE_PATH = "D:/Ai/模型/a.jpg"
    INPUT_IMAGE_PATH = "D:/Ai/模型/1.png"
    # INPUT_IMAGE_PATH = "D:/Ai/模型/ddd.jpg"
    # INPUT_IMAGE_PATH = "D:/Ai/模型/640.webp"
    # 随机时间的图片名
    info = get_image_info(INPUT_IMAGE_PATH)
    if not info:
        print("图片信息获取失败")
        exit()

    # 根据原图片格式确定输出扩展名
    original_ext = info['format'].lower() if info['format'] and info['format'].upper() != 'JPEG' else 'jpg'
    OUTPUT_IMAGE_PATH = f"D:/py_work/flask_demo/{time.strftime('%Y%m%d%H%M%S', time.localtime())}.{original_ext}"
    deal_image(INPUT_IMAGE_PATH, OUTPUT_IMAGE_PATH)