# 项目结构说明

## 目录结构

```
.
├── demo/                           # 核心应用模块
│   ├── controller/                 # 控制器层，处理业务逻辑
│   │   ├── app.py                  # Flask应用初始化
│   │   ├── auth_controller.py      # 认证相关控制器
│   │   ├── copyright_controller.py # 版权相关控制器
│   │   ├── main.py                 # 主入口文件
│   │   ├── ollama_controller.py    # Ollama AI相关控制器
│   │   ├── user_controller.py      # 用户相关控制器
│   │   ├── video_controller.py     # 视频处理相关控制器
│   │   └── yolo_controller.py      # YOLO模型相关控制器
│   ├── model/                      # 数据模型层
│   │   ├── copyright.py            # 版权模型
│   │   ├── dd.py                   # 其他数据模型
│   │   └── user.py                 # 用户模型
│   ├── routes/                     # 路由定义
│   │   ├── auth_routes.py          # 认证路由
│   │   ├── celery_routes.py        # Celery任务路由
│   │   ├── copyright_routes.py     # 版权路由
│   │   ├── email_routes.py         # 邮件路由
│   │   ├── ffmpeg_routes.py        # FFmpeg路由
│   │   ├── redis_routes.py         # Redis路由
│   │   ├── user_routes.py          # 用户路由
│   │   ├── yolo_routes.py          # YOLO路由
│   │   └── yolo_view_routes.py     # YOLO视图路由
│   ├── server/                     # 服务层
│   │   ├── crawler_tasks.py        # 爬虫任务
│   │   └── task_server.py          # 任务服务
│   ├── utils/                      # 工具类
│   │   ├── crawler.py              # 爬虫工具
│   │   ├── email.py                # 邮件工具
│   │   ├── redis_own.py            # Redis工具
│   │   ├── respose_utils.py        # 响应工具
│   │   └── test.py                 # 测试工具
│   ├── templates/                  # 模板文件
│   │   ├── ollama/
│   │   │   └── ai_chat.html        # AI聊天模板
│   │   └── yolo/
│   │       └── yolo_demo.html      # YOLO演示模板
│   ├── __init__.py                 # 模块初始化文件
│   ├── celery.py                   # Celery配置
│   └── setting.py                  # 应用设置
├── small/                          # 小工具脚本
│   └── change.py                   # 辅助脚本
├── logs/                           # 日志目录
├── templates/                      # 外部模板目录
│   └── ollama/
│       ├── ai_chat.html
│       └── chat.html
├── ai.py                           # AI相关功能
├── async.py                        # 异步处理
├── celery_instance.py              # Celery实例
├── environment.yml                 # Conda环境配置文件
├── flsk_async.py                   # Flask异步处理
├── model_info.py                   # 模型信息
├── model_test.py                   # 模型测试
├── quen.py                         # 队列处理
├── requirements.txt                # Pip依赖文件
├── requirements_freeze.txt         # 冻结的依赖文件
├── run.py                          # 运行入口
├── test.py                         # 测试文件
└── video_audio_processor.py        # 音视频处理器

```

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

## 功能参考拓展

人脸识别+对比这种

```
第一阶段: 使用 YOLO 等检测模型定位图像中的人脸区域
第二阶段: 第二阶段: 使用 FaceNet 或 ArcFace 等识别模型提取人脸特征并与数据库比对
FaceNet: Google开发的人脸识别系统，基于深度学习提取人脸特征向量
ArcFace: 旷视科技开发的高精度人脸识别算法，支持大规模人脸比对
InsightFace: 开源的人脸分析工具包，包含多种识别模型
```

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