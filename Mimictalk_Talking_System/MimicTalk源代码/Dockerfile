# 使用官方cuda镜像作为基础镜像
FROM nvcr.io/nvidia/cuda:12.1.0-cudnn8-devel-ubuntu20.04

# 设置工作目录
WORKDIR /app

# 设置非交互模式，指定时区
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        wget \
        bzip2 \
        ca-certificates \
        libgl1-mesa-glx \
        libglib2.0-0 \
        gcc \
        g++ \
        cmake \
        libasound2-dev \
        libsndfile1-dev \
        portaudio19-dev \
        python3-dev \
        tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 新增：安装系统图形/显卡依赖库
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libegl1-mesa \
        libgles2-mesa \
        libnvidia-gl-570 \
        mesa-utils \
        x11-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh

ENV PATH=$CONDA_DIR/bin:$PATH

# 接受conda服务条款并创建环境
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    conda create -n mimictalk python=3.9 -y

SHELL ["conda", "run", "-n", "mimictalk", "/bin/bash", "-c"]

# 复制 requirements.txt
COPY docs/prepare_env/requirements.txt .


RUN conda run -n mimictalk pip install --no-cache-dir --upgrade pip setuptools wheel cython numpy==1.26.4
# 1. 基础数据/科学计算包（变化少、依赖稳定）
RUN conda run -n mimictalk pip install --no-cache-dir \
    numba==0.60.0 pandas scipy==1.11.1 scikit-learn scikit-image

# 2. 日志/可视化包
RUN conda run -n mimictalk pip install --no-cache-dir \
    tensorboard tensorboardX matplotlib

# 3. 音频处理相关包 - 使用 conda-forge 安装预编译的 pyaudio 和 pyworld（避免编译问题）
RUN conda install -n mimictalk -c conda-forge pyworld pyaudio -y

RUN conda run -n mimictalk pip install --no-cache-dir \
    python_speech_features resampy librosa==0.9.2 praat-parselmouth \
    soundfile webrtcvad pyloudnorm pypinyin==0.42.0 soxr

# 4. 视觉/图像处理相关包
# 1. 安装ffmpeg依赖（解决av包安装问题）
RUN conda run -n mimictalk conda install -y ffmpeg -c conda-forge

# 2. 装预编译dlib（加速face_alignment）
RUN conda run -n mimictalk conda install -y dlib -c conda-forge

# 安装PyTorch相关（指定CUDA 12.1版本，按要求简化命令）
RUN conda run -n mimictalk pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 -f https://mirrors.aliyun.com/pytorch-wheels/cu121/

# 安装face_alignment（严格在PyTorch之后安装）
RUN conda run -n mimictalk pip install --default-timeout=2000 face_alignment -i https://mirrors.aliyun.com/pypi/simple/

# 安装kornia等依赖
RUN conda run -n mimictalk pip install --default-timeout=2000 kornia==0.5.0 lpips mediapipe av timm -i https://mirrors.aliyun.com/pypi/simple/

# 安装opencv-python
RUN conda run -n mimictalk pip install --default-timeout=2000 \
    opencv_python \
    -i https://mirrors.aliyun.com/pypi/simple/

# 5. 3D/几何处理包
RUN conda run -n mimictalk pip install --no-cache-dir \
    trimesh PyMCubes

# 6. 工具/框架相关包（按要求统一命令格式，指定moviepy==1.0.3）
RUN conda run -n mimictalk pip install --no-cache-dir configargparse ffmpeg-python moviepy==1.0.3 dearpygui ninja protobuf decord pillow einops beartype torchode torchdiffeq websocket-client torchshow

# 安装pretrainedmodels等模型/文本处理依赖（按要求指定transformers==4.33.2）
RUN conda run -n mimictalk pip install --no-cache-dir pretrainedmodels textgrid transformers==4.33.2

# 新增：安装iopath 和 huggingface_hub==0.19.3
RUN conda run -n mimictalk pip install --no-cache-dir iopath huggingface_hub==0.19.3

RUN conda run -n mimictalk pip install --no-cache-dir fastapi==0.112.2 gradio==3.50.2

# 安装mmcv（通过mim，按要求去掉版本号显式指定）
RUN conda run -n mimictalk pip install --no-cache-dir openmim==0.3.9 
RUN conda run -n mimictalk mim install mmcv

# 安装pytorch3d
RUN conda run -n mimictalk conda install -y \
    https://conda.anaconda.org/pytorch3d/linux-64/pytorch3d-0.7.8-py39_cu121_pyt240.tar.bz2

# 复制项目代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app

# 默认进入 conda 环境
CMD ["conda", "run", "-n", "mimictalk", "tail", "-f", "/dev/null"]