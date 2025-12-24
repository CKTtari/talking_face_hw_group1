"""
人脸检测和视频裁剪模块
基于 FaceTracker 代码进行封装
"""

import os
import cv2
import numpy as np
import pickle
import subprocess
import glob
from scipy import signal
from scipy.interpolate import interp1d
from scipy.io import wavfile
import warnings
warnings.filterwarnings('ignore')

class FaceDetector:
    """人脸检测和视频裁剪器"""
    
    def __init__(self, device='cuda'):
        """
        初始化人脸检测器
        
        Args:
            device: 计算设备
        """
        self.device = device
        self.detector = None
        self._load_detector()
        
    def _load_detector(self):
        """加载人脸检测器"""
        try:
            # 尝试导入 S3FD 检测器
            # 注意：需要先下载 S3FD 模型
            from third_party.syncnet_python.detectors import S3FD
            self.detector = S3FD(device='cuda')
            print("✓ S3FD 人脸检测器加载成功")
        except ImportError as e:
            print(f"⚠ 无法导入 S3FD: {e}")
            print("  将使用 OpenCV 内置人脸检测器")
            self.detector = 'opencv'
    
    def detect_faces_opencv(self, image, scale_factor=1.1, min_neighbors=5, min_size=(100, 100)):
        """
        使用 OpenCV 检测人脸
        
        Args:
            image: 输入图像
            scale_factor: 缩放因子
            min_neighbors: 最小邻居数
            min_size: 最小人脸大小
            
        Returns:
            list: 检测到的人脸边界框 [x1, y1, x2, y2]
        """
        # 加载 OpenCV 人脸检测器
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )
        
        # 转换为 [x1, y1, x2, y2] 格式
        bboxes = []
        for (x, y, w, h) in faces:
            bboxes.append([x, y, x+w, y+h])
        
        return bboxes
    
    def detect_faces_in_video(self, video_path, output_dir, facedet_scale=0.25):
        """
        在视频中检测人脸
        
        Args:
            video_path: 视频路径
            output_dir: 输出目录
            facedet_scale: 人脸检测缩放因子
            
        Returns:
            list: 每帧的人脸检测结果
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 提取视频帧
        frames_dir = os.path.join(output_dir, 'frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        # 使用 ffmpeg 提取帧
        cmd = f"ffmpeg -y -i {video_path} -qscale:v 2 -threads 1 -f image2 {frames_dir}/%06d.jpg"
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 获取帧列表
        flist = sorted(glob.glob(os.path.join(frames_dir, '*.jpg')))
        
        dets = []
        
        for fidx, fname in enumerate(flist):
            # 读取图像
            image = cv2.imread(fname)
            image_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 检测人脸
            if self.detector == 'opencv':
                bboxes = self.detect_faces_opencv(image)
            else:
                # 使用 S3FD
                bboxes = self.detector.detect_faces(
                    image_np, 
                    conf_th=0.9, 
                    scales=[facedet_scale]
                )
            
            # 格式化检测结果
            frame_dets = []
            for bbox in bboxes:
                if isinstance(bbox, np.ndarray):
                    # S3FD 返回 [x1, y1, x2, y2, score]
                    frame_dets.append({
                        'frame': fidx,
                        'bbox': bbox[:-1].tolist() if len(bbox) > 4 else bbox.tolist(),
                        'conf': float(bbox[-1]) if len(bbox) > 4 else 1.0
                    })
                else:
                    # OpenCV 返回 [x1, y1, x2, y2]
                    frame_dets.append({
                        'frame': fidx,
                        'bbox': bbox,
                        'conf': 1.0
                    })
            
            dets.append(frame_dets)
            # print(f'帧 {fidx}: 检测到 {len(frame_dets)} 个人脸')
        
        # 保存检测结果
        dets_path = os.path.join(output_dir, 'faces.pckl')
        with open(dets_path, 'wb') as f:
            pickle.dump(dets, f)
        
        return dets
    
    def track_faces(self, dets, min_track=100, num_failed_det=25, iou_thres=0.5):
        """
        跟踪人脸
        
        Args:
            dets: 人脸检测结果
            min_track: 最小跟踪长度
            num_failed_det: 允许的最大连续失败检测数
            iou_thres: IOU阈值
            
        Returns:
            list: 跟踪结果
        """
        def bb_intersection_over_union(boxA, boxB):
            """计算两个边界框的 IOU"""
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])
            
            interArea = max(0, xB - xA) * max(0, yB - yA)
            boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
            boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
            
            iou = interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0
            return iou
        
        tracks = []
        scenefaces = dets.copy()
        
        while True:
            track = []
            for framefaces in scenefaces:
                for face in framefaces:
                    if track == []:
                        track.append(face)
                        framefaces.remove(face)
                    elif face['frame'] - track[-1]['frame'] <= num_failed_det:
                        iou = bb_intersection_over_union(face['bbox'], track[-1]['bbox'])
                        if iou > iou_thres:
                            track.append(face)
                            framefaces.remove(face)
                            continue
                    else:
                        break
            
            if track == []:
                break
            elif len(track) > min_track:
                framenum = np.array([f['frame'] for f in track])
                bboxes = np.array([np.array(f['bbox']) for f in track])
                
                frame_i = np.arange(framenum[0], framenum[-1] + 1)
                bboxes_i = []
                
                for ij in range(4):
                    interpfn = interp1d(framenum, bboxes[:, ij])
                    bboxes_i.append(interpfn(frame_i))
                
                bboxes_i = np.stack(bboxes_i, axis=1)
                tracks.append({'frame': frame_i, 'bbox': bboxes_i})
        
        return tracks
    
    def crop_face_video(self, video_path, track, output_path, crop_scale=0.4, frame_rate=25):
        """
        裁剪人脸区域视频
        
        Args:
            video_path: 输入视频路径
            track: 人脸跟踪结果
            output_path: 输出视频路径
            crop_scale: 裁剪缩放因子
            frame_rate: 帧率
            
        Returns:
            dict: 裁剪处理结果
        """
        # 创建临时目录
        import tempfile
        tmp_dir = tempfile.mkdtemp(prefix='face_crop_')
        frames_dir = os.path.join(tmp_dir, 'frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        # 提取视频帧
        cmd = f"ffmpeg -y -i {video_path} -qscale:v 2 -threads 1 -f image2 {frames_dir}/%06d.jpg"
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        flist = sorted(glob.glob(os.path.join(frames_dir, '*.jpg')))
        
        # 计算平滑的边界框
        dets = {'x': [], 'y': [], 's': []}
        
        for det in track['bbox']:
            dets['s'].append(max((det[3] - det[1]), (det[2] - det[0])) / 2)
            dets['y'].append((det[1] + det[3]) / 2)
            dets['x'].append((det[0] + det[2]) / 2)
        
        # 中值滤波平滑
        dets['s'] = signal.medfilt(dets['s'], kernel_size=13)
        dets['x'] = signal.medfilt(dets['x'], kernel_size=13)
        dets['y'] = signal.medfilt(dets['y'], kernel_size=13)
        
        # 创建输出视频
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        temp_video = os.path.join(tmp_dir, 'temp.avi')
        vout = cv2.VideoWriter(temp_video, fourcc, frame_rate, (224, 224))
        
        # 逐帧裁剪
        for fidx, frame_idx in enumerate(track['frame']):
            if frame_idx >= len(flist):
                break
                
            image = cv2.imread(flist[frame_idx])
            
            cs = crop_scale
            bs = dets['s'][fidx]
            bsi = int(bs * (1 + 2 * cs))
            
            # 填充图像
            padded = np.pad(image, ((bsi, bsi), (bsi, bsi), (0, 0)), 
                          'constant', constant_values=(110, 110))
            
            my = dets['y'][fidx] + bsi  # 边界框中心 Y
            mx = dets['x'][fidx] + bsi  # 边界框中心 X
            
            # 裁剪人脸区域
            face = padded[int(my - bs):int(my + bs * (1 + 2 * cs)),
                         int(mx - bs * (1 + cs)):int(mx + bs * (1 + cs))]
            
            # 调整大小并写入视频
            vout.write(cv2.resize(face, (224, 224)))
        
        vout.release()
        
        # 提取音频
        audio_path = os.path.join(tmp_dir, 'audio.wav')
        audiostart = track['frame'][0] / frame_rate
        audioend = (track['frame'][-1] + 1) / frame_rate
        
        cmd = (f"ffmpeg -y -i {video_path} -ss {audiostart:.3f} -to {audioend:.3f} "
               f"-ac 1 -vn -acodec pcm_s16le -ar 16000 {audio_path}")
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 合并音频和视频
        cmd = f"ffmpeg -y -i {temp_video} -i {audio_path} -c:v copy -c:a copy {output_path}"
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 清理临时文件
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
        
        print(f"✓ 人脸裁剪视频已保存: {output_path}")
        
        return {
            'track': track,
            'processed_track': dets,
            'output_path': output_path
        }
    
    def process_video_for_sync(self, video_path, output_dir=None, 
                              min_face_size=100, crop_scale=0.4):
        """
        处理视频用于唇语同步（检测并裁剪人脸）
        
        Args:
            video_path: 输入视频路径
            output_dir: 输出目录
            min_face_size: 最小人脸大小
            crop_scale: 裁剪缩放因子
            
        Returns:
            str: 裁剪后的人脸视频路径
        """
        if output_dir is None:
            import tempfile
            output_dir = tempfile.mkdtemp(prefix='sync_processed_')
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 检测人脸
        print("检测视频中的人脸...")
        dets = self.detect_faces_in_video(
            video_path, 
            os.path.join(output_dir, 'detections'),
            facedet_scale=0.25
        )
        
        # 2. 跟踪人脸
        print("跟踪人脸...")
        tracks = self.track_faces(dets, min_track=100)
        
        if not tracks:
            print("⚠ 未检测到足够长度的人脸轨迹")
            return video_path  # 返回原视频
        
        # 3. 选择最长的轨迹
        longest_track = max(tracks, key=lambda x: len(x['frame']))
        
        # 4. 裁剪人脸视频
        output_video = os.path.join(output_dir, 'cropped_face.avi')
        print(f"裁剪人脸视频: {output_video}")
        
        result = self.crop_face_video(
            video_path,
            longest_track,
            output_video,
            crop_scale=crop_scale
        )
        
        return output_video