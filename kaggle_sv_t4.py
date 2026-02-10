# -*- coding: utf-8 -*-
"""
四川话Whisper微调训练 - 优化版（适配Kaggle T4×2）
核心优化：提升训练速度、适配双GPU、减少过拟合
"""

# Step 1: 安装依赖
# !pip install torch transformers torchaudio datasets soundfile jiwer accelerate -q

# Step 2: 导入库
import os
import pandas as pd
import numpy as np
import torch
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)
from transformers.trainer_utils import get_last_checkpoint
from datasets import Dataset, Audio
from dataclasses import dataclass
from typing import Any, Dict, List, Union
import jiwer
import librosa

# Step 3: 配置参数（核心优化）
@dataclass
class Config:
    model_name = "openai/whisper-small"  # Whisper-small模型
    output_dir = "./whisper-sichuan-finetuned"
    dataset_paths = ["/kaggle/input/sichuan/sichuan_dataset"]
    language = "chinese"
    task = "transcribe"
    num_train_epochs = 10  # 小数据集10个epoch足够
    per_device_train_batch_size = 8  # 🔧 优化点：适配T4×2，提升批大小
    per_device_eval_batch_size = 8
    gradient_accumulation_steps = 2  # 🔧 优化点：双GPU下降低梯度累积步数
    learning_rate = 5e-5
    warmup_steps = 500
    max_steps = -1  # 🔧 优化点：禁用max_steps，改用epoch控制训练时长
    fp16 = True  # T4对FP16支持更好
    eval_strategy = "epoch"  # 🔧 优化点：按epoch评估，减少评估次数
    save_strategy = "epoch"  # 🔧 优化点：与评估策略匹配，支持load_best_model_at_end
    save_steps = 100  # 保存步数适配小数据集
    eval_steps = -1  # 禁用step级评估，跟随epoch
    save_total_limit = 2
    logging_steps = 50  # 更频繁查看训练日志
    gradient_checkpointing = False  # 🔧 优化点：禁用梯度检查点避免梯度计算错误
    cache_version = "v1"  # 数据缓存版本号，新增数据时改为新版本
    use_cache = True  # 是否使用缓存，加速重复运行

config = Config()

# 数据整理器（保持原有逻辑）
@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

