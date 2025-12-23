# 文件名: backend.py
# 位置: 宿主机 (容器外面)

import os
import requests
import subprocess
import shutil
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MimicTalk 总控后端")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 定义请求参数：前端传给我们什么？
class GenerateRequest(BaseModel):
    text: str          # 想要生成的文字
    image_name: str    # 图片文件名 (假设图片已经上传到了挂载目录)
    reference_audio: str = "/app/Voice_Model/1.wav"  # 用户上传的参考音频路径，默认使用系统参考音频

# 定义容器内的路径配置
CONTAINER_NAME = "mimictalk"
VOICE_API_URL = "http://127.0.0.1:7860/tts"  # 容器暴露出来的语音端口，正确端点是/tts，端口按用户要求使用7860
MOUNT_DIR = "/app/data" # 假设挂载目录，用于存放生成的音频和视频
LOCAL_MOUNT_DIR = "./data"  # 宿主机上的挂载目录，确保存在
UPLOADS_DIR = "./uploads"  # 宿主机上的上传目录，需要挂载到容器内

# 确保本地挂载目录存在
os.makedirs(LOCAL_MOUNT_DIR, exist_ok=True)

# 添加静态文件服务
from fastapi.staticfiles import StaticFiles
app.mount("/data", StaticFiles(directory=LOCAL_MOUNT_DIR), name="data")

@app.post("/test-voice-clone")
async def test_voice_clone(req: GenerateRequest):
    """
    测试语音克隆功能的接口，不依赖视频生成。
    """
    print(f"收到语音克隆测试任务：文本='{req.text}'，参考音频='{req.reference_audio}'")
    
    # 确保本地挂载目录存在
    os.makedirs(LOCAL_MOUNT_DIR, exist_ok=True)
    
    # 定义音频保存路径
    generated_audio_filename = f"clone_voice_{int(datetime.now().timestamp())}.wav"
    local_save_path = f"{LOCAL_MOUNT_DIR}/{generated_audio_filename}"
    
    try:
        # 处理参考音频
        ref_audio_path = req.reference_audio
        audio_file = None
        ref_filename = ""
        
        # 提取文件名，处理两种情况：带/uploads/前缀或直接文件名
        if ref_audio_path.startswith('/uploads/'):
            filename = ref_audio_path.split('/')[-1]
        else:
            filename = ref_audio_path  # 直接使用传递的文件名
        
        # 获取宿主机上的完整路径
        # 项目根目录应该是backend的上级目录
        base_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, '..'))
        local_ref_path = os.path.join(project_root, 'uploads', filename)
        print(f"Debug: 项目根目录: {project_root}")
        print(f"Debug: 本地参考音频路径: {local_ref_path}")
        print(f"Debug: 文件是否存在: {os.path.exists(local_ref_path)}")
        
        if os.path.exists(local_ref_path):
            # 打开音频文件
            audio_file = open(local_ref_path, 'rb')
            ref_filename = filename
            print(f"Debug: 成功读取音频文件: {ref_filename}")
        
        if audio_file:
            # 直接发送音频文件内容
            files = {'ref_audio': (ref_filename, audio_file, 'audio/wav')}
            data = {
                "text": req.text,
                "text_lang": "zh",
                "prompt_lang": "zh"
            }
            print(f"Debug: 发送")
            response = requests.post(VOICE_API_URL, data=data, files=files)
            audio_file.close()
        else:
            # 使用默认参考音频路径
            response = requests.get(VOICE_API_URL, params={
                "text": req.text,
                "text_lang": "zh",
                "ref_audio_path": "/app/Voice_Model/1.wav",
                "prompt_lang": "zh"
            })
        
        if response.status_code == 200:
            # 保存生成的语音到本地
            print(f"Debug: 保存")
            with open(local_save_path, "wb") as f:
                f.write(response.content)
            print(">>> 语音克隆测试成功！")
            
            return {
                "status": "success",
                "msg": "语音克隆测试成功",
                "audio_path": local_save_path,
                "audio_filename": generated_audio_filename  # 返回生成的音频文件名
            }
        else:
            return {"status": "error", "msg": "语音生成失败", "detail": response.text}
            
    except Exception as e:
        return {"status": "error", "msg": "连接语音服务失败", "detail": str(e)}

