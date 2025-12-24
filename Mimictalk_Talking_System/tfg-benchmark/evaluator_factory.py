"""
评测器工厂
根据配置创建和管理各个指标评测器
"""

import torch
from metrics_config import AVAILABLE_METRICS, PRESET_CONFIGS

class EvaluatorFactory:
    """评测器工厂"""
    
    def __init__(self, config):
        """
        初始化评测器工厂
        
        Args:
            config: 评测配置
        """
        self.config = config
        self.device = config.get('device', 'cuda')
        if self.device == 'cuda' and not torch.cuda.is_available():
            print("警告: CUDA不可用，将使用CPU")
            self.device = 'cpu'
        
        self.evaluators = {}
        self._init_evaluators()
    
    def _init_evaluators(self):
        """初始化各个评测器"""
        # 获取要评测的指标列表
        preset = self.config.get('preset', 'full')
        if preset in PRESET_CONFIGS:
            metric_names = PRESET_CONFIGS[preset]['metrics']
        else:
            metric_names = self.config.get('metrics', list(AVAILABLE_METRICS.keys()))
        
        # 创建评测器实例
        for metric_name in metric_names:
            if metric_name not in AVAILABLE_METRICS:
                print(f"警告: 未知指标 '{metric_name}'，跳过")
                continue
            
            try:
                evaluator = self._create_evaluator(metric_name)
                if evaluator:
                    self.evaluators[metric_name] = evaluator
                    print(f"✓ 初始化 {AVAILABLE_METRICS[metric_name]['name']} 评测器")
            except Exception as e:
                print(f"⚠ 初始化 {metric_name} 评测器失败: {e}")
    
    def _create_evaluator(self, metric_name):
        """
        创建指定指标的评测器
        
        Args:
            metric_name: 指标名称
            
        Returns:
            object: 评测器实例
        """
        if metric_name == 'identity':
            from metrics.identity_metric import IdentityMetric
            return IdentityMetric(device=self.device)
        
        elif metric_name == 'fid':
            from metrics.fid_metric import FIDMetric
            return FIDMetric(device=self.device)
        
        elif metric_name == 'lpips':
            from metrics.lpips_metric import LPIPSMetric
            return LPIPSMetric(device=self.device)
        
        elif metric_name == 'ssim':
            from metrics.ssim_metric import SSIMMetric
            return SSIMMetric(device=self.device)
        
        elif metric_name == 'psnr':
            from metrics.psnr_metric import PSNRMetric
            return PSNRMetric(device=self.device)
        
        elif metric_name == 'niqe':
            from metrics.niqe_metric import NIQEMetric
            return NIQEMetric(device=self.device)
        
        elif metric_name == 'lsec':
            from metrics.lsec_metric import LSECMetric
            return LSECMetric(device=self.device, model_path=self.config['syncnet_model_path'])
        
        elif metric_name == 'lsed':
            from metrics.lsed_metric import LSEDMetric
            return LSEDMetric(device=self.device, model_path=self.config['syncnet_model_path'])
        
        else:
            return None
    
    def get_evaluator(self, metric_name):
        """
        获取指定指标的评测器
        
        Args:
            metric_name: 指标名称
            
        Returns:
            object: 评测器实例，None表示不存在
        """
        return self.evaluators.get(metric_name)
    
    def get_all_evaluators(self):
        """获取所有评测器"""
        return self.evaluators
    
    def get_available_metrics(self):
        """获取可用的指标列表"""
        return list(self.evaluators.keys())
    
    def check_requirements(self, metric_name, available_data):
        """
        检查指标的计算要求是否满足
        
        Args:
            metric_name: 指标名称
            available_data: 可用数据字典
            
        Returns:
            bool: 是否满足要求
            str: 错误信息（如果不满足）
        """
        if metric_name not in AVAILABLE_METRICS:
            return False, f"未知指标: {metric_name}"
        
        requirements = AVAILABLE_METRICS[metric_name]['requires']
        for req in requirements:
            if req not in available_data:
                return False, f"缺少必要数据: {req}"
        
        return True, ""