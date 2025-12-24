# Mimictalk Docker 配置说明

基于我们的配置经验，自行构建docker镜像耗时较长、在不同机器上配置环境也会遇到各种问题。
因此，我们建议直接使用我们提供的docker镜像。以下构建步骤仅供参考。

## 使用docker镜像
将mimictalk_hw.tar放到Mimictalk_Talking_System\MimicTalk中
执行以下命令生成容器：
```
docker load -i mimictalk.tar
docker compose up -d
```
## 使用源代码从头构建（不推荐）
按照正常的docker构建流程，从dockerfile构建镜像。理论上没问题，但可能遇到网络问题或者进去以后可能有其他环境问题。可以联系组长解决。

## 下载预训练与第三方模型
### 3DMM BFM模型
下载3DMM BFM模型：[Google Drive](https://drive.google.com/drive/folders/1o4t5YIw7w4cMUN4bgU9nPf6IyWVG1bEk?usp=sharing) 或 [BaiduYun Disk](https://pan.baidu.com/s/1aqv1z_qZ23Vp2VP4uxxblQ?pwd=m9q5 ) 提取码: m9q5


下载完成后，放置全部的文件到`deep_3drecon/BFM`里，文件结构如下：
```
deep_3drecon/BFM/
├── 01_MorphableModel.mat
├── BFM_exp_idx.mat
├── BFM_front_idx.mat
├── BFM_model_front.mat
├── Exp_Pca.bin
├── facemodel_info.mat
├── index_mp468_from_mesh35709.npy
├── mediapipe_in_bfm53201.npy
└── std_exp.txt
```

### 预训练模型
下载预训练的MimicTalk相关Checkpoints：[Google Drive](https://drive.google.com/drive/folders/1Kc6ueDO9HFDN3BhtJCEKNCZtyKHSktaA?usp=sharing) or [BaiduYun Disk](https://pan.baidu.com/s/1nQKyGV5JB6rJtda7qsThUg?pwd=mimi) 提取码: mimi
  
下载完成后，放置全部的文件到`checkpoints`与`checkpoints_mimictalk`里并解压，文件结构如下：
```
checkpoints/
├── mimictalk_orig
│   └── os_secc2plane_torso
│       ├── config.yaml
│       └── model_ckpt_steps_100000.ckpt
|-- 240112_icl_audio2secc_vox2_cmlr
│     ├── config.yaml
│     └── model_ckpt_steps_1856000.ckpt
└── pretrained_ckpts
    └── mit_b0.pth

checkpoints_mimictalk/
└── German_20s
    ├── config.yaml
    └── model_ckpt_steps_10000.ckpt
```

## MimicTalk训练与推理命令
```
python inference/train_mimictalk_on_a_video.py # train the model, this may take 10 minutes for 2,000 steps
python inference/mimictalk_infer.py # infer the model
```

## 语音克隆模型
### 如果是从镜像构建，无需进行任何操作。
###　如果从源代码构建：
请手动下载GPT_SoVITS和tools两个文件夹放到Voice_Model目录下

通过网盘分享的文件：Group1大文件.zip
链接: https://pan.baidu.com/s/11kA6_WdoyNHOtsUvYc66lQ?pwd=x4vp 提取码: x4vp 
--来自百度网盘超级会员v6的分享

并执行：
```
conda create -n voice python=3.9
conda activate voice
pip install -r requirements.txt
```

可以参考原项目https://github.com/RVC-Boss/GPT-SoVITS/blob/main/docs/cn/README.md中的环境配置。
