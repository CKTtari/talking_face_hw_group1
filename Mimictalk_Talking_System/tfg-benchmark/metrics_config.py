"""
评测指标配置
"""

# 可用指标列表
AVAILABLE_METRICS = {
    'identity': {
        'name': '身份相似度',
        'description': '使用FaceNet计算源图像与生成视频的人脸相似度',
        'requires': ['source_image', 'generated_video'],
        'default_weight': 0.2
    },
    'fid': {
        'name': 'FID',
        'description': 'Fréchet Inception Distance - 生成分布与真实分布的相似度',
        'requires': ['real_video', 'generated_video'],
        'default_weight': 0.2
    },
    'lpips': {
        'name': 'LPIPS',
        'description': 'Learned Perceptual Image Patch Similarity - 感知相似度',
        'requires': ['real_video', 'generated_video'],
        'default_weight': 0.15
    },
    'ssim': {
        'name': 'SSIM',
        'description': 'Structural Similarity Index - 结构相似度',
        'requires': ['real_video', 'generated_video'],
        'default_weight': 0.1
    },
    'psnr': {
        'name': 'PSNR',
        'description': 'Peak Signal-to-Noise Ratio - 峰值信噪比',
        'requires': ['real_video', 'generated_video'],
        'default_weight': 0.1
    },
    'niqe': {
        'name': 'NIQE',
        'description': 'Natural Image Quality Evaluator - 自然图像质量评估',
        'requires': ['generated_video'],
        'default_weight': 0.1
    },
    'lsec': {
        'name': 'LSE-C',
        'description': 'Lip Sync Error - Confidence - 唇语同步置信度误差',
        'requires': ['audio', 'generated_video'],
        'default_weight': 0.075
    },
    'lsed': {
        'name': 'LSE-D',
        'description': 'Lip Sync Error - Distance - 唇语同步距离误差',
        'requires': ['audio', 'generated_video'],
        'default_weight': 0.075
    }
}

# 预设评测配置
PRESET_CONFIGS = {
    'full': {
        'metrics': ['identity', 'fid', 'lpips', 'ssim', 'psnr', 'niqe', 'lsec', 'lsed'],
        'description': '完整评测 - 包含所有指标'
    },
    'basic': {
        'metrics': ['identity', 'fid', 'ssim', 'psnr'],
        'description': '基础评测 - 包含核心指标'
    },
    'sync': {
        'metrics': ['lsec', 'lsed'],
        'description': '同步评测 - 重点评测唇语同步'
    },
    'quality': {
        'metrics': ['fid', 'lpips', 'ssim', 'psnr', 'niqe'],
        'description': '质量评测 - 重点评测生成质量'
    }
}

# 默认配置
DEFAULT_CONFIG = {
    'video_resolution': (512, 512),  # 视频预处理分辨率
    'num_frames': 30,                # 采样帧数
    'device': 'cuda',                # 计算设备
    'preset': 'full',                # 预设配置
    'weights': None,                 # 自定义权重，None时使用默认权重
    'syncnet_model_path': 'models/syncnet.pth',
    'output_dir': 'evaluation_results'  # 输出目录
}