import os

import moviepy
# import moviepy.editor as mp
import whisper
from pydub import AudioSegment
from pydub.silence import split_on_silence
import re


def extract_audio_from_video(video_path, audio_output_path):
    """
    从视频文件中提取音频。
    """
    try:
        # video = mp.VideoFileClip(video_path)
        video =  moviepy.VideoFileClip(video_path)
        video.audio.write_audiofile(
            audio_output_path,
            fps=16000,
            nbytes=2,
            codec="pcm_s16le"
        )
        print(f"音频已成功提取到: {audio_output_path}")
        return True
    except Exception as e:
        print(f"提取音频时发生错误: {e}")
        return False


def transcribe_audio_with_whisper(audio_path, model_name="base", device=None, cache_dir=None):
    """
    使用 OpenAI Whisper 模型将音频转换为文本。
    model_name 可以是 "tiny", "base", "small", "medium", "large"。
    更大的模型准确度更高，但需要更多的计算资源和时间。
    """
    try:
        if device is None:
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"
        print(f"正在加载 Whisper 模型: {model_name}...")
        model = whisper.load_model(model_name, device=device, download_root=cache_dir)
        print(f"正在转录音频: {audio_path}...")
        fp16_run = device != "cpu"
        result = model.transcribe(audio_path, fp16=fp16_run)
        return result["text"]
    except Exception as e:
        print(f"转录音频时发生错误: {e}")
        return None


