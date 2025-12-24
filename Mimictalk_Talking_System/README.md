# TALKING SYSTEM GROUP1 前端介绍
一个结合 Flask 前端和 FastAPI 后端的语音克隆与视频生成系统，支持本地部署和使用。

## 使用指南
- 请先使用pip install -r requirements.txt 安装依赖
- 请先配置好DeepSeek API Key，参考目录下的示例填写好API，修改名字为api_key.py。或者可以自行修改代码使用其他API
- 确保前端端口（默认5000）和后端端口（默认8083）可用
- 新建两个独立终端，一个cd backend后执行python main.py启动后端，另一个在当前目录执行python app.py启动前端
- 进入弹出的前端地址（默认http://localhost:5000）即可开始使用啦！

## 功能特性

### 1. 首页

- 三个主要功能选项的选择页面
- 美观的卡片式界面设计
- 快速导航到相应功能页面
- 字体切换功能（支持默认、衬线体、无衬线体、等宽字体、手写体）
- 新手教程系统入口，指导用户快速上手各功能页面

### 2. 模型训练页面

- **参数设置**：
  - 模型名称选择（默认 SyncTalk）
  - 参考视频地址输入/上传
  - GPU 选择（GPU0-GPU3）
  - 自定义训练参数输入（JSON格式）
  
- **功能**：
  - 点击训练按钮启动训练
  - 实时进度条展示
  - 训练完成后在左侧显示训练视频
  - 支持新手引导教程，详细介绍各参数功能和使用方法

### 3. 视频生成页面

- **参数设置**：
  - 模型名称选择（默认 SyncTalk）
  - 模型目录地址输入
  - 参考音频地址输入/上传
  - 参考视频地址输入/上传
  - GPU 选择
  - 目标文字输入
  - 音频升降调设置
  - 视频速度调整

- **功能**：
  - 点击生成视频按钮启动生成
  - 实时进度条展示
  - 生成完成后在左侧显示视频
  - 支持新手引导教程，详细介绍各参数功能和使用方法

### 4. 实时对话页面

- **配置参数**：
  - 模型名称选择（默认 SyncTalk）
  - 模型目录地址输入
  - 参考音频地址输入/上传
  - 参考视频地址输入/上传
  - GPU 选择

- **功能**：
  - 左侧显示语音克隆人物视频
  - 右侧进行文本对话交互
  - 实时消息显示和时间戳
  - 停止对话按钮
  - 支持新手引导教程，详细介绍各参数功能和使用方法





## 项目结构

```
├── app.py                      # Flask 主应用文件
├── requirements.txt            # Python 依赖文件
├── backend/                    # 后端服务目录
│   ├── main.py                # FastAPI 主应用
│   ├── utils.py               # 工具函数
│   ├── config.py              # 配置文件
│   ├── video_generator.py     # 视频生成模块
│   ├── voice.py               # 语音克隆模块
│   ├── video_audio_processor.py # 视频音频处理模块
│   ├── data/                  # 数据存储目录
│   ├── temp/                  # 临时文件目录
│   ├── local_ckpts/           # 本地模型检查点
│   └── train_logs/            # 训练日志
├── templates/                  # HTML 模板文件
│   ├── index.html             # 主页
│   ├── train.html             # 模型训练页面
│   ├── generate.html          # 视频生成页面
│   └── chat.html              # 实时对话页面
├── static/                     # 静态资源
│   ├── css/                   # CSS 样式文件
│   │   ├── style.css          # 全局样式
│   │   ├── common.css         # 通用样式
│   │   ├── train.css          # 训练页面样式
│   │   ├── generate.css       # 生成页面样式
│   │   └── chat.css           # 对话页面样式
│   ├── js/                    # JavaScript 脚本
│   │   ├── ui.js              # 通用 UI 功能
│   │   ├── train.js           # 训练页面脚本
│   │   ├── generate.js        # 生成页面脚本
│   │   ├── chat.js            # 对话页面脚本
│   │   └── webrtc.js          # WebRTC 相关功能
│   └── videos/                # 视频存储目录
├── uploads/                   # 文件上传目录
├── SyncTalk/                  # SyncTalk 模型目录
│   ├── Dockerfile             # Docker 配置
│   └── run_synctalk.sh        # 模型运行脚本
└── .gitignore                 # Git 忽略文件
```

## 安装及运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行后端服务

```bash
cd backend
python main.py
```

后端服务默认运行在 `http://localhost:8000`

### 3. 运行前端应用

在新的终端窗口中：

```bash
python app.py
```

前端应用默认运行在 `http://localhost:5000`

### 4. 访问应用

在浏览器中打开 `http://localhost:5000`

## API 接口

### 1. 获取可用模型和配置

```python
GET /api/models
```

### 2. 开始训练

```python
POST /api/train
Content-Type: multipart/form-data

{
    "model_name": "SyncTalk",
    "reference_video": <文件上传>,
    "gpu": "GPU0",
    "custom_params": "{\"max_updates\": 10}"
}
```

### 3. 生成视频

```python
POST /api/generate
Content-Type: multipart/form-data

{
    "model_name": "SyncTalk",
    "model_dir": "/path/to/model",
    "reference_audio": <文件上传>,
    "reference_video": <文件上传>,
    "gpu": "GPU0",
    "target_text": "生成的文字",
    "pitch": 1.0,  # 音频升降调
    "speed": 1.0    # 视频速度调整
}
```

### 4. 获取任务状态

```python
GET /api/task/<task_id>
```

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript（原生）
- **后端框架**：Flask + FastAPI
- **音频处理**：FFmpeg
- **模型**：SyncTalk
- **数据传输**：JSON REST API
- **文件处理**：Python 文件操作
- **核心特性**：
  - 语音克隆功能
  - 视频生成与处理
  - 音频音高和视频速度调整
  - 实时进度展示
  - 文件上传与管理

## 特性

- ✅ 响应式设计，支持多种屏幕尺寸
- ✅ 现代化的 UI/UX 设计
- ✅ 实时进度条展示
- ✅ 文件上传功能
- ✅ 实时对话界面
- ✅ WebSocket 就绪架构（可扩展）
- ✅ 多主题切换系统
- ✅ 字体切换功能（支持多种字体风格）
- ✅ 智能新手教程系统（针对不同页面提供详细引导）
- ✅ 音频音高调整功能
- ✅ 视频速度调整功能
- ✅ 语音克隆功能

## 扩展建议

1. **后端扩展**：
   - 集成真实的模型训练脚本
   - 实现 WebSocket 实时通信
   - 添加数据库支持（SQLAlchemy）
   - 实现用户认证和授权

2. **前端扩展**：
   - 添加更多可视化效果
   - 实现拖拽上传文件
   - 添加本地存储管理
   - 支持多语言界面

3. **功能扩展**：
   - 实现真正的任务队列管理（如使用Celery）
   - 模型版本管理
   - 生成历史记录
   - 对话日志导出功能

## 配置说明

### GPU 选择

- 支持选择不同GPU进行训练推理
- 系统会自动检测可用GPU设备信息

### 模型名称

- SyncTalk（默认）

### 语音克隆

- 支持上传参考音频进行语音克隆
- 支持对克隆后的音频进行音高调整

### 视频处理

- 支持调整视频播放速度
- 音频与视频同步处理

## 许可证

本项目仅供学习和研究使用。