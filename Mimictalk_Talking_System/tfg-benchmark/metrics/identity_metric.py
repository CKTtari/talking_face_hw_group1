"""
身份相似度指标
使用FaceNet计算源图像与生成视频的人脸相似度
"""

import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms

class IdentityMetric:
    """身份相似度指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化身份相似度指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.model = None
        self._load_model()
        
        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
    
    def _load_model(self):
        """加载FaceNet模型"""
        try:
            from facenet_pytorch import InceptionResnetV1
            self.model = InceptionResnetV1(pretrained='vggface2').to(self.device)
            self.model.eval()
            print("✓ FaceNet 模型加载成功")
        except ImportError:
            print("⚠ facenet-pytorch 未安装，使用简化版本")
            self.model = self._create_simple_model()
    
    def _create_simple_model(self):
        """创建简化的人脸特征提取模型"""
        import torch.nn as nn
        
        class SimpleFaceNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 32, 3, 1, 1)
                self.conv2 = nn.Conv2d(32, 64, 3, 1, 1)
                self.conv3 = nn.Conv2d(64, 128, 3, 1, 1)
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(128, 512)
                
            def forward(self, x):
                x = F.relu(self.conv1(x))
                x = F.relu(self.conv2(x))
                x = F.relu(self.conv3(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                x = self.fc(x)
                return F.normalize(x, p=2, dim=1)
        
        model = SimpleFaceNet().to(self.device)
        model.eval()
        return model
    
    def extract_face_feature(self, image):
        """
        从图像提取人脸特征
        
        Args:
            image: 图像路径或numpy数组
            
        Returns:
            numpy array: 特征向量
        """
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                return None
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL图像并预处理
        img_pil = Image.fromarray(img_rgb)
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        
        # 提取特征
        with torch.no_grad():
            feature = self.model(img_tensor)
            return feature.cpu().numpy().flatten()
    
    def calculate(self, source_image, generated_video, video_processor, num_frames=30):
        """
        计算身份相似度
        
        Args:
            source_image: 源身份图像（路径或numpy数组）
            generated_video: 生成视频路径
            video_processor: 视频处理器实例
            num_frames: 采样帧数
            
        Returns:
            dict: 计算结果
        """
        from utils.file_utils import FileUtils
        
        print("计算身份相似度...")
        
        # 提取源图像特征
        source_feature = self.extract_face_feature(source_image)
        if source_feature is None:
            return {
                'name': '身份相似度',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': '无法从源图像提取人脸特征'
            }
        
        # 从视频提取帧
        frames, num_extracted = video_processor.extract_frames(generated_video, num_frames)
        if num_extracted == 0:
            return {
                'name': '身份相似度',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': '无法从视频提取帧'
            }
        
        # 计算每帧的相似度
        similarity_scores = []
        for frame in frames:
            frame_feature = self.extract_face_feature(frame)
            if frame_feature is not None:
                # 计算余弦相似度
                similarity = np.dot(source_feature, frame_feature) / (
                    np.linalg.norm(source_feature) * np.linalg.norm(frame_feature)
                )
                similarity_scores.append(similarity)
        
        if len(similarity_scores) == 0:
            return {
                'name': '身份相似度',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': '无法从视频帧提取人脸特征'
            }
        
        # 计算统计量
        similarity_scores = np.array(similarity_scores)
        mean_similarity = float(np.mean(similarity_scores))
        std_similarity = float(np.std(similarity_scores))
        
        result = {
            'name': '身份相似度',
            'value': mean_similarity,
            'mean': mean_similarity,
            'std': std_similarity,
            'min': float(np.min(similarity_scores)),
            'max': float(np.max(similarity_scores)),
            'num_frames': len(similarity_scores),
            'scores': similarity_scores.tolist(),
            'status': 'success',
            'interpretation': self._interpret_score(mean_similarity)
        }
        
        print(f"  身份相似度: {mean_similarity:.4f} ± {std_similarity:.4f}")
        return result
    
    def _interpret_score(self, score):
        """解释分数含义"""
        if score > 0.8:
            return "身份保持非常好"
        elif score > 0.6:
            return "身份保持良好"
        elif score > 0.4:
            return "身份保持一般"
        else:
            return "身份保持较差"