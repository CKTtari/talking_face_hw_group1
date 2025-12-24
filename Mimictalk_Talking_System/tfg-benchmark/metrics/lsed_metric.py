"""
LSE-D 指标 (使用 SyncNet)
Lip Sync Error - Distance
唇语同步距离误差
"""

import numpy as np
import os
from syncnet_wrapper import SyncNetWrapper

class LSEDMetric:
    """LSE-D 指标 (使用 SyncNet)"""
    
    def __init__(self, device='cuda', model_path="models/syncnet.pth", enable_face_crop=True):
        """
        初始化 LSE-D 指标
        
        Args:
            device: 计算设备
            model_path: SyncNet 模型路径
        """
        self.device = device
        self.model_path = model_path
        self.enable_face_crop = enable_face_crop
        self.syncnet = None
        self._load_syncnet()
    
    def _load_syncnet(self):
        """加载 SyncNet 模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                print(f"⚠ SyncNet 模型文件不存在: {self.model_path}")
                print(f"  请将 syncnet.pth 放在 {self.model_path}")
                self.syncnet = None
                return
            
            # 初始化 SyncNet 包装器
            from syncnet_wrapper import SyncNetWrapper
            self.syncnet = SyncNetWrapper(
                model_path=self.model_path,
                device=self.device,
                enable_face_crop=self.enable_face_crop
            )
            
            if self.syncnet.model is not None:
                print("✓ LSE-C 指标初始化完成 (使用 SyncNet)")
                if self.enable_face_crop:
                    print("  ✓ 启用人脸裁剪预处理")
            else:
                print("⚠ LSE-C: SyncNet 模型加载失败")
                self.syncnet = None
                
        except Exception as e:
            print(f"⚠ LSE-C 初始化失败: {e}")
            self.syncnet = None
    
    def calculate(self, audio_path, generated_video, video_processor, 
                 audio_extractor, num_frames=30):
        """
        计算 LSE-D
        
        Args:
            audio_path: 音频路径
            generated_video: 生成视频路径
            video_processor: 视频处理器实例
            audio_extractor: 音频提取器实例
            num_frames: 采样帧数
            
        Returns:
            dict: 计算结果
        """
        print("计算 LSE-D (使用 SyncNet)...")
        
        # 检查 SyncNet 是否可用
        if self.syncnet is None or self.syncnet.model is None:
            return {
                'name': 'LSE-D',
                'value': 1.0,
                'status': 'error',
                'message': 'SyncNet 模型未加载或不可用'
            }
        
        # 检查音频文件是否存在
        if audio_path is None or not os.path.exists(audio_path):
            print("  警告: 音频文件不存在，尝试从视频提取...")
            # 从视频提取音频
            output_dir = os.path.join("temp_audio", os.path.basename(generated_video))
            os.makedirs(output_dir, exist_ok=True)
            audio_path = audio_extractor.extract_audio(generated_video, output_dir)
            
            if audio_path is None or not os.path.exists(audio_path):
                return {
                    'name': 'LSE-D',
                    'value': 1.0,
                    'status': 'error',
                    'message': '无法获取音频文件'
                }
        
        # 检查视频文件是否存在
        if not os.path.exists(generated_video):
            return {
                'name': 'LSE-D',
                'value': 1.0,
                'status': 'error',
                'message': f'视频文件不存在: {generated_video}'
            }
        
        try:
            # 使用 SyncNet 计算 LSE
            result = self.syncnet.compute_lse(audio_path, generated_video)
            
            if result['status'] == 'success':
                lsed_score = result['lsed']
                
                final_result = {
                    'name': 'LSE-D',
                    'value': float(lsed_score),
                    'offset': result.get('offset', 0.0),
                    'confidence': result.get('confidence', 0.0),
                    'lsec': result.get('lsec', 0.0),  # 也记录 LSE-C 值
                    'status': 'success',
                    'dist': result.get('dist', None),
                    'interpretation': self._interpret_score(lsed_score),
                    'message': result.get('message', '计算成功')
                }
                
                print(f"  LSE-D: {lsed_score:.4f}")
                if 'offset' in result:
                    print(f"  音频视频偏移: {result['offset']:.1f} 帧")
                if 'confidence' in result:
                    print(f"  同步置信度: {result['confidence']:.4f}")
                
                return final_result
            else:
                return {
                    'name': 'LSE-D',
                    'value': 1.0,
                    'status': 'error',
                    'message': result.get('message', 'SyncNet 计算失败')
                }
                
        except Exception as e:
            print(f"  LSE-D 计算异常: {e}")
            return {
                'name': 'LSE-D',
                'value': 1.0,
                'status': 'error',
                'message': f'计算异常: {str(e)}'
            }
    
    def _interpret_score(self, score):
        """解释 LSE-D 分数（越低越好）"""
        if score < 0.2:
            return "唇语距离非常小"
        elif score < 0.4:
            return "唇语距离较小"
        elif score < 0.6:
            return "唇语距离一般"
        else:
            return "唇语距离较大"
    
    def compute_frame_distances(self, audio_path, video_path):
        """
        计算帧级距离（用于详细分析）
        
        Args:
            audio_path: 音频路径
            video_path: 视频路径
            
        Returns:
            numpy array: 帧级距离
        """
        if self.syncnet is None:
            return None
        
        # 这里可以扩展为计算帧级距离
        # 目前通过 compute_lse 返回总体结果
        result = self.syncnet.compute_lse(audio_path, video_path)
        
        if result['status'] == 'success' and 'dists' in result:
            return result['dists']
        
        return None