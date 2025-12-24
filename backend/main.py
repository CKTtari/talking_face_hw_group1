import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from config import cfg
import os
import uuid
import json
from io import BytesIO
import requests
from datetime import datetime
import time
from utils import (
    docker_cp_local_to_container,
    docker_cp_container_to_local,
    docker_exec_train,
    docker_exec_infer,
    sync_ckpt_from_container_to_local,
)

# 语音克隆服务配置
VOICE_API_URL = "http://127.0.0.1:7860/tts"  # 容器暴露的语音克隆服务接口
LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")  # 本地数据目录

# 确保本地数据目录存在
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

app = FastAPI(title="MimicTalk 容器外API（带实时进度）")

# -------------------------- 启动语音克隆服务 --------------------------
def start_voice_clone_service():
    """启动容器中的语音克隆API后台"""
    try:
        print("🚀 正在启动语音克隆服务...")
        
        # 1. 检查容器是否正在运行
        result = subprocess.run(["docker", "ps", "-q", "-f", "name=mimictalk"], 
                              capture_output=True, text=True, timeout=60)
        
        if not result.stdout.strip():
            print("⚠️  mimictalk容器未运行，正在启动...")
            subprocess.run(["docker", "start", "mimictalk"], capture_output=True, text=True, timeout=300)
            print("✅ mimictalk容器已启动")
            time.sleep(2)  # 给容器启动留一点时间
        
        # 2. 用Popen后台运行（不阻塞脚本）
        manual_cmd = '''docker exec mimictalk bash -c "export PYTHONUNBUFFERED=1 && source /opt/conda/etc/profile.d/conda.sh && conda activate voice && cd /app/Voice_Model && python api_v2.py"'''
        
        # 用Popen后台执行，不会阻塞脚本
        process = subprocess.Popen(
            manual_cmd,
            shell=True,
            stdout=open("voice_manual.log", "w"),  # 可选：把输出写到本地日志
            stderr=open("voice_manual_error.log", "w"),
            text=True
        )
        
        time.sleep(15)  # 等待服务加载（根据你的模型加载速度调整）
        print("✅ 语音克隆服务命令已后台执行")
        print(f"📡 语音克隆服务地址: {VOICE_API_URL}")
        print(f"📄 本地日志: voice_manual.log / voice_manual_error.log")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动语音克隆服务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# -------------------------- 关闭语音克隆服务 --------------------------
