"""
音频处理工具
"""

import os
import warnings
warnings.filterwarnings('ignore')

class AudioExtractor:
    """音频提取器"""
    
    def __init__(self):
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查依赖"""
        self.has_moviepy = False
        try:
            from moviepy.video.io.VideoFileClip import VideoFileClip
            self.VideoFileClip = VideoFileClip
            self.has_moviepy = True
        except ImportError:
            print("警告: moviepy 未安装，音频提取功能不可用")
    
    def extract_audio(self, video_path, output_dir="extracted_audio"):
        """
        从视频提取音频
        
        Args:
            video_path: 视频路径
            output_dir: 输出目录
            
        Returns:
            str: 音频文件路径，None表示失败
        """
        if not self.has_moviepy:
            print("错误: moviepy 未安装，无法提取音频")
            return None
        
        from utils.file_utils import FileUtils
        FileUtils.ensure_dir(output_dir)
        
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(output_dir, f"{video_name}_audio.wav")
        
        # 如果已经存在，直接返回
        if os.path.exists(audio_path):
            return audio_path
        
        try:
            clip = self.VideoFileClip(video_path)
            
            if clip.audio is not None:
                # 设置verbose=False避免输出
                clip.audio.write_audiofile(audio_path, logger=None)
                print(f"✓ 音频提取成功: {audio_path}")
            else:
                print("⚠ 视频中没有音频轨道")
                audio_path = None
            
            clip.close()
            return audio_path
            
        except Exception as e:
            print(f"⚠ 音频提取失败: {e}")
            return None
    
    def extract_audio_features(self, audio_path, sr=16000):
        """
        提取音频特征（用于唇语同步）
        
        Args:
            audio_path: 音频路径
            sr: 采样率
            
        Returns:
            dict: 音频特征
        """
        try:
            import librosa
            
            # 加载音频
            audio, _ = librosa.load(audio_path, sr=sr)
            
            # 提取MFCC特征
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            
            # 提取能量
            energy = librosa.feature.rms(y=audio)
            
            features = {
                'audio': audio,
                'mfcc': mfcc,
                'energy': energy,
                'duration': len(audio) / sr
            }
            
            return features
            
        except Exception as e:
            print(f"音频特征提取失败: {e}")
            return None