def split_and_transcribe_audio(audio_path, output_dir="audio_chunks", min_silence_len=500, silence_thresh=-40,
                               model_name="base", device=None, cache_dir=None):
    """
    将音频文件分割成小块，然后逐块转录。
    这对于长音频文件或内存受限的情况非常有用。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        audio = AudioSegment.from_file(audio_path)
        chunks = split_on_silence(audio,
                                  min_silence_len=min_silence_len,  # 识别为静音的最小长度 (毫秒)
                                  silence_thresh=silence_thresh,  # 低于此分贝值的被认为是静音
                                  keep_silence=200  # 保留静音的前后200毫秒
                                  )

        full_text = []
        if device is None:
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"
        model = whisper.load_model(model_name, device=device, download_root=cache_dir)
        print(f"正在加载 Whisper 模型: {model_name}...")

        for i, chunk in enumerate(chunks):
            chunk_filename = os.path.join(output_dir, f"chunk_{i}.wav")
            chunk.export(chunk_filename, format="wav")
            print(f"正在转录分块 {i + 1}/{len(chunks)}: {chunk_filename}")

            # 使用 Whisper 转录每个分块
            fp16_run = device != "cpu"
            result = model.transcribe(chunk_filename, fp16=fp16_run)
            text = result["text"]
            full_text.append(text)
            print(f"分块 {i + 1} 转录完成。")

            # 立即删除已处理的分块文件以节省空间
            try:
                os.remove(chunk_filename)
                print(f"✓ 已删除分块文件: {chunk_filename}")
            except Exception as e:
                print(f"⚠️  删除分块文件时出错: {e}")

        return " ".join(full_text)
    except Exception as e:
        print(f"分段和转录音频时发生错误: {e}")
        return None


def get_filename_without_extension(file_path):
    """
    获取文件名（不包含扩展名和路径）
    """
    base_name = os.path.basename(file_path)  # 获取文件名（包含扩展名）
    filename_without_ext = os.path.splitext(base_name)[0]  # 去除扩展名
    return filename_without_ext


def _apply_ml_punctuation(text, cache_dir=None):
    try:
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            os.environ["HF_HOME"] = cache_dir
            os.environ["HUGGINGFACE_HUB_CACHE"] = os.path.join(cache_dir, "hub")
        from dbpunctuator.inference import Inference, InferenceArguments
        from dbpunctuator.utils import DEFAULT_CHINESE_TAG_PUNCTUATOR_MAP
        args = InferenceArguments(
            model_name_or_path="Qishuai/distilbert_punctuator_zh",
            tokenizer_name="Qishuai/distilbert_punctuator_zh",
            tag2punctuator=DEFAULT_CHINESE_TAG_PUNCTUATOR_MAP
        )
        punctuator = Inference(args)
        res = punctuator.punctuation(text)
        if isinstance(res, str):
            return res
        if isinstance(res, tuple) and len(res) >= 2:
            tokens, tags = res[0], res[1]
            def _norm_tag(t):
                while isinstance(t, list) and len(t) > 0:
                    t = t[0]
                if isinstance(t, (list, tuple)) and len(t) == 0:
                    return None
                if isinstance(t, (int, float)):
                    return str(int(t))
                if t is None:
                    return None
                return str(t)
            local_map = {
                "COMMA": "，", "PERIOD": "。", "QUESTION": "？", "EXCLAMATION": "！",
                "comma": "，", "period": "。", "question": "？", "exclamation": "！",
                "B-COMMA": "，", "B-PERIOD": "。", "B-QUESTION": "？", "B-EXCLAMATION": "！",
                ",": "，", ".": "。", "?": "？", "!": "！",
                "1": "，", "2": "。", "3": "？", "4": "！"
            }
            mapping = DEFAULT_CHINESE_TAG_PUNCTUATOR_MAP or local_map
            buf = []
            out = []
            for tk, tg in zip(tokens, tags):
                s = str(tk).strip()
                if not s:
                    continue
                s = s.replace("。", "").replace("，", "").replace("！", "").replace("？", "").replace(".", "").replace("!", "").replace("?", "")
                if s:
                    buf.append(s)
                nt = _norm_tag(tg)
                punct = mapping.get(nt)
                if isinstance(punct, str) and punct:
                    if punct in [",", "，"]:
                        buf.append("，")
                    else:
                        end = "。" if punct == "." else punct
                        out.append("".join(buf) + end)
                        buf = []
            if buf:
                out.append("".join(buf))
            punct_text = "".join(out)
            if not re.search(r"[，。,\.？！?!]", punct_text):
                tmp = text
                tmp = re.sub(r"(什麼|什么|嗎|吗)(?![。？！?!])", r"\1。", tmp)
                if not re.search(r"[。\.？！?!]$", tmp):
                    tmp = tmp + "。"
                return tmp
            return punct_text
        if isinstance(res, tuple) and len(res) >= 1:
            tokens = res[0]
            if isinstance(tokens, list):
                tmp = "".join(tokens)
                if not re.search(r"[，。,\.？！?!]", tmp):
                    tmp = re.sub(r"(什麼|什么|嗎|吗)(?![。？！?!])", r"\1。", tmp)
                    if not re.search(r"[。\.？！?!]$", tmp):
                        tmp = tmp + "。"
                return tmp
            if isinstance(tokens, str):
                tmp = tokens
                if not re.search(r"[，。,\.？！?!]", tmp):
                    tmp = re.sub(r"(什麼|什么|嗎|吗)(?![。？！?!])", r"\1。", tmp)
                    if not re.search(r"[。\.？！?!]$", tmp):
                        tmp = tmp + "。"
                return tmp
        s = str(res)
        if not re.search(r"[，。,\.？！?!]", s):
            s = re.sub(r"(什麼|什么|嗎|吗)(?![。？！?!])", r"\1。", s)
            if not re.search(r"[。\.？！?!]$", s):
                s = s + "。"
        return s
    except Exception as e:
        print(f"标点恢复失败，将使用原始文本: {e}")
        return None


def process_audio_to_text(audio_path, model_name="base", use_segmentation=False, model_cache_dir=None, use_ml_punctuation=False, ml_cache_dir=None):
    if not os.path.exists(audio_path):
        print(f"错误：音频文件不存在: {audio_path}")
        return False
    audio_name = get_filename_without_extension(audio_path)
    text_output_file = f"{audio_name}.txt"
    print(f"正在处理音频: {audio_path}")
    print(f"输出文本文件将保存为: {text_output_file}")
    transcribed_text = None
    if use_segmentation:
        print("\n--- 正在使用分段转录 ---")
        transcribed_text = split_and_transcribe_audio(
            audio_path,
            output_dir=f"{audio_name}_audio_chunks",
            min_silence_len=700,
            silence_thresh=-35,
            model_name=model_name,
            cache_dir=model_cache_dir
        )
    else:
        print("\n--- 正在使用直接转录 ---")
        transcribed_text = transcribe_audio_with_whisper(audio_path, model_name=model_name, cache_dir=model_cache_dir)
    if use_ml_punctuation and transcribed_text:
        print("\n--- 正在恢复文本标点 ---")
        punctuated_text = _apply_ml_punctuation(transcribed_text, cache_dir=ml_cache_dir)
        if punctuated_text:
            transcribed_text = punctuated_text
    if transcribed_text:
        print("\n--- 转录完成 ---")
        print("转录结果预览:")
        print(transcribed_text[:200] + "..." if len(transcribed_text) > 200 else transcribed_text)
        try:
            with open(text_output_file, "w", encoding="utf-8") as f:
                f.write(transcribed_text)
            print(f"\n转录文本已成功保存到: {text_output_file}")
        except Exception as e:
            print(f"保存文件时发生错误: {e}")
            return False
    else:
        print("转录失败。")
        return False
    try:
        if use_segmentation:
            chunks_dir = f"{audio_name}_audio_chunks"
            if os.path.exists(chunks_dir):
                import shutil
                shutil.rmtree(chunks_dir)
                print(f"已删除临时音频分块目录: {chunks_dir}")
    except Exception as e:
        print(f"清理临时文件时发生警告: {e}")
    return True


def process_video_to_text(video_path, model_name="base", use_segmentation=False, model_cache_dir=None, use_ml_punctuation=False, ml_cache_dir=None):
    """
    处理视频文件，提取音频并转录为文本

    Args:
        video_path: 视频文件路径
        model_name: Whisper模型名称 ("tiny", "base", "small", "medium", "large")
        use_segmentation: 是否使用分段转录（推荐用于长视频）
    """
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print(f"错误：视频文件不存在: {video_path}")
        return False

    # 生成输出文件名
    video_name = get_filename_without_extension(video_path)
    audio_file = f"{video_name}_temp_audio.wav"  # 临时音频文件（WAV，便于语音识别）
    text_output_file = f"{video_name}.txt"  # 输出文本文件

    print(f"正在处理视频: {video_path}")
    print(f"输出文本文件将保存为: {text_output_file}")

    # 1. 从视频中提取音频
    if not extract_audio_from_video(video_path, audio_file):
        print("音频提取失败，无法继续处理。")
        return False

    # 2. 转录音频
    transcribed_text = None

    if use_segmentation:
        print("\n--- 正在使用分段转录 ---")
        transcribed_text = split_and_transcribe_audio(
            audio_file,
            output_dir=f"{video_name}_audio_chunks",
            min_silence_len=700,
            silence_thresh=-35,
            model_name=model_name,
            cache_dir=model_cache_dir
        )
    else:
        print("\n--- 正在使用直接转录 ---")
        transcribed_text = transcribe_audio_with_whisper(audio_file, model_name=model_name, cache_dir=model_cache_dir)
    if use_ml_punctuation and transcribed_text:
        print("\n--- 正在恢复文本标点 ---")
        punctuated_text = _apply_ml_punctuation(transcribed_text, cache_dir=ml_cache_dir)
        if punctuated_text:
            transcribed_text = punctuated_text

    # 3. 保存转录结果
    if transcribed_text:
        print("\n--- 转录完成 ---")
        print("转录结果预览:")
        print(transcribed_text[:200] + "..." if len(transcribed_text) > 200 else transcribed_text)

        try:
            with open(text_output_file, "w", encoding="utf-8") as f:
                f.write(transcribed_text)
            print(f"\n转录文本已成功保存到: {text_output_file}")
        except Exception as e:
            print(f"保存文件时发生错误: {e}")
            return False
    else:
        print("转录失败。")
        return False

    # 4. 清理临时文件
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"已删除临时音频文件: {audio_file}")

        # 如果使用了分段转录，清理分块目录
        if use_segmentation:
            chunks_dir = f"{video_name}_audio_chunks"
            if os.path.exists(chunks_dir):
                import shutil
                shutil.rmtree(chunks_dir)
                print(f"已删除临时音频分块目录: {chunks_dir}")
    except Exception as e:
        print(f"清理临时文件时发生警告: {e}")

    return True


# --- 主要执行部分 ---
if __name__ == "__main__":
    print("请选择输入类型:")
    print("1. 视频文件")
    print("2. 音频文件")
    input_choice = input("请输入选择 (1/2，默认为1): ").strip()
    is_video = input_choice != "2"
    path = input("请输入文件路径: ").strip().strip('"\'')

    if not path:
        print("错误：未提供文件路径")
        exit(1)

    print("\n可用的Whisper模型:")
    print("1. tiny - 最快，准确度最低")
    print("2. base - 平衡速度和准确度（推荐）")
    print("3. small - 较好准确度")
    print("4. medium - 高准确度")
    print("5. large - 最高准确度，需要更多资源")

    model_choice = input("\n请选择模型 (1-5，默认为2): ").strip()

    model_map = {
        "1": "tiny",
        "2": "base",
        "3": "small",
        "4": "medium",
        "5": "large"
    }

    selected_model = model_map.get(model_choice, "base")
    print(f"已选择模型: {selected_model}")

    segmentation_choice = input("\n是否使用分段转录？(适合长音频/长视频，y/N): ").strip().lower()
    use_segmentation = segmentation_choice in ['y', 'yes', '是']

    default_cache = os.path.join(os.getcwd(), ".whisper_cache")
    use_default_cache = input(f"\n是否使用本地缓存目录 {default_cache}？(y/N): ").strip().lower()
    model_cache_dir = None
    if use_default_cache in ['y', 'yes', '是']:
        if not os.path.exists(default_cache):
            os.makedirs(default_cache, exist_ok=True)
        model_cache_dir = default_cache
    else:
        custom_cache = input("请输入自定义缓存目录（留空为系统默认）: ").strip().strip('"\'')
        if custom_cache:
            if not os.path.exists(custom_cache):
                os.makedirs(custom_cache, exist_ok=True)
            model_cache_dir = custom_cache
    ml_punct_choice = input("\n是否使用DistilBERT标点恢复？(y/N): ").strip().lower()
    use_ml_punctuation = ml_punct_choice in ['y', 'yes', '是']
    ml_default_cache = os.path.join(os.getcwd(), ".hf_cache")
    ml_use_default_cache = input(f"\n是否使用DistilBERT本地缓存目录 {ml_default_cache}？(y/N): ").strip().lower()
    ml_cache_dir = None
    if ml_use_default_cache in ['y', 'yes', '是']:
        if not os.path.exists(ml_default_cache):
            os.makedirs(ml_default_cache, exist_ok=True)
        ml_cache_dir = ml_default_cache
    else:
        ml_custom_cache = input("请输入DistilBERT自定义缓存目录（留空为系统默认）: ").strip().strip('\"\'')
        if ml_custom_cache:
            if not os.path.exists(ml_custom_cache):
                os.makedirs(ml_custom_cache, exist_ok=True)
            ml_cache_dir = ml_custom_cache

    if is_video:
        success = process_video_to_text(
            video_path=path,
            model_name=selected_model,
            use_segmentation=use_segmentation,
            model_cache_dir=model_cache_dir,
            use_ml_punctuation=use_ml_punctuation,
            ml_cache_dir=ml_cache_dir
        )
    else:
        success = process_audio_to_text(
            audio_path=path,
            model_name=selected_model,
            use_segmentation=use_segmentation,
            model_cache_dir=model_cache_dir,
            use_ml_punctuation=use_ml_punctuation,
            ml_cache_dir=ml_cache_dir
        )

    if success:
        print("\n🎉 转录完成！")
    else:
        print("\n❌ 转录失败。")
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass
    os._exit(0 if success else 1)
