"""
主评测器
整合所有评测模块，管理评测流程
"""

import os
import time
from datetime import datetime
from utils.file_utils import FileUtils
from utils.video_utils import VideoProcessor
from utils.audio_utils import AudioExtractor
from evaluator_factory import EvaluatorFactory
from metrics_config import AVAILABLE_METRICS, DEFAULT_CONFIG

class MainEvaluator:
    """主评测器"""
    
    def __init__(self, config=None):
        """
        初始化主评测器
        
        Args:
            config: 评测配置，None时使用默认配置
        """
        self.config = config or DEFAULT_CONFIG.copy()
        self._validate_config()
        
        # 初始化工具
        target_size = self.config.get('video_resolution', (512, 512))
        self.video_processor = VideoProcessor(target_size=target_size)
        self.audio_extractor = AudioExtractor()
        
        # 初始化评测器工厂
        self.evaluator_factory = EvaluatorFactory(self.config)
        
        # 评测结果
        self.source_image = None
        self.results = {}
        self.video_info = {}
        
        print(f"\n{'='*60}")
        print("Talking Face Generation 评测系统")
        print(f"设备: {self.config.get('device', 'cuda')}")
        print(f"分辨率: {target_size[0]}x{target_size[1]}")
        print(f"采样帧数: {self.config.get('num_frames', 30)}")
        print(f"{'='*60}\n")
    
    def _validate_config(self):
        """验证配置"""
        # 确保必要的配置项存在
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value
    
    def set_reference_video(self, reference_video_path):
        """
        设置参考视频
        
        Args:
            reference_video_path: 参考视频路径
        """
        if not os.path.exists(reference_video_path):
            raise FileNotFoundError(f"参考视频不存在: {reference_video_path}")
        
        self.reference_video = reference_video_path
        self.video_info['reference_video'] = reference_video_path
        
        # 提取参考视频的中心帧作为身份图像
        print("提取参考视频身份帧...")
        self.source_image = self.video_processor.extract_center_frame(reference_video_path)
        if self.source_image is None:
            print("警告: 无法从参考视频提取身份帧")
        else:
            print("✓ 身份帧提取成功")
        
        # 获取参考视频信息
        ref_info = self.video_processor.get_video_info(reference_video_path)
        if ref_info:
            self.video_info['reference_info'] = ref_info
    
    def set_generated_video(self, generated_video_path):
        """
        设置生成视频
        
        Args:
            generated_video_path: 生成视频路径
        """
        if not os.path.exists(generated_video_path):
            raise FileNotFoundError(f"生成视频不存在: {generated_video_path}")
        
        self.generated_video = generated_video_path
        self.video_info['generated_video'] = generated_video_path
        self.video_info['video_name'] = FileUtils.get_video_basename(generated_video_path)
        
        # 获取生成视频信息
        gen_info = self.video_processor.get_video_info(generated_video_path)
        if gen_info:
            self.video_info['generated_info'] = gen_info
    
    def extract_audio_from_generated(self, output_dir="extracted_audio"):
        """
        从生成视频提取音频
        
        Args:
            output_dir: 音频输出目录
            
        Returns:
            str: 音频文件路径，None表示失败
        """
        print("从生成视频提取音频...")
        audio_path = self.audio_extractor.extract_audio(self.generated_video, output_dir)
        
        if audio_path and os.path.exists(audio_path):
            self.audio_path = audio_path
            print(f"✓ 音频提取成功: {audio_path}")
        else:
            print("⚠ 音频提取失败，相关指标将无法计算")
            self.audio_path = None
        
        return audio_path
    
    def evaluate(self, output_dir=None):
        """
        执行评测
        
        Args:
            output_dir: 输出目录，None时使用配置中的目录
            
        Returns:
            dict: 评测结果
        """
        if output_dir is None:
            output_dir = self.config.get('output_dir', 'evaluation_results')
        
        # 创建输出目录
        FileUtils.ensure_dir(output_dir)
        
        # 检查必要数据
        if not hasattr(self, 'generated_video'):
            raise ValueError("未设置生成视频")
        
        # 提取音频（如果需要）
        needs_audio = any(metric in self.evaluator_factory.get_available_metrics() 
                         for metric in ['lsec', 'lsed'])
        if needs_audio:
            self.extract_audio_from_generated(output_dir)
        
        print(f"\n开始评测: {self.video_info.get('video_name', '未知视频')}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 初始化结果存储
        self.results = {
            'video_info': {
                **self.video_info,
                'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'config': self.config
            },
            'metrics': {}
        }
        
        # 获取所有评测器
        evaluators = self.evaluator_factory.get_all_evaluators()
        num_metrics = len(evaluators)
        
        print(f"\n将要计算 {num_metrics} 个指标:")
        for i, (metric_name, evaluator) in enumerate(evaluators.items(), 1):
            print(f"  {i}. {AVAILABLE_METRICS.get(metric_name, {}).get('name', metric_name)}")
        
        print(f"\n{'='*60}")
        
        # 逐个计算指标
        for metric_name, evaluator in evaluators.items():
            print(f"\n计算指标: {AVAILABLE_METRICS.get(metric_name, {}).get('name', metric_name)}")
            
            try:
                # 检查数据要求
                available_data = {
                    'source_image': getattr(self, 'source_image', None),
                    'real_video': getattr(self, 'reference_video', None),
                    'generated_video': self.generated_video,
                    'audio': getattr(self, 'audio_path', None)
                }
                
                # 根据指标类型调用相应的计算方法
                if metric_name == 'identity':
                    if self.source_image is None:
                        result = {
                            'name': AVAILABLE_METRICS[metric_name]['name'],
                            'value': 0.0,
                            'status': 'error',
                            'message': '无身份图像可用'
                        }
                    else:
                        result = evaluator.calculate(
                            self.source_image, 
                            self.generated_video,
                            self.video_processor,
                            self.config.get('num_frames', 30)
                        )
                
                elif metric_name in ['fid', 'lpips', 'ssim', 'psnr']:
                    if not hasattr(self, 'reference_video'):
                        result = {
                            'name': AVAILABLE_METRICS[metric_name]['name'],
                            'value': 0.0 if metric_name != 'fid' else float('inf'),
                            'status': 'error',
                            'message': '无参考视频可用'
                        }
                    else:
                        result = evaluator.calculate(
                            self.reference_video,
                            self.generated_video,
                            self.video_processor,
                            self.config.get('num_frames', 30)
                        )
                
                elif metric_name == 'niqe':
                    result = evaluator.calculate(
                        self.generated_video,
                        self.video_processor,
                        self.config.get('num_frames', 30)
                    )
                
                elif metric_name in ['lsec', 'lsed']:
                    if self.audio_path is None or not os.path.exists(self.audio_path):
                        result = {
                            'name': AVAILABLE_METRICS[metric_name]['name'],
                            'value': 0.0 if metric_name == 'lsec' else 1.0,
                            'status': 'error',
                            'message': '无音频可用'
                        }
                    else:
                        result = evaluator.calculate(
                            self.audio_path,
                            self.generated_video,
                            self.video_processor,
                            self.audio_extractor,
                            self.config.get('num_frames', 30)
                        )
                
                else:
                    result = {
                        'name': metric_name,
                        'value': 0.0,
                        'status': 'error',
                        'message': f'未知指标类型: {metric_name}'
                    }
                
                # 存储结果
                self.results['metrics'][metric_name] = result
                
                if result.get('status') == 'success':
                    print(f"  ✓ 完成")
                else:
                    print(f"  ✗ 失败: {result.get('message', '未知错误')}")
                
            except Exception as e:
                print(f"  ✗ 异常: {e}")
                self.results['metrics'][metric_name] = {
                    'name': AVAILABLE_METRICS.get(metric_name, {}).get('name', metric_name),
                    'value': 0.0,
                    'status': 'error',
                    'message': str(e)
                }
        
        # 计算综合分数
        self._calculate_summary()
        
        # 保存结果
        self._save_results(output_dir)
        
        # 打印总结
        self._print_summary()
        
        print(f"\n{'='*60}")
        print("评测完成！")
        print(f"结果保存在: {output_dir}")
        print(f"{'='*60}")
        
        return self.results
    
    def _calculate_summary(self):
        """计算综合分数"""
        # 获取权重
        weights = self.config.get('weights')
        if weights is None:
            # 使用默认权重
            weights = {}
            for metric_name in self.evaluator_factory.get_available_metrics():
                weights[metric_name] = AVAILABLE_METRICS.get(metric_name, {}).get('default_weight', 0.1)
        
        # 归一化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        # 计算加权分数
        weighted_scores = []
        valid_metrics = []
        
        for metric_name, result in self.results['metrics'].items():
            if result.get('status') == 'success' and 'value' in result:
                score = result['value']
                weight = weights.get(metric_name, 0)
                
                # 对于某些指标需要特殊处理（越低越好）
                if metric_name in ['fid', 'lsec', 'lsed', 'niqe']:
                    # 这些指标越低越好，需要转换
                    if metric_name == 'fid':
                        # FID: 转换到0-1范围，假设小于200为合理范围
                        normalized = max(0, min(1, 1 - score/200))
                    elif metric_name == 'niqe':
                        # NIQE: 转换到0-1范围
                        normalized = max(0, min(1, 1 - score/10))
                    else:
                        # LSE-C和LSE-D: 直接取1-score
                        normalized = 1 - score
                else:
                    # 其他指标越高越好
                    normalized = score
                
                weighted_scores.append(normalized * weight)
                valid_metrics.append(metric_name)
        
        if weighted_scores:
            overall_score = sum(weighted_scores)
            
            # 根据分数给出评价
            if overall_score > 0.8:
                interpretation = "优秀：生成质量很高"
            elif overall_score > 0.6:
                interpretation = "良好：生成质量不错"
            elif overall_score > 0.4:
                interpretation = "一般：有改进空间"
            else:
                interpretation = "较差：需要显著改进"
        else:
            overall_score = 0.0
            interpretation = "无法计算综合分数"
        
        self.results['summary'] = {
            'overall_score': float(overall_score),
            'weights': weights,
            'valid_metrics': valid_metrics,
            'interpretation': interpretation,
            'calculation_time': time.time()
        }
    
    def _save_results(self, output_dir):
        """保存结果"""
        # 保存JSON结果
        video_name = self.video_info.get('video_name', 'unknown')
        json_file = os.path.join(output_dir, f"{video_name}_results.json")
        FileUtils.save_json(self.results, json_file)
        
        # 保存CSV摘要
        csv_file = os.path.join(output_dir, f"{video_name}_summary.csv")
        FileUtils.save_results_to_csv(self.results, csv_file)
        
        # 保存身份帧（如果存在）
        if self.source_image is not None:
            image_file = os.path.join(output_dir, f"{video_name}_identity.jpg")
            self.video_processor.save_frame_as_image(self.source_image, image_file)
    
    def _print_summary(self):
        """打印总结"""
        if 'summary' not in self.results:
            return
        
        summary = self.results['summary']
        
        print(f"\n{'='*60}")
        print("评测总结")
        print(f"{'='*60}")
        print(f"综合分数: {summary['overall_score']:.4f}")
        print(f"评价: {summary['interpretation']}")
        print(f"\n各指标结果:")
        
        for metric_name, result in self.results['metrics'].items():
            if result.get('status') == 'success' and 'value' in result:
                metric_info = AVAILABLE_METRICS.get(metric_name, {})
                metric_name_display = metric_info.get('name', metric_name)
                value = result['value']
                
                # 格式化输出
                if metric_name in ['fid', 'lsec', 'lsed', 'niqe']:
                    # 这些指标越低越好
                    print(f"  {metric_name_display}: {value:.4f} (越低越好)")
                else:
                    # 其他指标越高越好
                    print(f"  {metric_name_display}: {value:.4f} (越高越好)")
        
        print(f"{'='*60}")