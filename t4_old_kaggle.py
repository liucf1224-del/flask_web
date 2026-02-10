# -- coding: utf-8 -- 老版本的t4
# """ 四川话Whisper微调训练 - 修正版 在Kaggle上运行 """

# Step 1: 安装依赖
# !pip install torch transformers torchaudio datasets soundfile jiwer accelerate -q
# Step 2: 导入库
# import os import pandas as pd import numpy as np import torch from transformers import ( WhisperForConditionalGeneration, WhisperProcessor, Seq2SeqTrainer, Seq2SeqTrainingArguments ) from datasets import Dataset, Audio import librosa from dataclasses import dataclass from typing import Any, Dict, List, Union import jiwer

# Step 3: 配置参数
# @dataclass class Config: model_name = "openai/whisper-small" # 建议使用small，base效果有限 output_dir = "./whisper-sichuan-finetuned" dataset_path = "/kaggle/input/sichuan/sichuan_dataset" # 你的数据集名称 language = "chinese" task = "transcribe" num_train_epochs = 10 # 增加epoch数 per_device_train_batch_size = 4 # Kaggle P100显存较小，减小batch per_device_eval_batch_size = 4 gradient_accumulation_steps = 4 learning_rate = 5e-5 warmup_steps = 500 max_steps = 4000 fp16 = True eval_strategy = "steps" save_steps = 500 eval_steps = 500 save_total_limit = 2 logging_steps = 100 gradient_checkpointing = False

# config = Config()

# 数据整理器
# @dataclass class DataCollatorSpeechSeq2SeqWithPadding: processor: Any

# def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
#     input_features = [{"input_features": feature["input_features"]} for feature in features]
#     batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

#     label_features = [{"input_ids": feature["labels"]} for feature in features]
#     labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

#     labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

#     if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
#         labels = labels[:, 1:]

#     batch["labels"] = labels
#     return batch
# Step 4: 加载数据集（修正版）
# def load_sichuan_dataset(dataset_path): """加载四川话数据集""" print(f"📂 正在从 {dataset_path} 加载数据...")

# # 检查数据集根目录是否存在
# if not os.path.exists(dataset_path):
#     print(f"❌ 数据集根目录不存在: {dataset_path}")
#     return None, None, None

# # 列出数据集目录内容
# print(f"📁 数据集目录内容: {os.listdir(dataset_path)}")

# def fix_path(df, split_name):
#     """修正音频路径：假设结构是 {split_name}/audio/xxx.wav"""
#     base_dir = os.path.join(dataset_path, split_name)
    
#     # 检查audio_path列是否包含完整路径
#     sample_path = str(df.iloc[0]['audio_path'])
    
#     # 如果已经是绝对路径且存在，直接返回
#     if os.path.exists(sample_path):
#         return df
    
#     # 否则，修正为完整路径
#     def make_full_path(x):
#         # 如果x是相对路径（如audio/xxx.wav），直接拼接
#         return os.path.join(base_dir, x)
    
#     df['audio_path'] = df['audio_path'].apply(make_full_path)
#     return df

# try:
#     # 读取三个分区的metadata
#     splits = ['train', 'dev', 'test']
#     datasets = {}
    
#     for split in splits:
#         csv_path = os.path.join(dataset_path, split, "metadata.csv")
#         print(f"🔍 检查文件: {csv_path}")
        
#         if not os.path.exists(csv_path):
#             print(f"⚠️ 警告: 找不到 {csv_path}")
#             # 尝试检查split目录是否存在
#             split_dir = os.path.join(dataset_path, split)
#             if os.path.exists(split_dir):
#                 print(f"📁 {split} 目录存在，内容: {os.listdir(split_dir)}")
#             else:
#                 print(f"❌ {split} 目录不存在")
#             continue
            
#         df = pd.read_csv(csv_path, encoding='utf-8')
#         df = fix_path(df, split)
        
#         # 创建Dataset
#         dataset = Dataset.from_pandas(df)
#         datasets[split] = dataset
#         print(f"✅ 加载 {split} 集: {len(dataset)} 条")
    
#     return datasets.get('train'), datasets.get('dev'), datasets.get('test')
# except Exception as e:
#     print(f"❌ 加载数据集出错: {e}")
#     import traceback
#     traceback.print_exc()
#     return None, None, None
# Step 5: 预处理函数
# def prepare_dataset(batch, processor): """预处理音频数据""" audio_path = batch["audio_path"]

# if not os.path.exists(audio_path):
#     print(f"❌ 文件不存在: {audio_path}")
#     return {"input_features": None, "labels": None}

# try:
#     # 加载音频
#     speech, sr = librosa.load(audio_path, sr=16000)
    
#     # 提取特征
#     input_features = processor.feature_extractor(
#         speech, 
#         sampling_rate=16000,
#         return_tensors="pt"
#     ).input_features[0]
    
#     # 编码文本
#     labels = processor.tokenizer(batch["transcription"]).input_ids
    
