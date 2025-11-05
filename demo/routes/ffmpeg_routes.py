from flask import Blueprint
from demo.controller.video_controller import VideoController

ffmpeg_bp = Blueprint('ffmpeg', __name__, url_prefix='/ffmpeg')

@ffmpeg_bp.route('/process', methods=['POST'])
def process_video_audio():
    """
    处理视频音频：
    1. 从视频中提取音频（如果没有提供新音频）
    2. 将新音频替换到视频中（如果提供了新音频）
    
    请求参数：
    {
        "video_path": "视频文件路径",
        "audio_path": "新音频文件路径（可选）",
        "shortest": true/false (可选，默认为true，表示以最短的流为准)
    }
    
    返回：
    {
        "code": 0,  # 0表示成功，-1表示失败
        "message": "处理结果信息",
        "output_path": "处理后的视频文件路径"
    }
    """
    return VideoController.process_video_audio()