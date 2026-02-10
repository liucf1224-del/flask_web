# 项目结构说明

## 📁 目录结构

```
.
├── demo/                           # 🎯 核心Flask应用模块
│   ├── controller/                 # 🎮 控制器层，处理业务逻辑
│   │   ├── app.py                  # Flask应用初始化
│   │   ├── auth_controller.py      # 认证相关控制器
│   │   ├── copyright_controller.py # 版权相关控制器
│   │   ├── dingtalk_controller.py  # 钉钉消息推送控制器
│   │   ├── main.py                 # 主入口文件
│   │   ├── ollama_controller.py    # Ollama AI相关控制器
│   │   ├── user_controller.py      # 用户相关控制器
│   │   ├── video_controller.py     # 视频处理相关控制器
│   │   ├── yeepay_controller.py    # 易宝支付控制器
│   │   └── yolo_controller.py      # YOLO模型相关控制器
│   ├── model/                      # 🗄️ 数据模型层
│   │   ├── copyright.py            # 版权模型
│   │   ├── dd.py                   # 其他数据模型
│   │   └── user.py                 # 用户模型
│   ├── routes/                     # 🚦 路由定义
│   │   ├── auth_routes.py          # 认证路由
│   │   ├── celery_routes.py        # Celery任务路由
│   │   ├── copyright_routes.py     # 版权路由
│   │   ├── dingtalk_routes.py      # 钉钉消息推送路由
│   │   ├── email_routes.py         # 邮件路由
│   │   ├── ffmpeg_routes.py        # FFmpeg路由
│   │   ├── redis_routes.py         # Redis路由
│   │   ├── user_routes.py          # 用户路由
│   │   ├── yolo_routes.py          # YOLO路由
│   │   └── yolo_view_routes.py     # YOLO视图路由
│   ├── server/                     # ⚙️ 服务层
│   │   ├── crawler_tasks.py        # 爬虫任务
│   │   └── task_server.py          # 任务服务
│   ├── utils/                      # 🛠️ 工具类
│   │   ├── crawler.py              # 爬虫工具
│   │   ├── email.py                # 邮件工具
│   │   ├── redis_own.py            # Redis工具
│   │   ├── respose_utils.py        # 响应工具
│   │   ├── yeepay_client.py        # 易宝支付客户端
│   │   └── test.py                 # 测试工具
│   ├── templates/                  # 📄 模板文件
│   │   ├── ollama/
│   │   │   └── ai_chat.html        # AI聊天模板
│   │   └── yolo/
│   │       └── yolo_demo.html      # YOLO演示模板
│   ├── __init__.py                 # 模块初始化文件
│   ├── celery.py                   # Celery配置
│   └── setting.py                  # 应用设置
├── small/                          # 🔧 小工具脚本
│   └── change.py                   # 辅助脚本
├── logs/                           # 📊 日志目录
├── templates/                      # 📄 外部模板目录
│   └── ollama/
│       ├── ai_chat.html
│       └── chat.html
├── 🌟 重点项目/
│   ├── binlog_sync.py              # 🔄 MySQL Binlog监听同步到StarRocks
│   ├── image_format.py             # 🖼️ 图片格式转换工具
│   ├── image_matting.py            # ✂️ 基于本地模型的图片抠图
│   ├── voice_to_sentence.py        # 🎵 语音转文字（支持方言训练）
│   ├── udp_send.py                 # 📡 UDP消息发送Demo
│   ├── KTVOrderScraper.py          # 🕸️ KTV订单数据爬取与存储
│   ├── kaggle_sv_t4.py             # 🚀 Kaggle T4×2方言模型训练
│   ├── sichuan_supplement.py       # 📚 四川话训练语料库
│   ├── t4_old_kaggle.py            # ⚡ Kaggle单卡模型训练
│   └── test_ping.py                # 🧪 数据库连接测试
├── ai.py                           # 🤖 AI相关功能
├── async.py                        # ⏱️ 异步处理
├── celery_instance.py              # 📦 Celery实例
├── environment.yml                 # 🐍 Conda环境配置文件
├── flsk_async.py                   # ⚡ Flask异步处理
├── model_info.py                   # 📋 模型信息
├── model_test.py                   # 🧪 模型测试
├── quen.py                         # 📥 队列处理
├── requirements.txt                # 📦 Pip依赖文件
├── requirements_freeze.txt         # 🔒 冻结的依赖文件
├── run.py                          # ▶️ 运行入口
├── test.py                         # 🧪 测试文件
└── video_audio_processor.py        # 🎞️ 音视频处理器

```

## 📋 文件功能详解

