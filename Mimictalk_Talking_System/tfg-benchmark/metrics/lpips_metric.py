"""
LPIPS指标
使用pyiqa计算Learned Perceptual Image Patch Similarity
"""

import numpy as np
import torch

class LPIPSMetric:
    """LPIPS指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化LPIPS指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.metric = None
        self._load_metric()
    
    def _load_metric(self):
        """加载LPIPS指标"""
        try:
            import pyiqa
            self.metric = pyiqa.create_metric('lpips', device=self.device)
            print("✓ LPIPS 指标加载成功")
        except ImportError:
            print("⚠ pyiqa 未安装，LPIPS指标不可用")
            self.metric = None
    
    def calculate(self, real_video, generated_video, video_processor, num_frames=30):
        """
        计算LPIPS
        
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
                'name': 'LPIPS',
                'value': 1.0,
                'scores': [],
                'status': 'error',
                'message': 'pyiqa未安装，LPIPS指标不可用'
            }
        
        print("计算LPIPS...")
        
        # 提取匹配的帧（相同时间点）
        real_frames, gen_frames, matched_indices = video_processor.extract_matched_frames(
            real_video, generated_video, num_frames
        )
        
        if len(real_frames) == 0 or len(gen_frames) == 0:
            return {
                'name': 'LPIPS',
                'value': 1.0,
                'scores': [],
                'status': 'error',
                'message': '无法提取匹配的帧'
            }
        
        print(f"  成功匹配 {len(real_frames)} 对帧")
        
        # 逐帧计算LPIPS
        lpips_scores = []
        for real_frame, gen_frame in zip(real_frames, gen_frames):
            # 转换为张量
            real_tensor = video_processor.frames_to_tensor([real_frame])[0].unsqueeze(0)
            gen_tensor = video_processor.frames_to_tensor([gen_frame])[0].unsqueeze(0)
            
            # 计算LPIPS
            with torch.no_grad():
                score = self.metric(real_tensor, gen_tensor)
                if isinstance(score, torch.Tensor):
                    score = score.item()
                lpips_scores.append(score)
        
        # 计算统计量
        lpips_scores = np.array(lpips_scores)
        mean_lpips = float(np.mean(lpips_scores))
        std_lpips = float(np.std(lpips_scores))
        
        result = {
            'name': 'LPIPS',
            'value': mean_lpips,
            'mean': mean_lpips,
            'std': std_lpips,
            'min': float(np.min(lpips_scores)),
            'max': float(np.max(lpips_scores)),
            'num_frames': len(lpips_scores),
            'matched_indices': matched_indices,
            'scores': lpips_scores.tolist(),
            'status': 'success',
            'interpretation': self._interpret_score(mean_lpips)
        }
        
        print(f"  LPIPS: {mean_lpips:.4f} ± {std_lpips:.4f} (基于 {len(lpips_scores)} 对匹配帧)")
        return result
    
    def _interpret_score(self, score):
        """解释LPIPS分数"""
        if score < 0.1:
            return "感知质量非常高"
        elif score < 0.2:
            return "感知质量较高"
        elif score < 0.3:
            return "感知质量一般"
        else:
            return "感知质量较低"