# Talking Face Generation Benchmark
This project provides flexible, combinable evaluation using the following metrics: LSE-C (Lip Sync Error – Confidence), LSE-D (Lip Sync Error – Distance), NIQE, SSIM, FID, PSNR, Identity, and LPIPS.
## Download Checkpoints
First download syncnet and face detection models for LSE-C and LSE-D.
```
mkdir models
wget http://www.robots.ox.ac.uk/~vgg/software/lipsync/data/syncnet_v2.model -O models/syncnet.pth
wget https://www.robots.ox.ac.uk/~vgg/software/lipsync/data/sfd_face.pth -O models/sfd_face.pth
```
## Install
```
conda create -n tfg_benchmark python=3.10
conda activate trg_benchmark

pip install -r requirements.txt
```
Then download syncnet_python
```
mkdir third_party
cd third_party
git clone https://github.com/joonson/syncnet_python.git
cd ..
```
## Install with Docker

### Install NVIDIA Container Toolkit
```
sudo apt-get update

sudo apt-get install -y ca-certificates curl gnupg

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /etc/apt/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

sudo apt-get install -y nvidia-container-toolkit

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
### Build and Run
```
docker build -t tfg_benchmark:latest .
docker-compose run --rm tfg_benchmark
```

## Run
We provide several presets for different requirements, you can check `metrics_config.py` for more details.

You can use different presets to evaluate different metrics.
```
python combined_main.py     --reference eval_data/Lieu.mp4     --generated eval_data/Lieu_gen.mp4     --syncnet_model models/syncnet.pth     --preset full
```
All metrics needs `generated` video as input. For Sync metrics(LSE-C and LSE-D), `reference` video is not nessesary, and other metrics need `reference` video as ground truth.

## Results on Mimictalk
| Method       | LSE-C ↓ | LSE-D ↓ | PSNR ↑ | SSIM ↑ | FID↓ | LPIPS ↑ | NIQE ↓ | IDENTITY ↑ |
|--------------|---------|---------|--------|--------|------|---------|--------|------------|
| Mimictalk    | 0.25    | 0.43   | 25.60  | 0.86   | 22.20| 0.10    | 5.49   | 0.94       |