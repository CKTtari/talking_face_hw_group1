import os
class Config:
    # 容器配置
    CONTAINER_NAME = "mimictalk"
    CONTAINER_DATA_DIR = "/app/data/raw/videos"
    CONTAINER_AUDIO_DIR = "/app/data/raw/examples"
    CONTAINER_CKPT_DIR = "/app/checkpoints_mimictalk"
    CONTAINER_INFER_OUT_DIR = "/app/infer_output"
    CONTAINER_OUTSIDE_DIR = "/app/outside"  # 外部上传文件的容器存储路径
    CONTAINER_OUTSIDE_INFER_DIR = "/app/outside/infer_out"  # 外部输出目录
    # 本地配置
    LOCAL_API_PORT = 8083
    # 使用绝对路径避免路径解析问题
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOCAL_TEMP_DIR = os.path.join(BASE_DIR, "temp")
    LOCAL_CKPT_DIR = os.path.join(BASE_DIR, "local_ckpts")  # 本地模型存储目录
    LOCAL_CKPT_SAVE_DIR = os.path.join(BASE_DIR, "local_ckpts")  # 本地模型保存目录（与LOCAL_CKPT_DIR一致）
    LOCAL_LOG_DIR = os.path.join(BASE_DIR, "train_logs")  # 新增：保存训练日志
    # 自动创建目录
    os.makedirs(LOCAL_TEMP_DIR, exist_ok=True, mode=0o755)
    os.makedirs(LOCAL_CKPT_SAVE_DIR, exist_ok=True, mode=0o755)
    os.makedirs(LOCAL_LOG_DIR, exist_ok=True, mode=0o755)
cfg = Config()