@app.post("/run")
async def run_process(req: GenerateRequest):
    """
    这个接口是给前端调用的。
    收到请求后，它负责去指挥容器里的两个模型干活。
    """
    print(f"收到任务：文本='{req.text}'，图片='{req.image_name}'")
    
    # 确保本地挂载目录存在
    os.makedirs(LOCAL_MOUNT_DIR, exist_ok=True)

    # --- 第一步：调用语音克隆 (HTTP交互) ---
    print(">>> 1. 正在请求容器生成语音...")
    
    # 定义音频在容器内的保存路径
    audio_filename = "output_voice.wav"
    audio_path_in_container = f"{MOUNT_DIR}/{audio_filename}"
    local_save_path = f"{LOCAL_MOUNT_DIR}/{audio_filename}"
    
    try:
        # 处理参考音频
        ref_audio_path = req.reference_audio
        audio_file = None
        audio_filename = ""
        
        # 提取文件名，处理两种情况：带/uploads/前缀或直接文件名
        if ref_audio_path.startswith('/uploads/'):
            filename = ref_audio_path.split('/')[-1]
        else:
            filename = ref_audio_path  # 直接使用传递的文件名
        
        # 获取宿主机上的完整路径
        # 项目根目录应该是backend的上级目录
        base_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, '..'))
        local_ref_path = os.path.join(project_root, 'uploads', filename)
        print(f"Debug (run): 项目根目录: {project_root}")
        print(f"Debug (run): 本地参考音频路径: {local_ref_path}")
        print(f"Debug (run): 文件是否存在: {os.path.exists(local_ref_path)}")
        
        if os.path.exists(local_ref_path):
            # 打开音频文件
            audio_file = open(local_ref_path, 'rb')
            audio_filename = filename
            print(f"Debug (run): 成功读取音频文件: {audio_filename}")
        
        if audio_file:
            # 直接发送音频文件内容
            files = {'ref_audio': (audio_filename, audio_file, 'audio/wav')}
            data = {
                "text": req.text,
                "text_lang": "zh",
                "prompt_lang": "zh"
            }
            
            response = requests.post(VOICE_API_URL, data=data, files=files)
            audio_file.close()
        else:
            # 使用默认参考音频路径
            response = requests.get(VOICE_API_URL, params={
                "text": req.text,
                "text_lang": "zh",
                "ref_audio_path": "/app/Voice_Model/1.wav",
                "prompt_lang": "zh"
            })
        
        if response.status_code == 200:
            # 保存生成的语音到本地
            with open(local_save_path, "wb") as f:
                f.write(response.content)
            print(">>> 语音生成成功！")
        else:
            return {"status": "error", "msg": "语音生成失败", "detail": response.text}
            
    except Exception as e:
        return {"status": "error", "msg": "连接语音服务失败", "detail": str(e)}

    # --- 第二步：调用 MimicTalk (Docker命令交互) ---
    print(">>> 2. 正在触发容器生成视频...")
    
    # 构造 Docker 命令
    # 相当于你在终端手动敲：docker exec mimictalk python inference/...
    cmd = [
        "docker", "exec", CONTAINER_NAME,
        "python", "inference/app_mimictalk.py", # 假设这是容器里的入口脚本
        "--audio_path", audio_path_in_container,
        "--image_path", f"{MOUNT_DIR}/{req.image_name}"
    ]
    
    # 执行命令
    try:
        # subprocess.run 会等待命令执行完毕
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(">>> 视频生成成功！")
            return {
                "status": "success", 
                "video_path": f"{MOUNT_DIR}/output_video.mp4",
                "logs": result.stdout
            }
        else:
            print(">>> 视频生成出错！")
            return {"status": "error", "msg": "视频生成脚本报错", "logs": result.stderr}
            
    except Exception as e:
        return {"status": "error", "msg": "执行Docker命令失败", "detail": str(e)}

    # --- 第二步：调用 MimicTalk (Docker命令交互) ---
    print(">>> 2. 正在触发容器生成视频...")
    
    # 构造 Docker 命令
    # 相当于你在终端手动敲：docker exec mimictalk python inference/...
    cmd = [
        "docker", "exec", CONTAINER_NAME,
        "python", "inference/app_mimictalk.py", # 假设这是容器里的入口脚本
        "--audio_path", audio_path_in_container,
        "--image_path", f"{MOUNT_DIR}/{req.image_name}"
    ]
    
    # 执行命令
    try:
        # subprocess.run 会等待命令执行完毕
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(">>> 视频生成成功！")
            return {
                "status": "success", 
                "video_path": f"{MOUNT_DIR}/output_video.mp4",
                "logs": result.stdout
            }
        else:
            print(">>> 视频生成出错！")
            return {"status": "error", "msg": "视频生成脚本报错", "logs": result.stderr}
            
    except Exception as e:
        return {"status": "error", "msg": "执行Docker命令失败", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)