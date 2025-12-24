# 视频和音频处理模块
import os
import subprocess
import tempfile
import ffmpeg
import uuid

class VideoAudioProcessor:
    def __init__(self):
        pass
    
    def adjust_audio_pitch(self, input_file, output_file, pitch_shift):
        """
        调整音频升降调
        :param input_file: 输入音频文件路径
        :param output_file: 输出音频文件路径
        :param pitch_shift: 音高偏移量（半音），正值升调，负值降调
        :return: 成功返回True，失败返回False
        """
        try:
            # 使用ffmpeg调整音频升降调
            (ffmpeg
             .input(input_file)
             .filter('asetrate', f'44100*{2**(float(pitch_shift)/12)}')
             .filter('atempo', f'1/{2**(float(pitch_shift)/12)}')
             .output(output_file, acodec='libmp3lame')
             .overwrite_output()
             .run(capture_stdout=True, capture_stderr=True)
             )
            return True
        except ffmpeg.Error as e:
            print(f"调整音频升降调失败: {e.stderr.decode()}")
            return False
    
    def adjust_video_speed(self, input_file, output_file, speed_factor):
        """
        调整视频加速减速
        :param input_file: 输入视频文件路径
        :param output_file: 输出视频文件路径
        :param speed_factor: 速度因子，0.5表示减速到一半，2.0表示加速到两倍
        :return: 成功返回True，失败返回False
        """
        try:
            # 获取输入视频的帧率
            probe = ffmpeg.probe(input_file)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            fps = float(video_stream['avg_frame_rate'].split('/')[0]) / float(video_stream['avg_frame_rate'].split('/')[1])
            
            # 使用ffmpeg调整视频速度
            if float(speed_factor) == 1.0:
                # 速度不变，直接复制文件
                import shutil
                shutil.copy2(input_file, output_file)
                return True
            else:
                (ffmpeg
                 .input(input_file)
                 .filter('setpts', f'{1/float(speed_factor)}*PTS')
                 .output(output_file, vcodec='libx264', crf=18, preset='fast')
                 .overwrite_output()
                 .run(capture_stdout=True, capture_stderr=True)
                 )
                return True
        except ffmpeg.Error as e:
            print(f"调整视频速度失败: {e.stderr.decode()}")
            return False
    
    def adjust_video_audio(self, input_video_file, output_video_file, pitch_shift, speed_factor):
        """
        同时调整视频速度和音频升降调
        :param input_video_file: 输入视频文件路径
        :param output_video_file: 输出视频文件路径
        :param pitch_shift: 音高偏移量（半音）
        :param speed_factor: 速度因子
        :return: 成功返回True，失败返回False
        """
        print(f"\n🔊 开始视频音频后处理:")
        print(f"   输入视频: {input_video_file}")
        print(f"   输出视频: {output_video_file}")
        print(f"   音高调整: {pitch_shift} 半音")
        print(f"   速度调整: {speed_factor}x")
        
        try:
            # 使用后端的temp目录而不是系统临时目录
            backend_temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
            os.makedirs(backend_temp_dir, exist_ok=True)
            
            # 创建唯一的临时目录名称
            temp_dir_name = f"temp_{uuid.uuid4().hex}"
            temp_dir = os.path.join(backend_temp_dir, temp_dir_name)
            os.makedirs(temp_dir, exist_ok=True)
            
            print(f"   创建临时目录: {temp_dir}")
            
            # 分离音频
            temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
            print(f"   分离音频到: {temp_audio}")
            
            # 确保输入文件存在
            if not os.path.exists(input_video_file):
                print(f"❌ 输入视频文件不存在: {input_video_file}")
                return False
            
            try:
                (ffmpeg
                 .input(input_video_file)
                 .output(temp_audio, acodec='libmp3lame')
                 .overwrite_output()
                 .run(capture_stdout=True, capture_stderr=True)
                 )
                print(f"✅ 音频分离完成")
            except Exception as e:
                print(f"❌ 分离音频失败: {e}")
                return False
            
            # 调整音频升降调
            temp_audio_pitch = os.path.join(temp_dir, "temp_audio_pitch.mp3")
            print(f"   调整音频升降调到: {temp_audio_pitch}")
            if not self.adjust_audio_pitch(temp_audio, temp_audio_pitch, pitch_shift):
                return False
            print(f"✅ 音频升降调完成")
            
            # 调整视频速度
            temp_video_speed = os.path.join(temp_dir, "temp_video_speed.mp4")
            print(f"   调整视频速度到: {temp_video_speed}")
            if not self.adjust_video_speed(input_video_file, temp_video_speed, speed_factor):
                return False
            print(f"✅ 视频速度调整完成")
            
            # 重新合并视频和音频
            print(f"   合并视频和音频到: {output_video_file}")
            try:
                (ffmpeg
                 .input(temp_video_speed)
                 .input(temp_audio_pitch)
                 .output(output_video_file, vcodec='libx264', acodec='libmp3lame', crf=18, preset='fast')
                 .overwrite_output()
                 .run(capture_stdout=True, capture_stderr=True)
                 )
                
                # 确保输出文件存在
                if not os.path.exists(output_video_file):
                    print(f"❌ 输出视频文件不存在: {output_video_file}")
                    return False
                
                print(f"✅ 视频音频合并完成")
                return True
            except Exception as e:
                print(f"❌ 合并视频音频失败: {e}")
                return False
            finally:
                # 清理临时目录
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                    print(f"✅ 临时目录已清理: {temp_dir}")
                except Exception as e:
                    print(f"⚠️  清理临时目录失败: {e}")
        except Exception as e:
            print(f"❌ 处理视频和音频失败: {str(e)}")
            return False

# 创建处理器实例
processor = VideoAudioProcessor()