# 使用Docker运行MimicTalk

本指南提供了如何使用Docker和Docker Compose来构建和运行MimicTalk项目的详细步骤。

## 前提条件

- 安装Docker: [Docker官方文档](https://docs.docker.com/get-docker/)
- 安装Docker Compose: [Docker Compose官方文档](https://docs.docker.com/compose/install/)
- NVIDIA Docker支持 (如果需要GPU加速): [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/[your-username]/MimicTalk.git
cd MimicTalk
```

### 2. 构建Docker镜像

使用Docker Compose构建镜像：

```bash
docker-compose build
```

这将创建一个包含所有依赖项的Docker镜像。

### 3. 下载预训练模型

按照项目README中的说明下载预训练模型，并将其放置在相应的目录中：

- `checkpoints/` 目录
- `checkpoints_mimictalk/` 目录

### 4. 运行容器

使用Docker Compose运行容器：

```bash
docker-compose up -d
```

### 5. 进入容器

```bash
docker exec -it mimictalk bash
```

### 6. 运行推理

在容器内，您可以按照项目文档运行推理：

```bash
# 运行MimicTalk推理
python inference/app_mimictalk.py

# 或者运行Real3D-Portrait推理
python inference/app_real3dportrait.py
```

### 7. 访问Gradio界面

如果运行了Gradio界面应用，您可以通过以下地址访问：

```
http://localhost:7860
```

## 数据持久化

docker-compose.yml文件中已配置以下卷挂载：

- `./checkpoints` 挂载到 `/app/checkpoints`
- `./checkpoints_mimictalk` 挂载到 `/app/checkpoints_mimictalk`
- `./data` 挂载到 `/app/data`
- `./infer_outs` 挂载到 `/app/infer_outs`

这确保了数据在容器重启后仍然保留。

## GPU支持

docker-compose.yml文件已配置为使用NVIDIA GPU（如果可用）。请确保已正确安装NVIDIA Docker支持。

## 自定义配置

如果需要修改配置，可以编辑以下文件：

- `Dockerfile`：修改基础镜像、安装的依赖项等
- `docker-compose.yml`：修改端口映射、卷挂载、GPU配置等

## 故障排除

### 构建失败

如果构建过程中遇到网络问题（特别是安装pytorch3d时），可以尝试使用代理或修改Dockerfile中的源。

### GPU不可用

确保：
1. 已正确安装NVIDIA驱动
2. 已安装NVIDIA Container Toolkit
3. Docker守护进程已重启：`sudo systemctl restart docker`

### 内存不足

如果遇到内存问题，可以在docker-compose.yml中增加`shm_size`值。

## 停止容器

```bash
docker-compose down
```