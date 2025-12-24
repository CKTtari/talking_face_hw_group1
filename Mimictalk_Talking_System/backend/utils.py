import os
import uuid
import subprocess
from config import cfg
def docker_cp_local_to_container(local_path, container_path, skip_if_exists=False):
    """本地文件复制到容器内"""
    # 将容器路径的反斜杠替换为正斜杠，因为容器内是Linux系统
    container_path = container_path.replace('\\', '/')
    
    # 先创建容器内的目标目录
    container_dir = os.path.dirname(container_path)
    if container_dir:
        container_dir = container_dir.replace('\\', '/')
        create_dir_cmd = f"docker exec mimictalk mkdir -p {container_dir}"
        print(f"📁 创建容器内目录：{create_dir_cmd}")
        subprocess.run(create_dir_cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    # 检查文件是否已存在于容器内
    if skip_if_exists:
        check_cmd = f"docker exec mimictalk test -f {container_path} && echo 'exists' || echo 'not exists'"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.stdout.strip() == 'exists':
            print(f"✅ 容器内文件已存在，跳过复制：{container_path}")
            return True
    
    # 文件不存在或不需要跳过，执行复制逻辑
    if not skip_if_exists:
        # 检查并删除容器内已存在的文件（解决权限问题）
        delete_cmd = f"docker exec mimictalk rm -f {container_path}"
        print(f"🧹 清理容器内已存在的文件：{delete_cmd}")
        subprocess.run(delete_cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    cmd = f"docker cp {local_path} mimictalk:{container_path}"
    print(f"📤 执行复制命令：{cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise Exception(f"文件复制到容器失败：命令={cmd}，错误={result.stderr}")
    return True
def docker_cp_container_to_local(container_path, local_path):
    """容器内文件复制到本地"""
    cmd = f"docker cp mimictalk:{container_path} {local_path}"
    print(f"📥 执行复制命令：{cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise Exception(f"文件从容器复制失败：命令={cmd}，错误={result.stderr}")
    return True
def docker_exec_train(container_video_path, max_updates, container_work_dir, torso_ckpt="checkpoints/mimictalk_orig/os_secc2plane_torso", batch_size=1, lr=0.001, lr_triplane=0.005):
    """执行容器内训练命令（直接运行训练脚本）"""
    # 将容器路径的反斜杠替换为正斜杠，因为容器内是Linux系统
    container_video_path = container_video_path.replace('\\', '/')
    container_work_dir = container_work_dir.replace('\\', '/')
    
    # 构建bash命令内容 - 直接运行训练脚本，不需要单独extract
    bash_cmd = f"export PYTHONUNBUFFERED=1 && source activate mimictalk && cd /app && export PYTHONPATH=./ && python inference/train_mimictalk_on_a_video.py --video_id {container_video_path} --max_updates {max_updates} --work_dir {container_work_dir} --batch_size {batch_size} --lr {lr} --lr_triplane {lr_triplane} --torso_ckpt {torso_ckpt} --lora_mode secc2plane_sr --lora_r 2"
    print(f"🚀 执行容器内训练命令：docker exec mimictalk bash -c '{bash_cmd}'")
    
    # 使用列表形式的命令，避免引号转义问题
    cmd = ["docker", "exec", "mimictalk", "bash", "-c", bash_cmd]
    
    # 捕获完整日志（包括图像分割步骤）
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding='utf-8'
    )
    
    # 实时输出日志（让用户看到分割步骤是否执行）
    all_output = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            print(f"📝 容器内日志：{line.strip()}")  # 明确标记是容器内输出
            all_output.append(line)
            yield line  # 流式返回给curl客户端

    
    # 收集剩余输出
    remaining_output = process.stdout.read()
    if remaining_output:
        print(remaining_output.strip())
        all_output.append(remaining_output)
    
    # 检查训练是否成功
    if process.returncode != 0:
        full_output = "".join(all_output)
        raise Exception(f"训练失败：命令={cmd}，日志=\n{full_output}")
    
    return "".join(all_output)

def docker_exec_infer(container_audio_path, container_ckpt_dir, container_out_path, drv_pose="static", bg_img=""):
    """执行容器内推理命令"""
    container_audio_16k = container_audio_path.replace(".wav", "_16k.wav").replace(".mp3", "_16k.wav")
    
    # 1. 转码音频（简化命令，避免引号问题）
    resample_cmd = f"source /opt/conda/etc/profile.d/conda.sh && conda activate mimictalk && cd /app && ffmpeg -i {container_audio_path} -ar 16000 -ac 1 -y {container_audio_16k}"
    print(f"🚀 执行转码命令：docker exec mimictalk bash -c '{resample_cmd}'")
    result = subprocess.run(
        ["docker", "exec", "mimictalk", "bash", "-c", resample_cmd],
        capture_output=False,
        timeout=600
    )
    if result.returncode != 0:
        raise Exception(f"音频转码失败，返回码：{result.returncode}")
    
    # 2. 推理命令（简化命令，避免引号问题）
    bg_arg = f"--bg_img {bg_img}" if bg_img else ""
    container_out_dir = cfg.CONTAINER_OUTSIDE_INFER_DIR
    
    # 将输出目录与文件名合并，因为脚本不支持--out_dir参数
    # 确保文件名包含.mp4扩展名，以便FFmpeg正确识别输出格式
    full_out_path = f"{container_out_dir}/{container_out_path}"
    if not full_out_path.endswith('.mp4'):
        full_out_path += '.mp4'
    
    infer_cmd = f"source /opt/conda/etc/profile.d/conda.sh && conda activate mimictalk && cd /app && mkdir -p {container_out_dir} && export PYTHONPATH=./ && python inference/mimictalk_infer.py --drv_aud {container_audio_16k} --torso_ckpt {container_ckpt_dir} --drv_pose {drv_pose} --drv_style {drv_pose} --out_name {full_out_path} --out_mode final {bg_arg}"
    print(f"\n🚀 执行推理命令：docker exec mimictalk bash -c '{infer_cmd}'")
    result = subprocess.run(
        ["docker", "exec", "mimictalk", "bash", "-c", infer_cmd],
        capture_output=False,
        timeout=6000
    )
    if result.returncode != 0:
        raise Exception(f"推理失败，返回码：{result.returncode}")
    return True

def sync_ckpt_from_container_to_local(container_ckpt_dir, local_speaker_name):
    """训练完成后，自动把容器内模型复制到本地"""
    local_ckpt_dir = os.path.join(cfg.LOCAL_CKPT_SAVE_DIR, local_speaker_name)
    os.makedirs(local_ckpt_dir, exist_ok=True)
    cmd = f"docker cp mimictalk:{container_ckpt_dir}/. {local_ckpt_dir}/"
    print(f"📥 同步模型命令：{cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1000)
    if result.returncode != 0:
        raise Exception(f"模型从容器复制到本地失败：命令={cmd}，错误={result.stderr}")
    print(f"✅ 模型已保存到本地：{local_ckpt_dir}")
    return local_ckpt_dir
def sync_ckpt_from_local_to_container(local_ckpt_dir):
    """推理前，自动把本地模型复制到容器内临时路径"""
    container_temp_ckpt_dir = f"/app/checkpoints_mimictalk/local_sync_ckpt"
    print(f"🗑️  清理容器内旧模型：docker exec mimictalk rm -rf {container_temp_ckpt_dir}")
    subprocess.run(f"docker exec mimictalk rm -rf {container_temp_ckpt_dir}", shell=True, capture_output=True, text=True, timeout=10)
    cmd = f"docker cp {local_ckpt_dir}/. mimictalk:{container_temp_ckpt_dir}/"
    print(f"📤 同步本地模型到容器：{cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise Exception(f"本地模型复制到容器失败：命令={cmd}，错误={result.stderr}")
    return container_temp_ckpt_dir