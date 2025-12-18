from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 存储训练和生成任务的状态
tasks = {}

@app.route('/')
def index():
    """主页 - 显示三个选项"""
    return render_template('index.html')

@app.route('/train')
def train():
    """模型训练页面"""
    return render_template('train.html')

@app.route('/generate')
def generate():
    """视频生成页面"""
    return render_template('generate.html')

@app.route('/chat')
def chat():
    """实时对话页面"""
    return render_template('chat.html')

@app.route('/workflow')
def workflow():
    """一条龙体验页面"""
    return render_template('workflow.html')

# API 端点

@app.route('/api/train', methods=['POST'])
def api_train():
    """开始训练模型"""
    try:
        data = request.json
        task_id = f"train_{datetime.now().timestamp()}"
        
        tasks[task_id] = {
            'type': 'train',
            'status': 'processing',
            'model_name': data.get('model_name', 'SyncTalk'),
            'reference_video': data.get('reference_video', ''),
            'gpu': data.get('gpu', 'GPU0'),
            'epochs': data.get('epochs', 10),
            'custom_params': data.get('custom_params', ''),
            'progress': 0,
            'video_url': None,
            'created_at': datetime.now().isoformat()
        }
        
        # 这里应该调用实际的训练脚本
        # 现在返回模拟响应
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['video_url'] = '/static/videos/training_sample.mp4'
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '训练已启动'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """生成视频"""
    try:
        data = request.json
        task_id = f"generate_{datetime.now().timestamp()}"
        
        tasks[task_id] = {
            'type': 'generate',
            'status': 'processing',
            'model_name': data.get('model_name', 'SyncTalk'),
            'model_dir': data.get('model_dir', ''),
            'reference_audio': data.get('reference_audio', ''),
            'gpu': data.get('gpu', 'GPU0'),
            'voice_clone_model': data.get('voice_clone_model', 'Voice Clone A'),
            'target_text': data.get('target_text', ''),
            'progress': 0,
            'video_url': None,
            'created_at': datetime.now().isoformat()
        }
        
        # 这里应该调用实际的视频生成脚本
        # 现在返回模拟响应
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['video_url'] = '/static/videos/generated_sample.mp4'
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '视频生成已启动'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id in tasks:
        return jsonify(tasks[task_id]), 200
    else:
        return jsonify({'error': '任务不存在'}), 404

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用的模型列表"""
    return jsonify({
        'models': ['SyncTalk', 'Wav2Lip', 'MoFA-Talk'],
        'voice_models': ['Voice Clone A', 'Voice Clone B', 'Voice Clone C'],
        'gpus': ['GPU0', 'GPU1', 'GPU2', 'GPU3'],
        'apis': ['OpenAI API', 'Claude API', 'Local LLM']
    }), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件部分'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 保存文件
        filename = f"{datetime.now().timestamp()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': f'/uploads/{filename}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """处理实时对话"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # 这里应该调用对话API（OpenAI、Claude等）
        # 现在返回模拟响应
        response = {
            'user_message': user_message,
            'bot_response': f"这是对你的消息 '{user_message}' 的模拟回应",
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': response
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
