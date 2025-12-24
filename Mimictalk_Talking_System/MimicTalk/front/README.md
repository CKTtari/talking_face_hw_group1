# 语音识别与合成系统 Web 前端

一个使用 Flask 框架构建的语音识别与合成系统的 Web 前端应用。

## 功能特性

### 1. 主页（首页）

- 三个主要功能选项的选择页面
- 美观的卡片式界面设计
- 快速导航到相应功能页面

### 2. 模型训练页面

- **参数设置**：
  - 模型名称选择（默认 SyncTalk）
  - 参考视频地址输入/上传
  - GPU 选择（GPU0-GPU3）
  - Epoch（训练轮数）设置，默认 10
  - 自定义训练参数输入
  
- **功能**：
  - 点击训练按钮启动训练
  - 实时进度条展示
  - 训练完成后在左侧显示训练视频

### 3. 视频生成页面

- **参数设置**：
  - 模型名称选择（默认 SyncTalk）
  - 模型目录地址输入
  - 参考音频地址输入/上传
  - GPU 选择
  - 语音克隆模型名称选择（默认 Voice Clone A）
  - 目标文字输入

- **功能**：
  - 点击生成视频按钮启动生成
  - 实时进度条展示
  - 生成完成后在左侧显示视频

### 4. 实时对话页面

- **配置参数**：
  - 模型名称选择（默认 SyncTalk）
  - 模型目录地址输入
  - 参考音频地址输入/上传
  - GPU 选择
  - 语音克隆模型名称选择（默认 Voice Clone A）
  - 对话 API 选择（默认 OpenAI API）

- **功能**：
  - 左侧显示语音克隆人物视频
  - 右侧进行文本对话交互
  - 实时消息显示和时间戳
  - 停止对话按钮

## 项目结构

```python
front/
├── app.py                      # Flask 主应用文件
├── requirements.txt            # Python 依赖文件
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
│   │   ├── train.js           # 训练页面脚本
│   │   ├── generate.js        # 生成页面脚本
│   │   └── chat.js            # 对话页面脚本
│   └── videos/                # 视频存储（示例）
└── uploads/                   # 文件上传目录
```

## 安装及运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问应用

在浏览器中打开 `http://localhost:5000`
- 本地访问： http://127.0.0.1:8080
- 局域网访问： http://10.195.246.121:8080

## API 接口

### 1. 获取可用模型和配置

```python
GET /api/models
```

### 2. 开始训练

```python
POST /api/train
Content-Type: application/json

{
    "model_name": "SyncTalk",
    "reference_video": "/path/to/video",
    "gpu": "GPU0",
    "epochs": 10,
    "custom_params": ""
}
```

### 3. 生成视频

```python
POST /api/generate
Content-Type: application/json

{
    "model_name": "SyncTalk",
    "model_dir": "/path/to/model",
    "reference_audio": "/path/to/audio",
    "gpu": "GPU0",
    "voice_clone_model": "Voice Clone A",
    "target_text": "生成的文字"
}
```

### 4. 获取任务状态

```python
GET /api/task/<task_id>
```

### 5. 上传文件

```python
POST /api/upload
Content-Type: multipart/form-data

file: <binary_data>
```

### 6. 实时对话

```python
POST /api/chat
Content-Type: application/json

{
    "message": "用户消息"
}
```

## 技术栈

- **后端**：Flask 2.3.3
- **前端**：HTML5 + CSS3 + JavaScript（原生）
- **样式框架**：自定义 CSS（响应式设计）
- **数据传输**：JSON REST API

## 特性

- ✅ 响应式设计，支持多种屏幕尺寸
- ✅ 现代化的 UI/UX 设计
- ✅ 实时进度条展示
- ✅ 文件上传功能
- ✅ 实时对话界面
- ✅ WebSocket 就绪架构（可扩展）

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
   - 任务队列管理（Celery）
   - 模型版本管理
   - 生成历史记录
   - 对话日志导出

## 配置说明

### GPU 选择

目前支持 GPU0 至 GPU3，可根据实际硬件配置修改。

### 模型名称

- SyncTalk（默认）
- Wav2Lip
- MoFA-Talk

### 语音克隆模型

- Voice Clone A（默认）
- Voice Clone B
- Voice Clone C

### 对话 API

- OpenAI API（默认）
- Claude API
- Local LLM

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