def stop_voice_clone_service():
    """杀掉容器中的语音克隆API后台进程"""
    try:
        print("🛑 正在关闭语音克隆服务...")
        
        # 查找容器中运行的api_v2.py进程并杀掉
        kill_cmd = '''docker exec mimictalk bash -c "ps aux | grep 'python api_v2.py' | grep -v grep | awk '{print $2}' | xargs -r kill -9"'''
        
        # 执行命令杀掉进程
        subprocess.run(
            kill_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ 语音克隆服务已成功关闭")
        return True
        
    except Exception as e:
        print(f"❌ 关闭语音克隆服务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 添加静态文件服务
from fastapi.staticfiles import StaticFiles
app.mount("/data", StaticFiles(directory=LOCAL_DATA_DIR), name="data")

# -------------------------- 健康检查接口 --------------------------
@app.get("/api/health", summary="健康检查")
async def health_check():
    return JSONResponse({
        "code": 0,
        "msg": "服务正常运行",
        "data": {
            "port": cfg.LOCAL_API_PORT,
            "local_ckpt_dir": cfg.LOCAL_CKPT_SAVE_DIR,
            "local_temp_dir": cfg.LOCAL_TEMP_DIR
        }
    })

# -------------------------- GPU信息接口 --------------------------
@app.get("/api/gpu_info")
def get_gpu_info():
    """获取GPU信息"""
    try:
        gpus = []
        
        # 使用nvidia-smi获取GPU信息
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total,memory.free', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 4:
                        gpu_info = {
                            'id': f"GPU{parts[0]}",
                            'name': parts[1],
                            'memory_total': int(parts[2]),
                            'memory_free': int(parts[3]),
                            'available': True
                        }
                        gpus.append(gpu_info)
        
        # 如果没有检测到GPU，返回默认信息
        if not gpus:
            gpus = [{
                'id': 'GPU0',
                'name': 'CPU Only',
                'memory_total': 0,
                'memory_free': 0,
                'available': False
            }]
        
        return {"gpus": gpus}
        
    except Exception as e:
        print(f"获取GPU信息错误: {e}")
        # 出错时返回默认信息
        return {"gpus": [{
            'id': 'GPU0',
            'name': 'Error: GPU detection failed',
            'memory_total': 0,
            'memory_free': 0,
            'available': False
        }]}

# -------------------------- 语音克隆模型接口 --------------------------
@app.get("/api/voice-clone-models")
def get_voice_clone_models():
    """获取可用的语音克隆模型列表"""
    try:
        # 目前只支持一个默认语音克隆模型
        models = [
            {"id": "default_voice_clone", "name": "默认语音克隆模型"}
        ]
        
        return {
            "success": True,
            "models": models
        }
        
    except Exception as e:
        print(f"获取语音克隆模型错误: {e}")
        # 出错时返回默认模型列表
        return {
            "success": True,
            "models": [
                {"id": "default_voice_clone", "name": "默认语音克隆模型"}
            ]
        }

# -------------------------- 训练接口（带实时进度条）--------------------------
@app.post("/api/train", summary="上传视频训练（实时显示进度条）", response_class=StreamingResponse)
async def train(request: Request):
    try:
        # 解析请求体
        data = await request.json()
        
        # 获取参数
        max_updates = int(data.get("max_updates", 5))
        speaker_name = data.get("speaker_name", "my_first_speaker")
        torso_ckpt = data.get("torso_ckpt", "checkpoints/mimictalk_orig/os_secc2plane_torso")
        batch_size = int(data.get("batch_size", 1))
        lr = float(data.get("lr", 0.001))
        lr_triplane = float(data.get("lr_triplane", 0.005))
        
        # 获取Base64编码的视频内容
        video_base64 = data.get("video_file", "")
        if not video_base64:
            raise HTTPException(status_code=400, detail="缺少视频文件")
        
        # 解码Base64视频内容
        import base64
        video_data = base64.b64decode(video_base64.split(',')[1] if ',' in video_base64 else video_base64)
        
        # 1. 保存视频到本地临时目录
        local_video_name = f"train_{uuid.uuid4().hex}.mp4"
        local_video_path = os.path.join(cfg.LOCAL_TEMP_DIR, local_video_name)
        with open(local_video_path, "wb") as f:
            f.write(video_data)
        print(f"✅ 本地视频保存：{local_video_path}")
        
        # 2. 复制视频到容器（符合组长要求的路径）
        container_video_path = os.path.join(cfg.CONTAINER_DATA_DIR, local_video_name)
        docker_cp_local_to_container(local_video_path, container_video_path)
        
        # 3. 容器内模型保存路径
        container_work_dir = os.path.join(cfg.CONTAINER_CKPT_DIR, speaker_name)
        
        # 4. 执行训练（流式返回进度）
        def train_generator():
            # 调用 utils 的实时训练函数，生成日志流
            yield f"📌 开始训练：说话人={speaker_name}，步数={max_updates}，批次={batch_size}\n".encode("utf-8")
            try:
                # 调用 docker_exec_train（生成器函数，实时返回日志）
                for line in docker_exec_train(
                    container_video_path=container_video_path,
                    max_updates=max_updates,
                    container_work_dir=container_work_dir,
                    torso_ckpt=torso_ckpt,
                    batch_size=batch_size,
                    lr=lr,
                    lr_triplane=lr_triplane
                ):
                    yield line.encode("utf-8")  # 流式返回给客户端
                
                # 5. 同步模型到本地
                local_ckpt_dir = sync_ckpt_from_container_to_local(container_work_dir, speaker_name)
                yield f"\n✅ 训练完成！模型保存到：{local_ckpt_dir}\n".encode("utf-8")
                
                # 6. 复制验证视频（可选）
                local_val_video_path = os.path.join(cfg.LOCAL_TEMP_DIR, f"{speaker_name}_val.mp4")
                # 前端可访问的静态目录路径
                frontend_video_path = os.path.join("E:\projects\talking_face_hw_group1\static\videos", f"{speaker_name}_val.mp4")
                try:
                    # 列出容器内所有val_step*.mp4文件，找出数字最大的那个
                    list_cmd = ["docker", "exec", "mimictalk", "bash", "-c", f"ls {container_work_dir}/val_step*.mp4 2>/dev/null | sort -V"]
                    result = subprocess.run(list_cmd, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        # 获取所有val_step视频文件列表
                        val_videos = result.stdout.strip().split('\n')
                        if val_videos:
                            # 选择最后一个（数字最大的）
                            container_val_video_path = val_videos[-1].strip()
                            
                            docker_cp_container_to_local(container_val_video_path, local_val_video_path)
                            yield f"📹 验证视频保存到：{local_val_video_path}\n".encode("utf-8")
                            
                            # 复制到前端静态目录
                            import shutil
                            shutil.copy2(local_val_video_path, frontend_video_path)
                            yield f"📤 验证视频已复制到前端静态目录：{frontend_video_path}\n".encode("utf-8")
                            
                            # 在响应中包含前端可访问的视频URL
                            video_url = f"/static/videos/{speaker_name}_val.mp4"
                            yield f"🔗 前端可访问的视频URL：{video_url}\n".encode("utf-8")
                    else:
                        yield f"⚠️  容器内未找到val_step*.mp4文件\n".encode("utf-8")
                except Exception as e:
                    yield f"⚠️  验证视频复制失败：{str(e)}\n".encode("utf-8")
                
                # 返回最终结果JSON（客户端可解析）
                result = {
                    "code": 0,
                    "msg": "训练成功",
                    "data": {
                        "说话人名称": speaker_name,
                        "本地模型路径": local_ckpt_dir,
                        "本地验证视频路径": local_val_video_path if os.path.exists(local_val_video_path) else "无"
                    }
                }
                yield f"JSON_RESULT:{str(result)}\n".encode("utf-8")
            except Exception as e:
                error_msg = f"\n❌ 训练失败：{str(e)}\n".encode("utf-8")
                yield error_msg
                raise
        
        # 流式返回进度（text/plain 格式，curl 可直接显示）
        return StreamingResponse(
            train_generator(),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        error_msg = f"❌ 训练初始化失败：{str(e)}"
        print(error_msg)
        return StreamingResponse(
            [error_msg.encode("utf-8")],
            media_type="text/plain; charset=utf-8",
            status_code=500
        )
# -------------------------- 推理接口（生成说话视频）--------------------------
@app.post("/api/infer", summary="生成说话视频")
async def infer(request: Request):
    try:
        # 手动解析multipart/form-data请求，不依赖python-multipart
        import uuid
        import base64
        import os
        import io
        import requests
        from typing import Dict, Tuple
        
        # 获取请求体
        body = await request.body()
        content_type = request.headers.get("Content-Type", "")
        
        # 解析multipart/form-data
        if not content_type.startswith("multipart/form-data"):
            raise HTTPException(status_code=400, detail="只支持multipart/form-data格式")
        
        # 提取boundary
        boundary = content_type.split("boundary=")[-1]
        if not boundary:
            raise HTTPException(status_code=400, detail="Content-Type中缺少boundary参数")
        
        # 手动解析multipart数据
        def parse_multipart(body: bytes, boundary: str) -> Tuple[Dict[str, str], bytes, bytes]:
            """解析multipart/form-data，返回表单数据、音频文件内容和视频文件内容"""
            form_data: Dict[str, str] = {}
            audio_data: bytes = b""
            video_data: bytes = b""
            
            # 转换boundary格式
            boundary_bytes = f"--{boundary}".encode("utf-8")
            parts = body.split(boundary_bytes)
            
            for part in parts:
                if not part or part.strip() == b"--":
                    continue
                
                # 分离头部和内容
                headers, content = part.split(b"\r\n\r\n", 1)
                headers = headers.decode("utf-8", errors="ignore")
                
                # 解析Content-Disposition头部
                if "Content-Disposition:" in headers:
                    cd_header = headers.split("Content-Disposition:", 1)[1].split("\n")[0].strip()
                    
                    # 提取name参数
                    if "name=\"" in cd_header:
                        name = cd_header.split("name=\"")[1].split("\"")[0]
                    else:
                        continue
                    
                    # 检查是否是文件
                    if "filename=\"" in cd_header:
                        # 移除尾部的\r\n--
                        content = content.rstrip(b"\r\n--")
                        if name == "audio_file":
                            # 这是音频文件
                            audio_data = content
                        elif name == "video_file":
                            # 这是视频文件
                            video_data = content
                    else:
                        # 这是普通表单字段
                        content = content.decode("utf-8").rstrip("\r\n")
                        form_data[name] = content
            
            return form_data, audio_data, video_data
        
        # 解析表单数据、音频文件和视频文件
        form_data, audio_data, video_data = parse_multipart(body, boundary)
        
        # 获取参数
        local_ckpt_dir = form_data.get("local_ckpt_dir", "")
        drv_pose = form_data.get("drv_pose", "data/pose/RichardShelby_front_neutral_level1_001.mat")
        bg_img = form_data.get("bg_img", "data/bg/white_bg.png")
        out_name = form_data.get("out_name", "infer_result")
        # 确保out_name不包含.mp4扩展名，避免重复添加
        if out_name.endswith(".mp4"):
            out_name = out_name[:-4]
        
        # 检查音频文件
        if not audio_data:
            raise HTTPException(status_code=400, detail="缺少音频文件")
        
        # 保存音频到本地临时目录（直接使用传入的音频文件，不再进行语音克隆）
        local_audio_name = f"infer_{uuid.uuid4().hex}.wav"
        local_audio_path = os.path.join(cfg.LOCAL_TEMP_DIR, local_audio_name)
        with open(local_audio_path, "wb") as f:
            f.write(audio_data)
        print(f"✅ 音频文件保存：{local_audio_path}")
        
        # 3. 复制最终音频到容器的outside目录
        container_audio_path = os.path.join(cfg.CONTAINER_OUTSIDE_DIR, local_audio_name).replace('\\', '/')
        docker_cp_local_to_container(local_audio_path, container_audio_path)
        
        # 4. 处理参考视频文件
        if video_data:
            # 保存视频到本地临时目录
            local_video_name = f"pose_{uuid.uuid4().hex}.mp4"
            local_video_path = os.path.join(cfg.LOCAL_TEMP_DIR, local_video_name)
            with open(local_video_path, "wb") as f:
                f.write(video_data)
            print(f"✅ 视频文件保存：{local_video_path}")
            
            # 复制视频到容器的outside目录
            container_video_path = os.path.join(cfg.CONTAINER_OUTSIDE_DIR, local_video_name).replace('\\', '/')
            docker_cp_local_to_container(local_video_path, container_video_path)
            print(f"✅ 视频文件复制到容器：{container_video_path}")
            
            # 更新drv_pose为容器中的视频路径
            drv_pose = container_video_path
        elif os.path.exists(drv_pose):
            # 如果drv_pose是本地文件路径，复制到容器
            local_video_path = drv_pose
            local_video_name = os.path.basename(local_video_path)
            container_video_path = os.path.join(cfg.CONTAINER_OUTSIDE_DIR, local_video_name).replace('\\', '/')
            docker_cp_local_to_container(local_video_path, container_video_path)
            print(f"✅ 参考视频文件复制到容器：{container_video_path}")
            
            # 使用容器中的视频路径作为drv_pose
            drv_pose = container_video_path
        else:
            # 使用默认值
            print(f"⚠️  使用指定的参考姿势：{drv_pose}")
        
        # 3. 复制模型到容器（如果本地模型路径不为空）
        if local_ckpt_dir:
            # 检查路径是否存在
            if not os.path.exists(local_ckpt_dir):
                raise HTTPException(status_code=404, detail=f"模型目录不存在：{local_ckpt_dir}")
            
            # 生成容器内模型路径，确保使用正斜杠分隔符
            container_ckpt_dir = f"{cfg.CONTAINER_OUTSIDE_DIR}/{os.path.basename(local_ckpt_dir)}"
            
            # 只复制必要的文件：配置文件和最新的模型检查点
            # 1. 复制配置文件 - 支持多种格式
            config_files = [
                os.path.join(local_ckpt_dir, "config.yaml"),
                os.path.join(local_ckpt_dir, "config.yml"),
                os.path.join(local_ckpt_dir, "hparams.yaml"),
                os.path.join(local_ckpt_dir, "hparams.yml")
            ]
            
            config_file = None
            for cfg_file in config_files:
                if os.path.exists(cfg_file):
                    config_file = cfg_file
                    break
            
            if config_file:
                # 获取原始配置文件名
                config_filename = os.path.basename(config_file)
                container_config_path = os.path.join(container_ckpt_dir, config_filename).replace('\\', '/')
                docker_cp_local_to_container(config_file, container_config_path, skip_if_exists=True)
                print(f"✅ 复制配置文件：{config_file} -> {container_config_path}")
            else:
                # 列出目录内容以便调试
                dir_contents = os.listdir(local_ckpt_dir)
                print(f"📁 目录内容：{local_ckpt_dir} -> {dir_contents}")
                raise HTTPException(status_code=404, detail=f"配置文件不存在于目录 {local_ckpt_dir}。请确保目录中包含 config.yaml、config.yml、hparams.yaml 或 hparams.yml 文件")
            
            # 2. 找到最新的模型检查点
            ckpt_files = [f for f in os.listdir(local_ckpt_dir) if f.startswith("model_ckpt_steps_") and f.endswith(".ckpt")]
            if not ckpt_files:
                raise HTTPException(status_code=404, detail=f"模型检查点不存在于目录：{local_ckpt_dir}")
            
            # 按文件名中的步数排序，选择最新的（最大步数）
            ckpt_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]), reverse=True)
            latest_ckpt = ckpt_files[0]
            
            # 复制最新的模型检查点
            ckpt_file_path = os.path.join(local_ckpt_dir, latest_ckpt)
            container_ckpt_path = os.path.join(container_ckpt_dir, latest_ckpt).replace('\\', '/')
            docker_cp_local_to_container(ckpt_file_path, container_ckpt_path, skip_if_exists=True)
            print(f"✅ 复制最新模型检查点：{ckpt_file_path} -> {container_ckpt_path}")
            
            print(f"✅ 模型文件复制完成：{local_ckpt_dir} -> {container_ckpt_dir}")
        else:
            container_ckpt_dir = cfg.CONTAINER_CKPT_DIR
            print("⚠️  使用容器内默认模型")
        
        # 4. 执行推理
        result = docker_exec_infer(
            container_audio_path=container_audio_path,
            container_ckpt_dir=container_ckpt_dir,
            container_out_path=out_name,
            drv_pose=drv_pose,
            bg_img=bg_img
        )
        
        # 5. 同步结果视频到本地（从outside/infer_out目录）
        # 注意：docker_exec_infer函数会确保输出文件包含.mp4扩展名
        container_video_path = f"{cfg.CONTAINER_OUTSIDE_INFER_DIR}/{out_name}.mp4"
        local_video_path = os.path.join(cfg.LOCAL_TEMP_DIR, f"{out_name}.mp4")
        docker_cp_container_to_local(container_video_path, local_video_path)
        
        return JSONResponse({
            "code": 0,
            "msg": "推理成功",
            "data": {
                "本地生成视频路径": local_video_path,
                "容器视频路径": container_video_path
            }
        })
    except Exception as e:
        return JSONResponse({"code": -1, "msg": f"推理失败：{str(e)}", "data": None}, status_code=500)
# -------------------------- 下载接口 --------------------------
@app.get("/api/download", summary="下载文件")
async def download(file_path: str):
    if not file_path.startswith(cfg.LOCAL_TEMP_DIR) and not file_path.startswith(cfg.LOCAL_CKPT_SAVE_DIR):
        raise HTTPException(status_code=403, detail="禁止访问！")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在！")
    return FileResponse(file_path, filename=os.path.basename(file_path))


# -------------------------- 语音克隆接口 --------------------------
@app.post("/api/clone-voice", summary="语音克隆接口")
async def clone_voice(request: Request):
    """
    语音克隆接口 - 根据参考音频克隆语音
    每次调用时启动容器中的语音克隆API后台，完成后杀掉进程
    """
    try:
        # 解析请求体
        data = await request.json()
        
        # 获取参数
        text = data.get("text", "")
        text_lang = data.get("text_lang", "zh")
        prompt_lang = data.get("prompt_lang", "zh")
        
        print(f"收到语音克隆任务：文本='{text}'")
        
        # 生成唯一的音频文件名
        generated_audio_filename = f"clone_voice_{int(datetime.now().timestamp())}.wav"
        local_save_path = os.path.join(LOCAL_DATA_DIR, generated_audio_filename)
        
        # 获取Base64编码的参考音频内容
        audio_base64 = data.get("reference_audio", "")
        if not audio_base64:
            return JSONResponse({"success": False, "message": "缺少参考音频文件"})
        
        # 解码Base64音频内容
        import base64
        audio_data = base64.b64decode(audio_base64.split(',')[1] if ',' in audio_base64 else audio_base64)
        
        # 保存参考音频到临时文件
        temp_ref_path = os.path.join(LOCAL_DATA_DIR, f"temp_ref_{int(datetime.now().timestamp())}.wav")
        with open(temp_ref_path, "wb") as f:
            f.write(audio_data)
        
        # 启动语音克隆服务
        if not start_voice_clone_service():
            # 删除临时文件
            if os.path.exists(temp_ref_path):
                os.remove(temp_ref_path)
            return JSONResponse({
                "success": False,
                "message": "启动语音克隆服务失败"
            })
        
        # 发送请求到语音克隆服务
        try:
            with open(temp_ref_path, 'rb') as audio_file:
                files = {'ref_audio': ("reference.wav", audio_file, 'audio/wav')}
                data = {
                    "text": text,
                    "text_lang": text_lang,
                    "prompt_lang": prompt_lang,
                    "text_split_method": "cut5",
                    "batch_size": 1
                }
                
                # 添加超时和重试机制
                try:
                    response = requests.post(VOICE_API_URL, data=data, files=files, timeout=60)  # 增加超时时间
                    print(f"语音克隆服务响应状态码: {response.status_code}")
                except requests.exceptions.ConnectionError as e:
                    print(f"连接语音克隆服务失败: {str(e)}")
                    raise
                except requests.exceptions.Timeout as e:
                    print(f"请求语音克隆服务超时: {str(e)}")
                    raise
        finally:
                # 无论成功失败，都关闭语音克隆服务
            stop_voice_clone_service()
        
        # 删除临时文件
        if os.path.exists(temp_ref_path):
            os.remove(temp_ref_path)
        
        if response.status_code == 200:
            # 保存生成的语音到本地
            with open(local_save_path, "wb") as f:
                f.write(response.content)
            print(">>> 语音克隆成功！")
            
            return JSONResponse({
                "success": True,
                "audio_filename": generated_audio_filename
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "语音生成失败"
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 确保服务被关闭
        stop_voice_clone_service()
        return JSONResponse({
            "success": False,
            "message": "连接语音服务失败",
            "detail": str(e)
        })

if __name__ == "__main__": 
    import uvicorn
    
    # 启动主服务（不再自动启动语音克隆服务）
    print(f"🚀 启动主服务...")
    print(f"📡 主服务端口: {cfg.LOCAL_API_PORT}")
    
    # 启动时加上 --reload-dir 避免热重载冲突（可选）
    uvicorn.run(app, host="0.0.0.0", port=cfg.LOCAL_API_PORT, reload=False)