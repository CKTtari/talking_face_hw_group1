"""
文件处理工具
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
import glob

class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_dir(directory):
        """确保目录存在"""
        os.makedirs(directory, exist_ok=True)
        return directory
    
    @staticmethod
    def get_video_basename(video_path):
        """获取视频文件的基础名称（不含扩展名）"""
        return os.path.splitext(os.path.basename(video_path))[0]
    
    @staticmethod
    def save_json(data, file_path, indent=2):
        """
        保存数据到 JSON 文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: 缩进空格数
        """
        def convert(obj):
            if isinstance(obj, (np.ndarray, np.generic)):
                return obj.tolist() if hasattr(obj, 'tolist') else float(obj)
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            else:
                return obj
        
        FileUtils.ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(convert(data), f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def load_json(file_path):
        """从 JSON 文件加载数据"""
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_results_to_csv(results, file_path):
        """
        保存结果到 CSV
        
        Args:
            results: 结果字典
            file_path: 文件路径
        """
        try:
            if 'summary' in results:
                summary = results['summary']
                rows = []
                
                # 添加基本信息
                if 'video_info' in results:
                    info = results['video_info']
                    rows.append(['视频名称', info.get('video_name', '')])
                    rows.append(['参考视频', info.get('reference_video', '')])
                    rows.append(['生成视频', info.get('generated_video', '')])
                    rows.append(['评测时间', info.get('evaluation_time', '')])
                    rows.append(['-' * 20, '-' * 20])
                
                # 添加各个指标
                for metric_name, metric_data in results.items():
                    if metric_name in ['summary', 'video_info']:
                        continue
                    
                    if isinstance(metric_data, dict) and 'value' in metric_data:
                        rows.append([metric_data.get('name', metric_name), 
                                    f"{metric_data['value']:.4f}"])
                
                # 添加综合分数
                if 'overall_score' in summary:
                    rows.append(['-' * 20, '-' * 20])
                    rows.append(['综合分数', f"{summary['overall_score']:.4f}"])
                    rows.append(['评价', summary.get('interpretation', '')])
                
                # 转换为DataFrame并保存
                df = pd.DataFrame(rows, columns=['指标', '值'])
                FileUtils.ensure_dir(os.path.dirname(file_path))
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                return True
            
        except Exception as e:
            print(f"保存 CSV 失败: {e}")
        
        return False
    
    @staticmethod
    def generate_timestamp():
        """生成时间戳字符串"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def find_video_files(directory, extensions=None):
        """
        查找目录中的视频文件
        
        Args:
            directory: 目录路径
            extensions: 视频扩展名列表
            
        Returns:
            list: 视频文件路径列表
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        
        video_files = []
        for ext in extensions:
            video_files.extend(glob.glob(os.path.join(directory, f'*{ext}')))
        
        return sorted(video_files)