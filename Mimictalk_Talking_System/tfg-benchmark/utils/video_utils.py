"""
视频处理工具
"""

import cv2
import numpy as np
from PIL import Image

class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, target_size=(512, 512)):
        """
        初始化视频处理器
        
        Args:
            target_size: 目标分辨率 (width, height)
        """
        self.target_size = target_size
    
    def resize_frame(self, frame):
        """
        调整帧大小到目标分辨率
        
        Args:
            frame: 输入帧
            
        Returns:
            numpy array: 调整大小后的帧
        """
        if frame is None:
            return None
        return cv2.resize(frame, self.target_size)
    
    def extract_frames_same_timestamps(self, video1_path, video2_path, num_frames=30):
        """
        从两个视频中提取相同时间戳的帧
        
        Args:
            video1_path: 第一个视频路径
            video2_path: 第二个视频路径
            num_frames: 提取帧数
            
        Returns:
            tuple: (video1_frames, video2_frames, timestamps)
        """
        # 获取两个视频的信息
        info1 = self.get_video_info(video1_path)
        info2 = self.get_video_info(video2_path)
        
        if info1 is None or info2 is None:
            return [], [], []
        
        # 以时长较短的视频为基准
        duration1 = info1['duration']
        duration2 = info2['duration']
        min_duration = min(duration1, duration2)
        
        if min_duration == 0:
            return [], [], []
        
        # 计算采样时间点
        timestamps = np.linspace(0, min_duration, num_frames, endpoint=False)
        
        # 提取两个视频的帧
        frames1 = self._extract_frames_at_timestamps(video1_path, timestamps, info1['fps'])
        frames2 = self._extract_frames_at_timestamps(video2_path, timestamps, info2['fps'])
        
        return frames1, frames2, timestamps
    
    def extract_frames(self, video_path, num_frames=30, start_frame=0, 
                      use_timestamps=None, reference_fps=None):
        """
        从视频中提取帧
        
        Args:
            video_path: 视频路径
            num_frames: 提取帧数
            start_frame: 起始帧
            use_timestamps: 使用指定的时间戳列表（秒）
            reference_fps: 参考帧率（如果已知）
            
        Returns:
            list: 帧列表
            int: 实际提取的帧数
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return [], 0
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps == 0 or total_frames == 0:
            cap.release()
            return [], 0
        
        frames = []
        
        if use_timestamps is not None:
            # 使用指定的时间戳
            for timestamp in use_timestamps:
                frame_idx = int(timestamp * fps)
                frame_idx = min(frame_idx, total_frames - 1)
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frame = self.resize_frame(frame)
                    frames.append(frame)
        else:
            # 均匀采样
            if num_frames >= total_frames:
                frame_indices = list(range(total_frames))
            else:
                frame_indices = np.linspace(start_frame, total_frames-1, 
                                           num_frames, dtype=int)
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame = self.resize_frame(frame)
                    frames.append(frame)
        
        cap.release()
        return frames, len(frames)
    
    def _extract_frames_at_timestamps(self, video_path, timestamps, fps):
        """
        在指定时间戳提取帧
        
        Args:
            video_path: 视频路径
            timestamps: 时间戳列表（秒）
            fps: 视频帧率
            
        Returns:
            list: 帧列表
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames = []
        for timestamp in timestamps:
            frame_idx = int(timestamp * fps)
            frame_idx = min(frame_idx, total_frames - 1)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frame = self.resize_frame(frame)
                frames.append(frame)
            else:
                frames.append(None)  # 标记缺失的帧
        
        cap.release()
        return frames
    
    def extract_matched_frames(self, real_video_path, generated_video_path, num_frames=30):
        """
        提取匹配的帧（确保相同时间点）
        
        Args:
            real_video_path: 真实视频路径
            generated_video_path: 生成视频路径
            num_frames: 采样帧数
            
        Returns:
            tuple: (real_frames, generated_frames, matched_indices)
        """
        # 获取视频信息
        real_info = self.get_video_info(real_video_path)
        gen_info = self.get_video_info(generated_video_path)
        
        if real_info is None or gen_info is None:
            return [], [], []
        
        # 以时长较短的视频为基准
        real_duration = real_info['duration']
        gen_duration = gen_info['duration']
        min_duration = min(real_duration, gen_duration)
        
        if min_duration == 0:
            return [], [], []
        
        # 计算采样时间点
        timestamps = np.linspace(0, min_duration, num_frames, endpoint=False)
        
        # 提取两个视频的帧
        real_frames = self._extract_frames_at_timestamps(real_video_path, timestamps, real_info['fps'])
        gen_frames = self._extract_frames_at_timestamps(generated_video_path, timestamps, gen_info['fps'])
        
        # 只保留两个视频都成功提取的帧
        matched_real_frames = []
        matched_gen_frames = []
        matched_indices = []
        
        for i, (real_frame, gen_frame) in enumerate(zip(real_frames, gen_frames)):
            if real_frame is not None and gen_frame is not None:
                matched_real_frames.append(real_frame)
                matched_gen_frames.append(gen_frame)
                matched_indices.append(i)
        
        return matched_real_frames, matched_gen_frames, matched_indices
    
    def extract_center_frame(self, video_path, frame_time=0.5):
        """
        提取视频中心帧（用于身份识别）
        
        Args:
            video_path: 视频路径
            frame_time: 时间点（秒）
            
        Returns:
            numpy array: 中心帧
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps == 0 or total_frames == 0:
            cap.release()
            return None
        
        # 计算帧索引
        frame_idx = int(frame_time * fps)
        frame_idx = min(frame_idx, total_frames - 1)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return self.resize_frame(frame)
        return None
    
    def get_video_info(self, video_path):
        """
        获取视频信息
        
        Args:
            video_path: 视频路径
            
        Returns:
            dict: 视频信息
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        info = {
            'fps': float(cap.get(cv2.CAP_PROP_FPS)),
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': 0
        }
        
        if info['fps'] > 0:
            info['duration'] = info['total_frames'] / info['fps']
        
        cap.release()
        return info
    
    def save_frame_as_image(self, frame, output_path):
        """
        保存帧为图像
        
        Args:
            frame: 帧数据
            output_path: 输出路径
        """
        if frame is not None:
            cv2.imwrite(output_path, frame)
    
    def frames_to_tensor(self, frames, normalize=True):
        """
        将帧列表转换为张量
        
        Args:
            frames: 帧列表
            normalize: 是否归一化到 [0, 1]
            
        Returns:
            torch.Tensor: 形状为 [N, C, H, W] 的张量
        """
        import torch
        
        tensor_frames = []
        for frame in frames:
            if frame is None:
                # 创建黑色帧作为占位符
                frame = np.zeros((self.target_size[1], self.target_size[0], 3), dtype=np.uint8)
            
            # BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # HWC to CHW
            frame_chw = np.transpose(frame_rgb, (2, 0, 1))
            tensor_frames.append(frame_chw)
        
        if len(tensor_frames) == 0:
            return torch.FloatTensor()
        
        tensor = torch.FloatTensor(np.array(tensor_frames))
        
        if normalize:
            tensor = tensor / 255.0
        
        return tensor