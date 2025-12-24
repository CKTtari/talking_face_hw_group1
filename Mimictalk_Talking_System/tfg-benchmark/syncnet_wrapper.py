"""
SyncNet 包装器（集成人脸裁剪）
封装 SyncNetInstance 用于 LSE 计算，自动进行人脸裁剪
"""

import os
import torch
import numpy as np
import cv2
from scipy.io import wavfile
import python_speech_features
from pathlib import Path
from face_detector import FaceDetector

class SyncNetWrapper:
    """SyncNet 包装器（集成人脸裁剪）"""
    
    def __init__(self, model_path="models/syncnet.pth", device='cuda', 
                 enable_face_crop=True):
        """
        初始化 SyncNet 包装器
        
        Args:
            model_path: SyncNet 模型路径
            device: 计算设备
            enable_face_crop: 是否启用人脸裁剪
        """
        self.device = device
        self.model_path = model_path
        self.enable_face_crop = enable_face_crop
        self.model = None
        self.face_detector = None
        
        self._load_components()
        
    def _load_components(self):
        """加载所有组件"""
        # 加载人脸检测器
        if self.enable_face_crop:
            try:
                self.face_detector = FaceDetector(device=self.device)
                print("✓ 人脸检测器加载成功")
            except Exception as e:
                print(f"⚠ 人脸检测器加载失败: {e}")
                self.face_detector = None
        
        # 加载 SyncNet 模型
        self._load_syncnet_model()
    
    def _load_syncnet_model(self):
        """加载 SyncNet 模型"""
        try:
            # 导入 SyncNet 类
            import sys
            sys.path.append(os.path.dirname(__file__) + "/third_party/syncnet_python")
            
            # 创建 SyncNetInstance
            from third_party.syncnet_python.SyncNetInstance import SyncNetInstance
            self.model = SyncNetInstance()
            
            # 加载模型权重
            if os.path.exists(self.model_path):
                self.model.loadParameters(self.model_path)
                print(f"✓ SyncNet 模型加载成功: {self.model_path}")
            else:
                print(f"⚠ SyncNet 模型文件不存在: {self.model_path}")
                print(f"  请将 syncnet.pth 放在: {self.model_path}")
                self.model = None
                
        except ImportError as e:
            print(f"⚠ 导入 SyncNet 失败: {e}")
            print("请确保 syncnet_instance.py 和 SyncNetModel.py 在 Python 路径中")
            self.model = None
        except Exception as e:
            print(f"⚠ SyncNet 加载失败: {e}")
            self.model = None
    
    def preprocess_video(self, video_path, output_dir=None):
        """
        预处理视频：裁剪人脸区域
        
        Args:
            video_path: 原始视频路径
            output_dir: 输出目录
            
        Returns:
            str: 预处理后的视频路径
        """
        if not self.enable_face_crop or self.face_detector is None:
            print("⚠ 人脸裁剪未启用，使用原始视频")
            return video_path
        
        try:
            print(f"预处理视频: {video_path}")
            print("  1. 检测人脸...")
            print("  2. 跟踪人脸轨迹...")
            print("  3. 裁剪人脸区域...")
            
            processed_video = self.face_detector.process_video_for_sync(
                video_path,
                output_dir=output_dir
            )
            
            print(f"✓ 视频预处理完成: {processed_video}")
            return processed_video
            
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print(err)
            print(f"⚠ 视频预处理失败: {e}")
            print("  使用原始视频进行同步计算")
            return video_path
    
    def extract_audio_features(self, audio_path):
        """
        提取音频特征
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            numpy array: 音频特征 [T, D]
        """
        try:
            sample_rate, audio = wavfile.read(audio_path)
            
            # 提取 MFCC 特征
            mfcc = python_speech_features.mfcc(audio, sample_rate, 
                                              winlen=0.025,   # 25ms 窗口
                                              winstep=0.01,   # 10ms 步长
                                              numcep=13,      # 13个MFCC系数
                                              nfilt=26,       # 26个滤波器
                                              nfft=512,       # FFT点数
                                              preemph=0.97,   # 预加重
                                              ceplifter=22,   # Cepstral lifter
                                              appendEnergy=True)  # 添加能量
            
            # 转置为 [T, D] 格式
            mfcc = mfcc.T  # [D, T] -> [T, D]
            
            return mfcc
            
        except Exception as e:
            print(f"音频特征提取失败: {e}")
            return None
    
    def extract_video_features(self, video_path):
        """
        提取视频特征
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            numpy array: 视频特征 [T, D]
        """
        if self.model is None:
            return None
        
        try:
            # 预处理视频（裁剪人脸）
            processed_video = self.preprocess_video(video_path)
            
            # 创建临时目录
            import tempfile
            tmp_dir = tempfile.mkdtemp(prefix="syncnet_")
            
            # 创建命令行参数对象
            class Args:
                def __init__(self):
                    self.tmp_dir = tmp_dir
                    self.reference = "video"
                    self.batch_size = 20
                    self.vshift = 10
            
            args = Args()
            
            # 提取视频特征
            video_feat = self.model.extract_feature(args, processed_video)
            
            # 清理临时目录
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
            # 如果使用了预处理视频，清理临时文件
            if processed_video != video_path and os.path.exists(processed_video):
                try:
                    os.remove(processed_video)
                    # 清理可能存在的临时目录
                    shutil.rmtree(os.path.dirname(processed_video), ignore_errors=True)
                except:
                    pass
            
            return video_feat.numpy() if video_feat is not None else None
            
        except Exception as e:
            print(f"视频特征提取失败: {e}")
            return None
    
    def compute_lse(self, audio_path, video_path):
        """
        计算 LSE-C 和 LSE-D
        
        Args:
            audio_path: 音频文件路径
            video_path: 视频文件路径
            
        Returns:
            dict: 包含 LSE-C 和 LSE-D 的结果
        """
        if self.model is None:
            return {
                'lsec': 0.0,
                'lsed': 0.0,
                'status': 'error',
                'message': 'SyncNet 模型未加载'
            }
        
        try:
            # 预处理视频（裁剪人脸）
            processed_video = self.preprocess_video(video_path)
            
            # 创建临时目录
            import tempfile
            tmp_dir = tempfile.mkdtemp(prefix="syncnet_")
            
            # 创建命令行参数对象
            class Args:
                def __init__(self):
                    self.tmp_dir = tmp_dir
                    self.reference = "video"
                    self.batch_size = 20
                    self.vshift = 10
            
            args = Args()
            
            # 计算偏移和距离
            print("使用 SyncNet 计算唇语同步...")
            offset, confidence, dists = self.model.evaluate(args, processed_video)
            
            # 清理临时目录
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
            # 如果使用了预处理视频，清理临时文件
            if processed_video != video_path and os.path.exists(processed_video):
                try:
                    os.remove(processed_video)
                    # 清理可能存在的临时目录
                    shutil.rmtree(os.path.dirname(processed_video), ignore_errors=True)
                except:
                    pass
            
            # 计算 LSE-C 和 LSE-D
            if confidence is None or dists is None:
                return {
                    'lsec': 0.0,
                    'lsed': 0.0,
                    'status': 'error',
                    'message': '无法计算同步指标'
                }
            
            # 计算 LSE-C: 1 - confidence (置信度越高，LSE-C 越低)
            # confidence 越大表示同步越好，所以 LSE-C = 1 - normalized_confidence
            normalized_confidence = min(1.0, max(0.0, np.log10(confidence)))  # 假设 confidence 范围 0-10
            lsec_score = 1.0 - normalized_confidence
            
            # 计算 LSE-D: 平均最小距离 (归一化)
            # dists 形状: [T, 2*vshift+1]
            if len(dists.shape) == 2 and dists.shape[0] > 0:
                # 计算每个时间步的最小距离
                min_dists = np.min(dists, axis=1)
                # 归一化到 0-1 范围
                max_dist = np.max(min_dists) if len(min_dists) > 0 else 1.0
                normalized_dists = min_dists / max_dist if max_dist > 0 else min_dists
                lsed_score = float(np.mean(normalized_dists))
            else:
                lsed_score = 0.0
            
            result = {
                'lsec': float(lsec_score),
                'lsed': float(lsed_score),
                'offset': float(offset),
                'confidence': float(confidence),
                'dist': np.mean(dists),
                'status': 'success',
                'message': '计算成功'
            }
            
            # 打印结果
            print(f"  LSE-C: {lsec_score:.4f}")
            print(f"  LSE-D: {lsed_score:.4f}")
            print(f"  音频视频偏移: {offset:.1f} 帧")
            print(f"  同步置信度: {confidence:.4f}")
            print(f"  平均距离: {np.mean(dists):.4f}")
            
            return result
            
        except Exception as e:
            print(f"LSE 计算失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'lsec': 0.0,
                'lsed': 0.0,
                'status': 'error',
                'message': str(e)
            }
    
    def compute_frame_level_sync(self, audio_path, video_path):
        """
        计算帧级同步分数
        
        Args:
            audio_path: 音频文件路径
            video_path: 视频文件路径
            
        Returns:
            numpy array: 帧级同步分数
        """
        result = self.compute_lse(audio_path, video_path)
        
        if result['status'] != 'success':
            return None
        
        # 这里可以扩展为返回帧级分数
        # 目前只返回总体分数
        return np.array([result['lsec'], result['lsed']])
    
    def batch_process(self, audio_video_pairs, output_dir=None):
        """
        批量处理多个音频视频对
        
        Args:
            audio_video_pairs: 音频视频对列表 [(audio_path, video_path), ...]
            output_dir: 输出目录
            
        Returns:
            list: 每个视频对的 LSE 结果
        """
        results = []
        
        for i, (audio_path, video_path) in enumerate(audio_video_pairs):
            print(f"\n处理第 {i+1}/{len(audio_video_pairs)} 个视频对")
            print(f"  音频: {os.path.basename(audio_path)}")
            print(f"  视频: {os.path.basename(video_path)}")
            
            result = self.compute_lse(audio_path, video_path)
            result['audio'] = audio_path
            result['video'] = video_path
            results.append(result)
        
        # 保存批量结果
        if output_dir:
            import json
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'batch_lse_results.json')
            
            # 转换为可序列化的格式
            def convert(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, (np.float32, np.float64)):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {k: convert(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert(item) for item in obj]
                else:
                    return obj
            
            serializable_results = [convert(r) for r in results]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n批量结果已保存: {output_file}")
        
        return results