"""
PSNR指标
使用pyiqa计算Peak Signal-to-Noise Ratio
"""

import numpy as np
import torch

class PSNRMetric:
    """PSNR指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化PSNR指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.metric = None
        self._load_metric()
    
    def _load_metric(self):
        """加载PSNR指标"""
        try:
            import pyiqa
            self.metric = pyiqa.create_metric('psnr', device=self.device)
            print("✓ PSNR 指标加载成功")
        except ImportError:
            print("⚠ pyiqa 未安装，PSNR指标不可用")
            self.metric = None
    
    def calculate(self, real_video, generated_video, video_processor, num_frames=30):
        """
        计算PSNR
        
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
                'name': 'PSNR',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': 'pyiqa未安装，PSNR指标不可用'
            }
        
        print("计算PSNR...")
        
        # 从两个视频提取帧
        real_frames, gen_frames, matched_indices = video_processor.extract_matched_frames(
            real_video, generated_video, num_frames
        )
        
        if len(real_frames) == 0 or len(gen_frames) == 0:
            return {
                'name': 'PSNR',
                'value': 0.0,
                'scores': [],
                'status': 'error',
                'message': '无法从视频提取足够且匹配的帧'
            }
        
        # 逐帧计算PSNR
        psnr_scores = []
        for real_frame, gen_frame in zip(real_frames, gen_frames):
            # 转换为张量
            real_tensor = video_processor.frames_to_tensor([real_frame])[0].unsqueeze(0)
            gen_tensor = video_processor.frames_to_tensor([gen_frame])[0].unsqueeze(0)
            
            # 计算PSNR
            with torch.no_grad():
                score = self.metric(real_tensor, gen_tensor)
                if isinstance(score, torch.Tensor):
                    score = score.item()
                psnr_scores.append(score)
        
        # 计算统计量
        psnr_scores = np.array(psnr_scores)
        mean_psnr = float(np.mean(psnr_scores))
        std_psnr = float(np.std(psnr_scores))
        
        result = {
            'name': 'PSNR',
            'value': mean_psnr,
            'mean': mean_psnr,
            'std': std_psnr,
            'min': float(np.min(psnr_scores)),
            'max': float(np.max(psnr_scores)),
            'num_frames': len(psnr_scores),
            'scores': psnr_scores.tolist(),
            'status': 'success',
            'interpretation': self._interpret_score(mean_psnr)
        }
        
        print(f"  PSNR: {mean_psnr:.2f} dB ± {std_psnr:.2f}")
        return result
    
    def _interpret_score(self, score):
        """解释PSNR分数"""
        if score > 40:
            return "信噪比非常高"
        elif score > 30:
            return "信噪比较高"
        elif score > 20:
            return "信噪比一般"
        else:
            return "信噪比较低"