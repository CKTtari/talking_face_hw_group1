
老蒋音频是原论文自带的示例。

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
简化版：
```
python inference/train_mimictalk_on_a_video.py # train the model, this may take 10 minutes for 2,000 steps
python inference/mimictalk_infer.py # infer the model
```
推荐命令：
python -m inference.mimictalk_infer --a2m_ckpt checkpoints/240112_icl_audio2secc_vox2_cmlr --torso_ckpt checkpoints_mimictalk/Lieu --drv_aud data/raw/examples/80_vs_60_10s.wav --drv_pose data/raw/videos/Lieu.mp4 --out_name LIEU.mp4 --out_mode final