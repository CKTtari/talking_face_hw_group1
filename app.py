from flask import Flask, render_template, request, jsonify, send_file
from backend.video_audio_processor import VideoAudioProcessor
import os
import subprocess
import threading
import time
import requests
from datetime import datetime
import json
import tempfile
import uuid

# 导入API key
from api_key import OPENAI_API_KEY

# 配置变量
BACKEND_PORT = 8083  # 后端服务端口

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 存储训练和生成任务的状态
tasks = {}

# 后端服务状态
backend_services = {
    'main': {'port': BACKEND_PORT, 'status': 'stopped', 'process': None},
    'voice': {'port': 8001, 'status': 'stopped', 'process': None}
}

def start_backend_service(service_name, script_path, port):
    """启动后端服务"""
    try:
        # 获取脚本所在目录和脚本文件名
        script_dir = os.path.dirname(script_path)
        script_filename = os.path.basename(script_path)
        
        # 使用subprocess启动服务，确保使用正确的Python解释器
        process = subprocess.Popen([
            'python', script_filename
        ], cwd=script_dir, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.PIPE,
           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        
        backend_services[service_name]['process'] = process
        backend_services[service_name]['status'] = 'starting'
        
        # 等待服务启动
        max_wait_time = 30
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # 检查服务是否在运行
                if process.poll() is not None:
                    # 进程已退出
                    stdout, stderr = process.communicate()
                    print(f"❌ {service_name} 服务启动失败，退出码: {process.returncode}")
                    if stdout:
                        print(f"stdout: {stdout.decode('utf-8', errors='ignore')}")
                    if stderr:
                        print(f"stderr: {stderr.decode('utf-8', errors='ignore')}")
                    backend_services[service_name]['status'] = 'failed'
                    return False
                
                # 检查健康接口
                response = requests.get(f'http://localhost:{port}/health', timeout=2)
                if response.status_code == 200:
                    backend_services[service_name]['status'] = 'running'
                    print(f"✅ {service_name} 服务启动成功，端口: {port}")
                    return True
            except requests.exceptions.RequestException:
                # 服务可能还在启动中，继续等待
                pass
            except Exception as e:
                print(f"检查 {service_name} 服务状态时出错: {e}")
            
            time.sleep(2)
        
        # 超时处理
        if process.poll() is None:
            print(f"⚠️ {service_name} 服务启动超时，但进程仍在运行")
            backend_services[service_name]['status'] = 'timeout'
        else:
            backend_services[service_name]['status'] = 'failed'
            print(f"❌ {service_name} 服务启动失败")
        
        return False
        
    except Exception as e:
        print(f"❌ 启动 {service_name} 服务时出错: {e}")
        backend_services[service_name]['status'] = 'failed'
        return False

def start_all_backend_services():
    """启动所有后端服务"""
    print("🚀 正在启动后端服务...")
    
    # 启动主服务
    main_script = os.path.join(os.path.dirname(__file__), 'backend', 'main.py')
    if os.path.exists(main_script):
        start_backend_service('main', main_script, BACKEND_PORT)
    
    print("📊 后端服务启动状态:")
    for service, info in backend_services.items():
        print(f"   {service}: {info['status']} (端口: {info['port']})")


# 从backend.chat_engine导入LLM响应生成函数
from backend.chat_engine import generate_llm_response as chat_engine_generate_llm_response

def generate_llm_response(user_message):
    """生成LLM响应 - 调用backend.chat_engine中的函数"""
    try:
        # 使用从api_key.py导入的API key
        API_KEY = OPENAI_API_KEY
        
        # 调用backend.chat_engine中的generate_llm_response函数
        return chat_engine_generate_llm_response(user_message, API_KEY)
    except Exception as e:
        # 处理异常情况
        return f"生成响应时出错: {str(e)}"


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

@app.route('/api/backend-status')
def backend_status():
    """检查后端服务状态"""
    return jsonify({
        'success': True,
        'services': backend_services
    })

# API 端点

@app.route('/api/train', methods=['POST'])
def api_train():
    """开始训练模型"""
    try:
        if 'reference_video' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传视频文件'
            }), 400
        
        # 获取表单数据和文件
        video_file = request.files['reference_video']
        model_name = request.form.get('model_name', 'SyncTalk')
        gpu = request.form.get('gpu', 'GPU0')
        custom_params = request.form.get('custom_params', '')
        
        task_id = f"train_{datetime.now().timestamp()}"
        
        # 解析custom_params获取max_updates
        try:
            custom_params_dict = json.loads(custom_params)
            max_updates = custom_params_dict.get('max_updates', 10)
        except json.JSONDecodeError:
            max_updates = 10
        
        tasks[task_id] = {
            'type': 'train',
            'status': 'processing',
            'model_name': model_name,
            'reference_video': video_file.filename,
            'gpu': gpu,
            'max_updates': max_updates,
            'custom_params': custom_params,
            'progress': 0,
            'video_url': None,
            'created_at': datetime.now().isoformat()
        }
        
        # 保存上传的视频文件到临时位置
        temp_video_path = os.path.join(tempfile.gettempdir(), f"train_{uuid.uuid4().hex}.mp4")
        video_file.save(temp_video_path)
        
        try:
            # 调用后端FastAPI训练API - 使用JSON格式
            backend_url = f"http://localhost:{BACKEND_PORT}/api/train"
            
            # 读取视频文件内容并转换为Base64编码
            with open(temp_video_path, 'rb') as f:
                video_content = f.read()
            
            import base64
            video_base64 = base64.b64encode(video_content).decode('utf-8')
            video_base64 = f"data:video/mp4;base64,{video_base64}"
            
            # 准备默认参数
            params = {
                'max_updates': max_updates,  # 使用解析出的max_updates或默认值
                'speaker_name': f"speaker_{uuid.uuid4().hex[:8]}",
                'torso_ckpt': 'checkpoints/mimictalk_orig/os_secc2plane_torso',
                'batch_size': 1,
                'lr': 0.001,
                'lr_triplane': 0.005,
                'video_file': video_base64
            }
            
            # 合并前端传递的自定义参数
            if custom_params:
                try:
                    custom_params_dict = json.loads(custom_params)
                    # 合并参数，自定义参数优先级更高
                    params.update(custom_params_dict)
                    
                    # 如果speaker_name为空字符串，使用自动生成的
                    if params.get('speaker_name') == '':
                        params['speaker_name'] = f"speaker_{uuid.uuid4().hex[:8]}"
                except json.JSONDecodeError:
                    print(f"无效的自定义参数JSON: {custom_params}")
            
            # 使用JSON格式发送请求
            response = requests.post(backend_url, json=params, stream=True)
            
            # 处理响应（这里简化处理，实际应该处理流式输出）
            if response.status_code == 200:
                # 从响应中提取视频URL - 初始化为None，不使用默认示例视频
                video_url = None
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        print(line_str)  # 输出到控制台以便调试
                        
                        # 查找包含视频URL的行
                        if '🔗 前端可访问的视频URL：' in line_str:
                            video_url = line_str.split('：')[1].strip()
                            break
                
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['progress'] = 100
                tasks[task_id]['video_url'] = video_url  # 只在有实际URL时设置
            else:
                tasks[task_id]['status'] = 'failed'
                tasks[task_id]['video_url'] = None  # 训练失败时不设置视频URL
                raise Exception(f"训练失败：{response.text}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
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
        if 'reference_audio' not in request.files or 'reference_video' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传音频文件或视频文件'
            }), 400
        
        # 获取表单数据和文件
        audio_file = request.files['reference_audio']
        video_file = request.files['reference_video']
        model_name = request.form.get('model_name', 'SyncTalk')
        model_dir = request.form.get('model_dir', '')
        gpu = request.form.get('gpu', 'GPU0')
        target_text = request.form.get('target_text', '')
        pitch = request.form.get('pitch', 0)  # 音频升降调
        speed = request.form.get('speed', 1.0)  # 视频加速减速
        
        task_id = f"generate_{datetime.now().timestamp()}"
        
        tasks[task_id] = {
            'type': 'generate',
            'status': 'processing',
            'model_name': model_name,
            'model_dir': model_dir,
            'reference_audio': audio_file.filename,
            'gpu': gpu,
            'target_text': target_text,
            'progress': 0,
            'video_url': None,
            'created_at': datetime.now().isoformat()
        }
        
        # 保存上传的音频文件到临时位置
        temp_audio_path = os.path.join(tempfile.gettempdir(), f"infer_{uuid.uuid4().hex}.wav")
        audio_file.save(temp_audio_path)
        
        # 保存上传的视频文件到临时位置
        temp_video_path = os.path.join(tempfile.gettempdir(), f"pose_{uuid.uuid4().hex}.mp4")
        video_file.save(temp_video_path)
        
        # 检查是否需要调整音频音高
        pitch_value = float(pitch) if pitch else 1.0
        speed_value = float(speed) if speed else 1.0
        
        # 如果提供了目标文本，先进行语音克隆
        final_audio_path = temp_audio_path
        
        if target_text.strip():
            try:
                # 将参考音频转换为Base64
                import base64
                with open(temp_audio_path, 'rb') as audio_file:
                    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
                
                # 调用语音克隆API
                clone_payload = {
                    'text': target_text,
                    'reference_audio': audio_base64
                }
               # 调用语音克隆API
                clone_response = requests.post(f'http://localhost:{BACKEND_PORT}/api/clone-voice', json=clone_payload)
                clone_data = clone_response.json()
                
                if clone_response.status_code == 200 and clone_data.get('success'):
                    # 使用克隆后的音频文件
                    cloned_audio_filename = clone_data.get('audio_filename')
                    if cloned_audio_filename:
                        # 从后端数据目录获取克隆的音频文件
                        backend_data_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data')
                        cloned_audio_path = os.path.join(backend_data_dir, cloned_audio_filename)
                        
                        if os.path.exists(cloned_audio_path):
                            if pitch_value != 1.0:
                                # 直接对克隆后的音频进行音高调整
                                from backend.video_audio_processor import VideoAudioProcessor
                                processor = VideoAudioProcessor()
                                adjusted_audio_path = os.path.join(backend_data_dir, f"pitch_adjusted_{cloned_audio_filename}")
                                if processor.adjust_audio_pitch(cloned_audio_path, adjusted_audio_path, pitch_value):
                                    final_audio_path = adjusted_audio_path
                                    tasks[task_id]['reference_audio'] = f"pitch_adjusted_cloned_{cloned_audio_filename}"
                                    print(f"✅ 使用语音克隆后并调整音高的音频: {os.path.basename(adjusted_audio_path)}")
                                else:
                                    # 如果音高调整失败，使用原始克隆音频
                                    final_audio_path = cloned_audio_path
                                    tasks[task_id]['reference_audio'] = f"cloned_{cloned_audio_filename}"
                                    print(f"⚠️ 音频音高调整失败，使用原始克隆音频: {cloned_audio_filename}")
                            else:
                                final_audio_path = cloned_audio_path
                                tasks[task_id]['reference_audio'] = f"cloned_{cloned_audio_filename}"
                                print(f"✅ 使用语音克隆后的音频: {cloned_audio_filename}")
                        else:
                            print(f"⚠️ 克隆音频文件不存在: {cloned_audio_path}")
                else:
                    print(f"⚠️ 语音克隆失败: {clone_data.get('message', '未知错误')}")
                    
            except Exception as e:
                print(f"⚠️ 语音克隆过程出错: {str(e)}")
        else:
            # 没有目标文本，直接使用上传的参考音频
            if pitch_value != 1.0:
                # 直接对参考音频进行音高调整
                from backend.video_audio_processor import VideoAudioProcessor
                processor = VideoAudioProcessor()
                adjusted_audio_path = os.path.join(os.path.dirname(temp_audio_path), f"pitch_adjusted_{os.path.basename(temp_audio_path)}")
                if processor.adjust_audio_pitch(temp_audio_path, adjusted_audio_path, pitch_value):
                    final_audio_path = adjusted_audio_path
                    tasks[task_id]['reference_audio'] = f"pitch_adjusted_{os.path.basename(temp_audio_path)}"
                    print(f"✅ 使用调整音高后的参考音频: {os.path.basename(adjusted_audio_path)}")
                else:
                    # 如果音高调整失败，使用原始参考音频
                    final_audio_path = temp_audio_path
                    print(f"⚠️ 音频音高调整失败，使用原始参考音频: {os.path.basename(temp_audio_path)}")
            else:
                print(f"✅ 使用原始参考音频: {os.path.basename(temp_audio_path)}")
        
        try:
            # 调用后端FastAPI推理API
            backend_url = f"http://localhost:{BACKEND_PORT}/api/infer"
            with open(final_audio_path, 'rb') as audio_file:
                files = {'audio_file': audio_file}
                data = {
                    'local_ckpt_dir': model_dir,
                    'out_name': f"infer_{uuid.uuid4().hex[:8]}.mp4",
                    'drv_pose': temp_video_path,  # 使用上传的视频作为参考姿势
                    'bg_img': '',
                    'target_text': target_text  # 传递目标文字参数
                }
                
                response = requests.post(backend_url, files=files, data=data)
                response_data = response.json()
            
            if response.status_code == 200 and response_data.get('code') == 0:
                # 获取生成的视频路径
                generated_video_path = response_data['data']['本地生成视频路径']
                
                # 检查生成的视频文件是否存在
                if not os.path.exists(generated_video_path):
                    raise Exception(f"生成的视频文件不存在: {generated_video_path}")
                
                # 创建视频音频处理器实例
                processor = VideoAudioProcessor()
                
                # 处理视频（应用音频升降调和视频加速减速）
                processed_video_path = os.path.join(os.path.dirname(generated_video_path), f"processed_{os.path.basename(generated_video_path)}")
                
                # 执行处理 - 只进行视频速度调整，音频已经在克隆时处理过
                speed_value = float(speed) if speed else 1.0
                pitch_value = float(pitch) if pitch else 1.0
                
                print(f"🔍 后处理参数检查: pitch={pitch_value}, speed={speed_value}")
                
                if speed_value != 1.0:
                    print(f"🔧 开始执行视频速度后处理")
                    print(f"   输入视频: {generated_video_path}")
                    print(f"   输出视频: {processed_video_path}")
                    print(f"   处理参数: speed={speed_value}")
                    
                    if not processor.adjust_video_speed(generated_video_path, processed_video_path, speed_value):
                        # 如果处理失败，直接使用原始视频
                        processed_video_path = generated_video_path
                        print(f"⚠️  视频速度处理失败，使用原始视频: {processed_video_path}")
                    else:
                        print(f"✅  视频速度后处理完成: {processed_video_path}")
                else:
                    # 当speed为1时，直接使用原始视频
                    processed_video_path = generated_video_path
                    print(f"✅  无需处理，使用原始视频: {processed_video_path}")
                
                # 确保static/videos目录存在
                static_videos_dir = os.path.join(app.static_folder, 'videos')
                os.makedirs(static_videos_dir, exist_ok=True)
                
                # 复制处理后的视频到static目录以便前端访问
                static_video_path = os.path.join(static_videos_dir, os.path.basename(processed_video_path))
                import shutil
                try:
                    shutil.copy(processed_video_path, static_video_path)
                    print(f"✅ 视频复制到static目录: {static_video_path}")
                    
                    tasks[task_id]['status'] = 'completed'
                    tasks[task_id]['progress'] = 100
                    tasks[task_id]['video_url'] = f'/static/videos/{os.path.basename(processed_video_path)}'
                except Exception as e:
                    print(f"❌ 复制视频到static目录失败: {e}")
                    # 如果复制失败，尝试直接使用本地临时文件路径
                    # 注意：这不是最佳实践，仅作为临时解决方案
                    tasks[task_id]['status'] = 'completed'
                    tasks[task_id]['progress'] = 100
                    # 直接提供本地文件路径，让前端能够访问
                    tasks[task_id]['video_url'] = f'/api/download?file_path={processed_video_path}'
            else:
                tasks[task_id]['status'] = 'failed'
                raise Exception(f"推理失败：{response_data.get('msg', '未知错误')}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
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

@app.route('/api/task/<task_id>/stop', methods=['POST'])
def stop_task(task_id):
    """停止任务生成"""
    if task_id in tasks:
        # 更新任务状态为stopped
        tasks[task_id]['status'] = 'stopped'
        tasks[task_id]['progress'] = 0
        return jsonify({'success': True, 'message': '任务已停止'}), 200
    else:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用的模型列表"""
    try:
        # 调用后端服务获取真实的模型列表
        response = requests.get(f'http://localhost:{BACKEND_PORT}/api/models')
        if response.status_code == 200:
            return response.json(), 200
        else:
            # 如果后端服务不可用，返回基本的真实可用模型
            return jsonify({
                'models': ['SyncTalk'],
                'voice_models': ['Voice Clone'],
                'gpus': ['GPU0', 'CPU'],
                'apis': ['Zhipu API']
            }), 200
    except Exception as e:
        print(f"获取模型列表出错: {e}")
        # 出错时返回基本的真实可用模型
        return jsonify({
            'models': ['SyncTalk'],
            'voice_models': ['Voice Clone'],
            'gpus': ['GPU0', 'CPU'],
            'apis': ['Zhipu API']
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

@app.route('/api/gpu_info', methods=['GET'])
def get_gpu_info():
    """获取GPU设备信息"""
    try:
        import subprocess
        import re
        
        gpu_list = []
        
        # 尝试使用nvidia-smi命令获取GPU信息
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total,memory.free', '--format=csv,noheader,nounits'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            gpu_info = {
                                'id': f"GPU{parts[0]}",
                                'name': parts[1],
                                'memory_total': f"{parts[2]} MB",
                                'memory_free': f"{parts[3]} MB",
                                'available': True
                            }
                            gpu_list.append(gpu_info)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            # 如果没有nvidia-smi或执行失败，返回模拟数据
            print(f"GPU检测失败: {e}")
            
        # 如果没有检测到GPU，返回默认选项
        if not gpu_list:
            gpu_list = [
                {'id': 'GPU0', 'name': '默认GPU', 'memory_total': '未知', 'memory_free': '未知', 'available': True},
                {'id': 'CPU', 'name': 'CPU模式', 'memory_total': '系统内存', 'memory_free': '未知', 'available': True}
            ]
        
        return jsonify({
            'success': True,
            'gpus': gpu_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'gpus': [{'id': 'GPU0', 'name': '默认GPU', 'memory_total': '未知', 'memory_free': '未知', 'available': True}]
        }), 200

@app.route('/api/clone-voice', methods=['POST'])
def clone_voice():
    """语音克隆API"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        if not data or 'text' not in data or 'reference_audio' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：text 和 reference_audio'
            }), 400
        
        # 调用后端语音克隆服务
        response = requests.post(
            f'http://localhost:{BACKEND_PORT}/api/clone-voice',
            json={
                'text': data['text'],
                'reference_audio': data['reference_audio']
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': f'语音克隆服务错误: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'语音克隆失败: {str(e)}'
        }), 500

@app.route('/api/voice-clone-models', methods=['GET'])
def get_voice_clone_models():
    """获取可用的语音克隆模型列表"""
    try:
        # 调用后端服务获取模型列表
        response = requests.get(f'http://localhost:{BACKEND_PORT}/api/voice-clone-models')
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            # 如果后端服务不可用，返回错误信息
            return jsonify({
                'success': False,
                'error': f'获取模型列表失败: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        # 出错时返回错误信息
        return jsonify({
            'success': False,
            'error': f'获取模型列表失败: {str(e)}'
        }), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """处理实时对话，调用LLM生成回复"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
        
        # 调用LLM生成回复
        bot_response = generate_llm_response(user_message)
        
        return jsonify({
            'success': True,
            'response': bot_response
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# 启动Flask前端服务
if __name__ == '__main__':
    print("🚀 启动前端服务...")
    print("📝 请确保先启动后端主服务：")
    print("   python -m backend.main")
    print("💡 语音克隆功能已整合到主服务中")
    print(f"🌐 前端服务将在端口 5000 启动")
    app.run(debug=True, host='0.0.0.0', port=5000)