#     return {
#         "input_features": input_features,
#         "labels": labels,
#     }
# except Exception as e:
#     print(f"❌ 处理音频失败: {audio_path}, 错误: {e}")
#     return {"input_features": None, "labels": None}
# Step 6: 中文专用评估指标
# def compute_metrics(eval_pred): predictions, labels = eval_pred

# # 替换-100为pad_token_id
# labels = np.where(labels != -100, labels, processor.tokenizer.pad_token_id)

# # 解码
# pred_str = processor.batch_decode(predictions, skip_special_tokens=True)
# label_str = processor.batch_decode(labels, skip_special_tokens=True)

# # 中文按字符分割计算CER（字符错误率）
# def char_segmentation(text):
#     # 简单的按字符分割
#     return " ".join(list(text))

# pred_str_seg = [char_segmentation(text) for text in pred_str]
# label_str_seg = [char_segmentation(text) for text in label_str]

# # 计算CER
# cer = jiwer.wer(label_str_seg, pred_str_seg)

# # 也可以计算原始WER（词错误率）
# wer = jiwer.wer(label_str, pred_str)

# return {"cer": cer, "wer": wer}
# Step 7: 主训练流程
# def main(): print("🚀 开始四川话Whisper微调训练")

# # 设置随机种子
# torch.manual_seed(42)
# np.random.seed(42)

# # 1. 加载模型
# print(f"📦 加载模型: {config.model_name}")
# model = WhisperForConditionalGeneration.from_pretrained(config.model_name)
# processor = WhisperProcessor.from_pretrained(config.model_name)

# # 设置语言
# model.config.forced_decoder_ids = None
# model.config.suppress_tokens = []

# # 2. 加载数据集
# train_dataset, dev_dataset, test_dataset = load_sichuan_dataset(config.dataset_path)
# if train_dataset is None:
#     print("❌ 无法加载数据集，程序退出")
#     return

# print(f"📊 数据集统计: Train={len(train_dataset)}, Dev={len(dev_dataset)}, Test={test_dataset and len(test_dataset)}")

# # 3. 预处理
# print("🔧 预处理数据...")

# # 使用多进程预处理
# train_dataset = train_dataset.map(
#     lambda x: prepare_dataset(x, processor),
#     remove_columns=train_dataset.column_names,
#     num_proc=2  # Kaggle CPU有限，不要设置太高
# )
# dev_dataset = dev_dataset.map(
#     lambda x: prepare_dataset(x, processor),
#     remove_columns=dev_dataset.column_names,
#     num_proc=2
# )

# # 过滤无效数据
# train_dataset = train_dataset.filter(lambda x: x["input_features"] is not None)
# dev_dataset = dev_dataset.filter(lambda x: x["input_features"] is not None)

# print(f"✅ 预处理完成: Train={len(train_dataset)}, Dev={len(dev_dataset)}")

# # 4. 数据整理器
# data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

# # 5. 训练参数
# training_args = Seq2SeqTrainingArguments(
#     output_dir=config.output_dir,
#     per_device_train_batch_size=config.per_device_train_batch_size,
#     per_device_eval_batch_size=config.per_device_eval_batch_size,
#     gradient_accumulation_steps=config.gradient_accumulation_steps,
#     learning_rate=config.learning_rate,
#     warmup_steps=config.warmup_steps,
#     max_steps=config.max_steps,
#     fp16=config.fp16,
#     eval_strategy=config.eval_strategy,
#     save_steps=config.save_steps,
#     eval_steps=config.eval_steps,
#     logging_steps=config.logging_steps,
#     save_total_limit=config.save_total_limit,
#     gradient_checkpointing=config.gradient_checkpointing,
#     load_best_model_at_end=True,
#     metric_for_best_model="cer",  # 使用CER作为主要指标
#     greater_is_better=False,
#     predict_with_generate=True,
#     generation_max_length=225,
#     report_to="none",  # Kaggle上禁用wandb/tensorboard
# )

# # 6. 创建Trainer
# trainer = Seq2SeqTrainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=dev_dataset,
#     tokenizer=processor.feature_extractor,
#     data_collator=data_collator,
#     compute_metrics=compute_metrics,
# )

# # 7. 开始训练
# print("🏃 开始训练...")
# trainer.train()

# # 8. 保存模型
# print("💾 保存模型...")
# model.save_pretrained(f"{config.output_dir}/final")
# processor.save_pretrained(f"{config.output_dir}/final")

# # 9. 在测试集上评估（如果有）
# if test_dataset:
#     print("🧪 在测试集上评估...")
#     test_dataset = test_dataset.map(
#         lambda x: prepare_dataset(x, processor),
#         remove_columns=test_dataset.column_names,
#         num_proc=2
#     )
#     test_dataset = test_dataset.filter(lambda x: x["input_features"] is not None)
    
#     test_results = trainer.evaluate(test_dataset)
#     print(f"📊 测试集结果: {test_results}")

# # 10. 打包模型
# print("📦 打包模型...")
# os.system(f"cd {config.output_dir} && zip -r ../whisper-sichuan-model.zip final/")

# print("✅ 训练完成！")
# if name == "main": main()