## 1.安装依赖requirement.txt
## 2.确定你的容器名字，代码中容器名是mimictalk（在config.py中修改）
## 3.打开api：运行
python3 main.py
## 4.调用预训练：
```bash
curl -X POST "http://你的华为云ip/私有ip:8080/api/train" \
  -F "video_file=@/mnt/new_speaker.mp4" \
  -F "max_updates=20000" \
  -F "speaker_name=new_speaker" \
  -F "torso_ckpt=checkpoints/mimictalk_orig/os_secc2plane_torso" \
  -F "batch_size=4" \
  -F "lr=0.0001" \
  -F "lr_triplane=0.0001"
```
## 5.调用推理：
```bash
curl -X POST "http://你的华为云ip/私有ip:8080/api/infer"   -F "audio_file=@/root/data/raw/examples/80_vs_60_10s.wav"   -F "local_ckpt_dir=./local_ckpts/new_speaker/"   -F "out_name=new_speaker_final.mp4"   -F "drv_pose=/root/data/raw/videos/new_speaker.mp4"   -F "bg_img=/root/data/raw/examples/bg.png"
````