### 🌟 重点项目

#### `binlog_sync.py` 🔄
**功能**: MySQL Binlog实时监听与数据同步
- 监听MySQL的binlog变更事件
- 实时同步数据到StarRocks数据仓库
- 支持断点续传和错误重试机制
- 适用于数据仓库实时ETL场景

#### `image_format.py` 🖼️
**功能**: 图片格式智能转换
- 支持JPEG、PNG、WEBP等多种格式互转
- 自动处理透明度和色彩模式转换
- 保持图片质量和优化压缩
- 适用于图片处理流水线

#### `image_matting.py` ✂️
**功能**: 智能图片抠图
- 基于U²Net本地模型进行背景移除
- 支持透明PNG输出
- 保留边缘细节和透明通道
- ⚠️ 注意：模型默认存储在C盘，可配置路径

#### `voice_to_sentence.py` 🎵
**功能**: 语音转文字解决方案
- 支持视频和音频文件处理
- 集成Whisper模型进行语音识别
- 包含中文分词和标点恢复
- 🎯 重点：正在训练四川话专用模型
- 适用场景：方言语音识别、会议记录、字幕生成

#### `udp_send.py` 📡
**功能**: UDP网络通信Demo
- 简单的UDP消息发送和接收示例
- 支持JSON格式数据传输
- 包含超时和错误处理机制
- 适用于物联网设备通信测试

#### `KTVOrderScraper.py` 🕸️
**功能**: KTV订单数据采集系统
- 爬取KTV订单管理系统数据
- 支持分页数据抓取和进度保存
- 多种格式输出（CSV、Excel、JSON、TXT）
- 适用于商业数据分析场景

#### `kaggle_sv_t4.py` 🚀
**功能**: Kaggle T4×2分布式训练
- 优化的方言语音模型训练脚本
- 适配双GPU并行训练
- 包含数据缓存和性能优化
- 支持训练进度监控和模型打包

#### `sichuan_supplement.py` 📚
**功能**: 四川话训练语料库
- 包含1000+条四川话常用语句
- 按场景分类（问候、购物、餐饮等）
- 为方言模型训练提供高质量数据
- 持续更新和扩充中

#### `t4_old_kaggle.py` ⚡
**功能**: Kaggle单卡训练脚本
- 适用于单GPU训练环境
- 相比双卡版本配置更简单
- 可能需要进一步调优以提升训练速度

#### `test_ping.py` 🧪
**功能**: 数据库连接健康检查
- 测试MySQL和StarRocks连接状态
- 快速验证环境配置正确性
- 适用于部署前的环境检查

