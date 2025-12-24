"""
SSIM指标
使用pyiqa计算Structural Similarity Index
"""

import numpy as np
import torch

class SSIMMetric:
    """SSIM指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化SSIM指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.metric = None
        self._load_metric()
    
    def _load_metric(self):
        """加载SSIM指标"""
        try:
            import pyiqa
            self.metric = pyiqa.create_metric('ssim', device=self.device)
            print("✓ SSIM 指标加载成功")
        except ImportError:
            print("⚠ pyiqa 未安装，SSIM指标不可用")
            self.metric = None
    
    def calculate(self, real_video, generated_video, video_processor, num_frames=30):
        """
        计算SSIM
        
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
                'name': 'SSIM',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': 'pyiqa未安装，SSIM指标不可用'
            }
        
        print("计算SSIM...")
        
        # 提取匹配的帧（相同时间点）
        real_frames, gen_frames, matched_indices = video_processor.extract_matched_frames(
            real_video, generated_video, num_frames
        )
        
        if len(real_frames) == 0 or len(gen_frames) == 0:
            return {
                'name': 'SSIM',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': '无法提取匹配的帧'
            }
        
        print(f"  成功匹配 {len(real_frames)} 对帧")
        
        # 逐帧计算SSIM
        ssim_scores = []
        for real_frame, gen_frame in zip(real_frames, gen_frames):
            # 转换为张量
            real_tensor = video_processor.frames_to_tensor([real_frame])[0].unsqueeze(0)
            gen_tensor = video_processor.frames_to_tensor([gen_frame])[0].unsqueeze(0)
            
            # 计算SSIM
            with torch.no_grad():
                score = self.metric(real_tensor, gen_tensor)
                if isinstance(score, torch.Tensor):
                    score = score.item()
                ssim_scores.append(score)
        
        # 计算统计量
        ssim_scores = np.array(ssim_scores)
        mean_ssim = float(np.mean(ssim_scores))
        std_ssim = float(np.std(ssim_scores))
        
        result = {
            'name': 'SSIM',
            'value': mean_ssim,
            'mean': mean_ssim,
            'std': std_ssim,
            'min': float(np.min(ssim_scores)),
            'max': float(np.max(ssim_scores)),
            'num_frames': len(ssim_scores),
            'matched_indices': matched_indices,
            'scores': ssim_scores.tolist(),
            'status': 'success',
            'interpretation': self._interpret_score(mean_ssim)
        }
        
        print(f"  SSIM: {mean_ssim:.4f} ± {std_ssim:.4f} (基于 {len(ssim_scores)} 对匹配帧)")
        return result
    
    def _interpret_score(self, score):
        """解释SSIM分数"""
        if score > 0.9:
            return "结构相似度非常高"
        elif score > 0.8:
            return "结构相似度较高"
        elif score > 0.6:
            return "结构相似度一般"
        else:
            return "结构相似度较低"