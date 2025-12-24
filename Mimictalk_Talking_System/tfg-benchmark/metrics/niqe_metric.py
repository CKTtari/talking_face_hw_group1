"""
NIQE指标
使用pyiqa计算Natural Image Quality Evaluator
"""

import numpy as np
import torch

class NIQEMetric:
    """NIQE指标"""
    
    def __init__(self, device='cuda'):
        """
        初始化NIQE指标
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.metric = None
        self._load_metric()
    
    def _load_metric(self):
        """加载NIQE指标"""
        try:
            import pyiqa
            self.metric = pyiqa.create_metric('niqe', device=self.device)
            print("✓ NIQE 指标加载成功")
        except ImportError:
            print("⚠ pyiqa 未安装，NIQE指标不可用")
            self.metric = None
    
    def calculate(self, generated_video, video_processor, num_frames=30):
        """
        计算NIQE（无需参考视频）
        
        Args:
            generated_video: 生成视频路径
            video_processor: 视频处理器实例
            num_frames: 采样帧数
            
        Returns:
            dict: 计算结果
        """
        if self.metric is None:
            return {
                'name': 'NIQE',
                'value': 100.0,
                'scores': [],
                'status': 'error',
                'message': 'pyiqa未安装，NIQE指标不可用'
            }
        
        print("计算NIQE...")
        
        # 从生成视频提取帧
        gen_frames, num_gen = video_processor.extract_frames(generated_video, num_frames)
        
        if num_gen == 0:
            return {
                'name': 'NIQE',
                'value': 100.0,
                'scores': [],
                'status': 'error',
                'message': '无法从视频提取足够的帧'
            }
        
        # 逐帧计算NIQE
        niqe_scores = []
        for frame in gen_frames:
            # 转换为张量
            frame_tensor = video_processor.frames_to_tensor([frame])[0].unsqueeze(0)
            
            # 计算NIQE
            with torch.no_grad():
                score = self.metric(frame_tensor)
                if isinstance(score, torch.Tensor):
                    score = score.item()
                niqe_scores.append(score)
        
        # 计算统计量
        niqe_scores = np.array(niqe_scores)
        mean_niqe = float(np.mean(niqe_scores))
        std_niqe = float(np.std(niqe_scores))
        
        result = {
            'name': 'NIQE',
            'value': mean_niqe,
            'mean': mean_niqe,
            'std': std_niqe,
            'min': float(np.min(niqe_scores)),
            'max': float(np.max(niqe_scores)),
            'num_frames': len(niqe_scores),
            'scores': niqe_scores.tolist(),
            'status': 'success',
            'interpretation': self._interpret_score(mean_niqe)
        }
        
        print(f"  NIQE: {mean_niqe:.4f} ± {std_niqe:.4f}")
        return result
    
    def _interpret_score(self, score):
        """解释NIQE分数（越低越好）"""
        if score < 3:
            return "自然度非常高"
        elif score < 5:
            return "自然度较高"
        elif score < 8:
            return "自然度一般"
        else:
            return "自然度较低"