> [YOLOv8](https://github.com/ultralytics/ultralytics)

> 识别图片模型来说一个是yolo 一个是RFDETR-base 前者更多是速度和监控一体 

> 后者是Transformer 架构在实时检测领域的创新尝试，在精度和复杂场景适应上超越 YOLO

> [YOLOv8](https://github.com/ultralytics/ultralytics)

> 识别图片模型来说一个是yolo 一个是RFDETR-base 前者更多是速度和监控一体 

> 后者是Transformer 架构在实时检测领域的创新尝试，在精度和复杂场景适应上超越 YOLO

## 模型文件说明

### 1. yolov8n.pt 基类的文件校验

### 2. yolo8_helm_best.pt 这个是安全帽的校验文件

```
专门用于安全帽检测的模型
类别：{0: 'pakai helm', 1: 'tanpa helm'}
来源：Kaggle平台训练的专用模型
适合当前的安全帽检测需
```

### 3. yolo8s_best_best.onnx 

```
模型类型: ONNX格式的目标检测模型 (task=detect)
检测类别: 3个音乐乐器类别
0: 'cello' (大提琴)
1: 'guitar' (吉他)
2: 'violon' (小提琴)
推理引擎: 使用ONNX Runtime进行CPU推理
```

### 4. yolov8x_person_face.pt
[下载链接-大于100m需要改git上传逻辑直接放到谷歌云盘](https://drive.google.com/file/d/1nH_CaDv7bTGbXR64NH9BMLtlvXOugcsk/view?usp=drive_link)
```
检测类别: 专门用于检测两类目标：
0: 'person' (人体)
1: 'face' (人脸)
模型配置: 基于YOLOv8x架构，输入图像尺寸为640×640
```

## 易宝支付功能

项目集成了易宝支付(Yeepay)功能，支持微信小程序支付流程：

### 主要特性
- 支持微信小程序支付
- 支持支付订单查询
- 支持发起退款请求

### 接口说明
- `POST /yeepay/pay` - 创建支付订单
- `GET /yeepay/query/<order_id>` - 查询支付结果
- `POST /yeepay/refund` - 发起退款

### 环境配置
需要在环境变量中配置以下易宝支付相关参数：
- `PRIMARY_KEY` - 商户私钥
- `PUBLIC_KEY` - 易宝公钥
- `MERCHANT_NO` - 商户账号
- `MERCHANT_APP_KEY` - 商户编号
- `APP_ID` - 微信小程序/公众号appId

## 功能参考拓展

人脸识别+对比这种

```
第一阶段: 使用 YOLO 等检测模型定位图像中的人脸区域
第二阶段: 第二阶段: 使用 FaceNet 或 ArcFace 等识别模型提取人脸特征并与数据库比对
FaceNet: Google开发的人脸识别系统，基于深度学习提取人脸特征向量
ArcFace: 旷视科技开发的高精度人脸识别算法，支持大规模人脸比对
InsightFace: 开源的人脸分析工具包，包含多种识别模型
```

## 钉钉消息推送功能

项目实现了将热点分析报告通过钉钉机器人推送到群聊的功能：

### 主要特性
- 支持将热点分析报告推送到钉钉群聊
- 提供测试接口验证推送功能
- 支持多种报告类型（当日汇总、增量更新等）
- 格式化消息内容，便于阅读

### 接口说明
- `POST /dingtalk/send_report` - 发送热点分析报告到钉钉
- `GET /dingtalk/test` - 测试钉钉消息发送

### 环境配置
需要在环境变量中配置 `DING_TALK`，值为钉钉机器人的Webhook URL。

---

## 环境配置说明

环境包导出 本地和生产环境 本地用conda线上是linux大部分是uv

```
环境配置文件使用场景
environment.yml
适用于本地 conda 环境
包含完整的环境配置，包括 Python 版本和所有依赖
跨平台兼容性好，特别是处理二进制包时
使用命令：conda env create -f environment.yml
创建命令:  conda env export > environment.yml 

requirements.txt
适用于 Linux 服务器部署
轻量级，只包含必要的 pip 包
标准的 Python 依赖管理方式
使用命令：pip install -r requirements.txt
创建命令:  
1.pip freeze > requirements.txt 但是这个会比较多，需要2次精简
2.也是在本环境下去操作
# 安装 pipreqs
pip install pipreqs

# 自动生成项目依赖（只扫描实际使用的包）
pipreqs . --encoding=utf8

# 强制覆盖已存在的 requirements.txt
pipreqs . --force --encoding=utf8
```



os 模块是 Python 标准库中的一个重要模块，它提供了一种使用操作系统相关功能的方式，例如读写文件、管理进程、获取环境变量等。以下是一些常见的 os 模块操作：
1. 文件与目录操作
os.getcwd()：获取当前工作目录。
os.chdir(path)：改变当前工作目录到指定路径 path。
os.listdir(path='.')：返回一个包含指定路径下所有文件和子目录名称的列表。
os.mkdir(path[, mode])：创建单个目录。
os.makedirs(name[, mode])：递归创建多层目录。
os.remove(path)：删除一个文件。
os.rmdir(path)：删除一个空目录。
os.removedirs(path)：递归删除空目录。
os.rename(src, dst)：重命名文件或目录。
2. 路径操作
os.path.join(path, *paths)：将多个路径组合成一个完整的路径。
os.path.exists(path)：判断路径是否存在。
os.path.isfile(path)：检查是否为文件。
os.path.isdir(path)：检查是否为目录。
os.path.basename(path)：返回路径中最后的部分（即文件名或最后一级目录名）。
os.path.dirname(path)：返回路径中的目录部分。
os.path.split(path)：分割路径为 (head, tail) 其中 tail 是最后一个路径组件。
3. 环境变量
os.getenv(key[, default])：获取环境变量值。
os.putenv(key, value)：设置环境变量。
os.unsetenv(key)：取消设置环境变量。
os.environ：一个表示环境变量的字典对象。
4. 进程管理
os.system(command)：执行 shell 命令。
os.popen(cmd[, mode[, bufsize]])：打开一个管道用于读取或写入数据。
os.spawnl(mode, path, ...) 和其他 spawn* 函数：启动新的进程。
os.kill(pid, sig)：向进程发送信号。
os.getpid()：获取当前进程 ID。
os.getppid()：获取父进程 ID。
5. 权限控制
os.chmod(path, mode)：更改文件权限。
os.access(path, mode)：测试对文件的访问权限。
以上只是 os 模块的一部分常用功能，更多详细信息可以查阅官方文档或者通过帮助命令 help(os) 获取。