# Step 4: 加载数据集（优化版：使用datasets.Audio替代librosa）
def load_sichuan_dataset(dataset_paths):
    """加载四川话数据集（优化数据加载速度）"""
    if isinstance(dataset_paths, str):
        dataset_paths = [dataset_paths]
    print(f"📂 正在从 {dataset_paths} 加载数据...")
    
    valid_roots = []
    for root in dataset_paths:
        if os.path.exists(root):
            valid_roots.append(root)
            try:
                print(f"📁 数据集目录内容({root}): {os.listdir(root)}")
            except Exception:
                pass
        else:
            print(f"❌ 数据集根目录不存在: {root}")
    if not valid_roots:
        return None, None, None

    def fix_path(df, root, split_name):
        """修正音频路径"""
        base_dir = os.path.join(root, split_name)
        def make_full_path(x):
            p = str(x)
            if os.path.isabs(p) and os.path.exists(p):
                return p
            return os.path.join(base_dir, p)
        df['audio_path'] = df['audio_path'].apply(make_full_path)
        return df

    try:
        splits = ['train', 'dev', 'test']
        datasets = {s: [] for s in splits}
        
        for root in valid_roots:
            for split in splits:
                csv_path = os.path.join(root, split, "metadata.csv")
                print(f"🔍 检查文件: {csv_path}")
                if not os.path.exists(csv_path):
                    print(f"⚠️ 警告: 找不到 {csv_path}")
                    split_dir = os.path.join(root, split)
                    if os.path.exists(split_dir):
                        try:
                            print(f"📁 {split} 目录存在，内容: {os.listdir(split_dir)}")
                        except Exception:
                            pass
                    else:
                        print(f"❌ {split} 目录不存在")
                    continue
                df = pd.read_csv(csv_path, encoding='utf-8')
                df = fix_path(df, root, split)
                datasets[split].append(df)
        
        result = {}
        for split in splits:
            if not datasets[split]:
                result[split] = None
                continue
            df_all = pd.concat(datasets[split], ignore_index=True)
            df_all = df_all.drop_duplicates(subset=['audio_path'])
            dataset = Dataset.from_pandas(df_all)
            result[split] = dataset
            print(f"✅ 合并 {split} 集: {len(dataset)} 条")
        
        return result.get('train'), result.get('dev'), result.get('test')
    except Exception as e:
        print(f"❌ 加载数据集出错: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

# Step 5: 预处理函数（优化版：使用datasets.Audio的内置加载）
def prepare_dataset(batch, processor):
    """预处理音频数据"""
    audio_path = batch["audio_path"]
    
    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在: {audio_path}")
        return {"input_features": None, "labels": None}

    try:
        # 加载音频
        speech, sr = librosa.load(audio_path, sr=16000)
        
        # 提取特征
        input_features = processor.feature_extractor(
            speech, 
            sampling_rate=16000,
            return_tensors="pt"
        ).input_features[0]
        
        # 编码文本
        labels = processor.tokenizer(batch["transcription"]).input_ids
        
        return {
            "input_features": input_features,
            "labels": labels,
        }
    except Exception as e:
        print(f"❌ 处理音频失败: {audio_path}, 错误: {e}")
        return {"input_features": None, "labels": None}

# Step 6: 中文专用评估指标（保持原有逻辑）
def get_compute_metrics(processor):
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        
        # 确保predictions是numpy数组
        if isinstance(predictions, torch.Tensor):
            predictions = predictions.cpu().numpy()
        if isinstance(labels, torch.Tensor):
            labels = labels.cpu().numpy()
        
        # 替换-100为pad_token_id
        labels = np.where(labels != -100, labels, processor.tokenizer.pad_token_id)
        
        # 解码标签
        label_str = processor.batch_decode(labels, skip_special_tokens=True)
        
        # 处理predictions - 对于Whisper模型，可能需要特殊处理
        try:
            # 尝试直接解码
            pred_str = processor.batch_decode(predictions, skip_special_tokens=True)
        except Exception as e:
            # 如果失败，尝试使用tokenizer直接解码
            print(f"⚠️ 直接解码失败，尝试使用tokenizer解码: {e}")
            pred_str = []
            for pred in predictions:
                try:
                    # 确保pred是一维数组
                    if pred.ndim > 1:
                        pred = pred[0]
                    pred_str.append(processor.tokenizer.decode(pred, skip_special_tokens=True))
                except Exception as inner_e:
                    print(f"⚠️ 单个预测解码失败: {inner_e}")
                    pred_str.append("")
        
        # 中文按字符分割计算CER（字符错误率）
        def char_segmentation(text):
            return " ".join(list(text))
        
        pred_str_seg = [char_segmentation(text) for text in pred_str]
        label_str_seg = [char_segmentation(text) for text in label_str]
        
        # 计算CER和WER
        try:
            cer = jiwer.wer(label_str_seg, pred_str_seg)
            wer = jiwer.wer(label_str, pred_str)
        except Exception as e:
            print(f"⚠️ 计算指标失败: {e}")
            cer = 1.0
            wer = 1.0
        
        return {"cer": cer, "wer": wer}
    return compute_metrics

# Step 7: 主训练流程（优化版）
def main():
    print("🚀 开始四川话Whisper微调训练（适配T4×2）")
    
    # 设置随机种子（保证可复现）
    torch.manual_seed(42)
    np.random.seed(42)
    
    # 1. 加载模型和处理器
    print(f"📦 加载模型: {config.model_name}")
    model = WhisperForConditionalGeneration.from_pretrained(config.model_name)
    processor = WhisperProcessor.from_pretrained(config.model_name)
    
    # 设置语言
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    model.generation_config.task = config.task
    model.generation_config.language = config.language
    
    # 2. 加载数据集
    train_dataset, dev_dataset, test_dataset = load_sichuan_dataset(config.dataset_paths)
    if train_dataset is None:
        print("❌ 无法加载数据集，程序退出")
        return
    
    print(f"📊 数据集统计: Train={len(train_dataset)}, Dev={len(dev_dataset)}, Test={test_dataset and len(test_dataset)}")
    
    # 3. 预处理（🔧 优化点：添加缓存，避免重复处理）
    print("🔧 预处理数据...")
    
    # 使用缓存加速预处理，num_proc适配Kaggle CPU
    train_dataset = train_dataset.map(
        lambda x: prepare_dataset(x, processor),
        remove_columns=train_dataset.column_names,
        num_proc=2,
        load_from_cache_file=config.use_cache,
        cache_file_name=os.path.join(config.output_dir, f"train_cache_{config.cache_version}.arrow")
    )
    dev_dataset = dev_dataset.map(
        lambda x: prepare_dataset(x, processor),
        remove_columns=dev_dataset.column_names,
        num_proc=2,
        load_from_cache_file=config.use_cache,
        cache_file_name=os.path.join(config.output_dir, f"dev_cache_{config.cache_version}.arrow")
    )
    
    # 过滤无效数据
    train_dataset = train_dataset.filter(lambda x: x["input_features"] is not None)
    dev_dataset = dev_dataset.filter(lambda x: x["input_features"] is not None)
    
    print(f"✅ 预处理完成: Train={len(train_dataset)}, Dev={len(dev_dataset)}")
    
    # 4. 数据整理器
    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)
    
    # 5. 训练参数（核心优化）
    training_args = Seq2SeqTrainingArguments(
        output_dir=config.output_dir,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=config.per_device_eval_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        max_steps=config.max_steps,
        num_train_epochs=config.num_train_epochs,
        fp16=config.fp16,
        eval_strategy=config.eval_strategy,
        save_strategy=config.save_strategy,
        save_steps=config.save_steps,
        eval_steps=config.eval_steps,
        logging_steps=config.logging_steps,
        save_total_limit=config.save_total_limit,
        gradient_checkpointing=config.gradient_checkpointing,
        load_best_model_at_end=True,
        metric_for_best_model="cer",
        greater_is_better=False,
        predict_with_generate=True,  # 评估时需要生成预测
        generation_max_length=225,
        report_to="none",  # Kaggle禁用wandb
        # 🔧 优化点：双GPU训练相关配置
        ddp_find_unused_parameters=False,  # 适配双GPU
        dataloader_pin_memory=False,  # 减少内存占用
    )
    
    # 6. 创建Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        processing_class=processor,
        data_collator=data_collator,
        compute_metrics=get_compute_metrics(processor),
    )
    
    print("🧪 训练前快速评估...")
    trainer.evaluate()
    
    # 7. 开始训练
    print("🏃 开始训练...")
    last_ckpt = get_last_checkpoint(config.output_dir)
    if last_ckpt:
        print(f"🔁 发现检查点，续训: {last_ckpt}")
        trainer.train(resume_from_checkpoint=last_ckpt)
    else:
        trainer.train()
    
    # 8. 保存模型
    print("💾 保存模型...")
    model.save_pretrained(f"{config.output_dir}/final")
    processor.save_pretrained(f"{config.output_dir}/final")
    
    # 9. 在测试集上评估（如果有，评估时开启生成）
    if test_dataset:
        print("🧪 在测试集上评估...")
        test_dataset = test_dataset.map(
            lambda x: prepare_dataset(x, processor),
            remove_columns=test_dataset.column_names,
            num_proc=2,
            load_from_cache_file=config.use_cache,
            cache_file_name=os.path.join(config.output_dir, f"test_cache_{config.cache_version}.arrow")
        )
        test_dataset = test_dataset.filter(lambda x: x["input_features"] is not None)
        
        # 评估时临时开启生成
        trainer.args.predict_with_generate = True
        test_results = trainer.evaluate(test_dataset)
        print(f"📊 测试集结果: {test_results}")
    
    # 10. 打包模型
    print("📦 打包模型...")
    os.makedirs(config.output_dir, exist_ok=True)
    os.system(f"cd {config.output_dir} && zip -r ../whisper-sichuan-model.zip final/")
    
    print("✅ 训练完成！模型已打包为 whisper-sichuan-model.zip")

if __name__ == "__main__":
    # 创建输出目录
    os.makedirs(config.output_dir, exist_ok=True)
    main()
