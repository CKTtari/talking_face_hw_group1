"""
FID指标
使用pyiqa计算Fréchet Inception Distance
"""

import os
import tempfile
import numpy as np
import cv2
import torch
from PIL import Image

class FIDMetric:
    """FID指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化FID指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.metric = None
        self._load_metric()
    
    def _load_metric(self):
        """加载FID指标"""
        try:
            import pyiqa
            # 注意：pyiqa的FID需要安装clean-fid
            # pip install clean-fid
            self.metric = pyiqa.create_metric('fid', device=self.device)
            print("✓ FID 指标加载成功")
        except ImportError:
            print("⚠ pyiqa 未安装，FID指标不可用")
            self.metric = None
        except Exception as e:
            print(f"⚠ FID指标初始化失败: {e}")
            self.metric = None
    
    def _save_frames_to_temp_dir(self, frames, temp_dir):
        """
        保存帧到临时目录
        
        Args:
            frames: 帧列表
            temp_dir: 临时目录路径
            
        Returns:
            list: 保存的图像文件路径列表
        """
        image_paths = []
        for i, frame in enumerate(frames):
            # 转换为RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 保存为临时文件
            img_path = os.path.join(temp_dir, f'frame_{i:04d}.png')
            cv2.imwrite(img_path, frame_rgb)
            image_paths.append(img_path)
        
        return image_paths
    
    def calculate(self, real_video, generated_video, video_processor, num_frames=30):
        """
        计算FID
        
        Args:
            real_video: 真实视频路径
            generated_video: 生成视频路径
            video_processor: 视频处理器实例
            num_frames: 采样帧数
            
        Returns:
            dict: 计算结果
        """
        if self.metric is None:
            return {
                'name': 'FID',
                'value': float('inf'),
                'status': 'error',
                'message': 'pyiqa未安装或初始化失败，FID指标不可用'
            }
        
        print("计算FID...")
        
        # 从两个视频提取帧
        real_frames, gen_frames, matched_indices = video_processor.extract_matched_frames(
            real_video, generated_video, num_frames
        )
        
        if len(real_frames) == 0 or len(gen_frames) == 0:
            return {
                'name': 'FID',
                'value': float('inf'),
                'status': 'error',
                'message': '无法从视频提取足够的帧'
            }
        
        # 创建临时目录保存图像
        with tempfile.TemporaryDirectory() as temp_dir:
            real_temp_dir = os.path.join(temp_dir, 'real')
            gen_temp_dir = os.path.join(temp_dir, 'gen')
            os.makedirs(real_temp_dir, exist_ok=True)
            os.makedirs(gen_temp_dir, exist_ok=True)
            
            # 保存帧到临时目录
            real_paths = self._save_frames_to_temp_dir(real_frames, real_temp_dir)
            gen_paths = self._save_frames_to_temp_dir(gen_frames, gen_temp_dir)
            
            try:
                # 计算FID - 使用图像目录
                fid_score = self.metric(gen_temp_dir, real_temp_dir)
                
                # 转换为Python浮点数
                if isinstance(fid_score, torch.Tensor):
                    fid_score = fid_score.item()
                
                result = {
                    'name': 'FID',
                    'value': float(fid_score),
                    'num_real_frames': len(real_frames),
                    'num_gen_frames': len(gen_frames),
                    'status': 'success',
                    'interpretation': self._interpret_score(fid_score)
                }
                
                print(f"  FID: {fid_score:.4f}")
                return result
                
            except Exception as e:
                print(f"  FID计算失败: {e}")
                
                # 尝试替代方法：如果上面的方法失败，尝试直接计算
                try:
                    return self._calculate_direct_fid(real_frames, gen_frames)
                except Exception as e2:
                    print(f"  直接计算FID也失败: {e2}")
                    
                    return {
                        'name': 'FID',
                        'value': float('inf'),
                        'status': 'error',
                        'message': f'FID计算失败: {str(e)}'
                    }
    
    def _calculate_direct_fid(self, real_frames, gen_frames):
        """
        直接计算FID（如果pyiqa的目录方式失败）
        
        Args:
            real_frames: 真实帧列表
            gen_frames: 生成帧列表
            
        Returns:
            dict: 计算结果
        """
        try:
            import cleanfid
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                real_dir = os.path.join(temp_dir, 'real')
                gen_dir = os.path.join(temp_dir, 'gen')
                os.makedirs(real_dir, exist_ok=True)
                os.makedirs(gen_dir, exist_ok=True)
                
                # 保存图像
                for i, frame in enumerate(real_frames):
                    img_path = os.path.join(real_dir, f'real_{i:04d}.png')
                    cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                for i, frame in enumerate(gen_frames):
                    img_path = os.path.join(gen_dir, f'gen_{i:04d}.png')
                    cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # 使用clean-fid计算
                fid_score = cleanfid.compute_fid(real_dir, gen_dir)
                
                result = {
                    'name': 'FID',
                    'value': float(fid_score),
                    'num_real_frames': len(real_frames),
                    'num_gen_frames': len(gen_frames),
                    'status': 'success',
                    'interpretation': self._interpret_score(fid_score),
                    'note': '使用clean-fid计算'
                }
                
                print(f"  FID (clean-fid): {fid_score:.4f}")
                return result
                
        except ImportError:
            raise Exception("clean-fid未安装，请运行: pip install clean-fid")
    
    def _interpret_score(self, score):
        """解释FID分数（越低越好）"""
        if score < 10:
            return "分布非常接近"
        elif score < 30:
            return "分布比较接近"
        elif score < 50:
            return "分布有一定差异"
        elif score < 100:
            return "分布差异较大"
        else:
            return "分布差异很大"