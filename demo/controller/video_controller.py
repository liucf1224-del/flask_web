import os
import shutil
import subprocess
import uuid
from flask import jsonify, request, current_app
import logging

# 设置日志
logger = logging.getLogger(__name__)

class VideoController:
    @staticmethod
    def extract_audio(video_path, audio_output_path):
        """
        从视频中提取音频
        
        Args:
            video_path (str): 视频文件路径
            audio_output_path (str): 输出音频文件路径
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-q:a', '0',
                '-map', 'a',
                audio_output_path,
                '-y'
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                error_msg = f"FFmpeg 错误: {result.stderr}"
                logger.error(error_msg)
                return False, error_msg
            
            logger.info("音频提取成功")
            return True, "音频提取成功"
        except subprocess.TimeoutExpired:
            error_msg = "FFmpeg 处理超时"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"提取音频时出错: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def replace_audio(video_path, new_audio_path, output_path, shortest=True):
        """
        将视频中的音频替换为新的音频
        
        Args:
            video_path (str): 原视频文件路径
            new_audio_path (str): 新音频文件路径
            output_path (str): 输出视频文件路径
            shortest (bool): 是否以最短的流为准
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', new_audio_path,
                '-c:v', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
            ]
            
            # 如果需要以最短的流为准，添加 -shortest 参数
            if shortest:
                cmd.append('-shortest')
                
            cmd.append(output_path)
            cmd.append('-y')
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                error_msg = f"FFmpeg 错误: {result.stderr}"
                logger.error(error_msg)
                return False, error_msg
            
            logger.info("音频替换成功")
            return True, "音频替换成功"
        except subprocess.TimeoutExpired:
            error_msg = "FFmpeg 处理超时"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"替换音频时出错: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def process_video_audio():
        """
        处理视频音频的主函数
        """
        try:
            data = request.get_json()
            video_path = data.get('video_path')
            audio_path = data.get('audio_path')
            shortest = data.get('shortest', True)  # 默认以最短的流为准
            
            # 验证输入参数
            if not video_path:
                return jsonify({"code": -1, "message": "缺少视频文件路径"}), 400
            
            if not os.path.exists(video_path):
                return jsonify({"code": -1, "message": "视频文件不存在"}), 400
            
            if audio_path and not os.path.exists(audio_path):
                return jsonify({"code": -1, "message": "音频文件不存在"}), 400
            
            # 获取应用实例和创建临时目录
            app = current_app._get_current_object()
            temp_dir = os.path.join(app.root_path, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成唯一标识符
            unique_id = str(uuid.uuid4())
            
            # 提取原始音频（如果未提供新音频）
            extracted_audio_path = None
            if not audio_path:
                extracted_audio_path = os.path.join(temp_dir, f'extracted_audio_{unique_id}.mp3')
                success, message = VideoController.extract_audio(video_path, extracted_audio_path)
                if not success:
                    # 清理可能创建的文件
                    if extracted_audio_path and os.path.exists(extracted_audio_path):
                        os.remove(extracted_audio_path)
                    return jsonify({"code": -1, "message": message}), 500
                audio_to_use = extracted_audio_path
            else:
                audio_to_use = audio_path
            
            # 生成输出文件路径
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(video_dir, f'{video_name}_processed_{unique_id}.mp4')
            
            # 替换音频
            success, message = VideoController.replace_audio(video_path, audio_to_use, output_path, shortest)
            if not success:
                # 清理可能创建的文件
                if extracted_audio_path and os.path.exists(extracted_audio_path):
                    os.remove(extracted_audio_path)
                return jsonify({"code": -1, "message": message}), 500
            
            # 清理临时文件
            if extracted_audio_path and os.path.exists(extracted_audio_path):
                os.remove(extracted_audio_path)
            
            return jsonify({
                "code": 0,
                "message": "处理完成",
                "output_path": output_path
            }), 200
            
        except Exception as e:
            logger.error(f"处理过程中出错: {str(e)}", exc_info=True)
            return jsonify({"code": -1, "message": f"处理过程中出错: {str(e)}"}), 500
        finally:
            # 删除临时目录
            shutil.rmtree(temp_dir)