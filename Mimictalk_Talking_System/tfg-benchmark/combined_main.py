"""
主程序入口
提供命令行接口
"""

import os
import sys
import argparse
import torch
from main_evaluator import MainEvaluator
from metrics_config import PRESET_CONFIGS, DEFAULT_CONFIG

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Talking Face Generation 综合评测系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 完整评测（需要参考视频和生成视频）
  python combined_main.py --reference ref_video.mp4 --generated gen_video.mp4
  
  # 基础评测
  python combined_main.py --reference ref_video.mp4 --generated gen_video.mp4 --preset basic
  
  # 自定义指标
  python combined_main.py --reference ref_video.mp4 --generated gen_video.mp4 --metrics identity ssim psnr
  
  # 批量模式（处理目录下所有视频）
  python combined_main.py --reference_dir ref_videos/ --generated_dir gen_videos/ --batch
        """
    )
    
    # 视频输入
    input_group = parser.add_argument_group('视频输入')
    input_group.add_argument('--reference', type=str, default='',
                           help='参考视频路径（单视频模式）')
    input_group.add_argument('--generated', type=str, required=True,
                           help='生成视频路径（必需）')
    input_group.add_argument('--reference_dir', type=str, default='',
                           help='参考视频目录（批量模式）')
    input_group.add_argument('--generated_dir', type=str, default='',
                           help='生成视频目录（批量模式）')
    
    # 评测配置
    config_group = parser.add_argument_group('评测配置')
    config_group.add_argument('--preset', type=str, default='full',
                            choices=list(PRESET_CONFIGS.keys()),
                            help=f'评测预设（默认: full）')
    config_group.add_argument('--metrics', type=str, nargs='+',
                            help='自定义评测指标列表')
    config_group.add_argument('--num_frames', type=int, default=30,
                            help='采样帧数（默认: 30）')
    config_group.add_argument('--resolution', type=int, nargs=2, default=[512, 512],
                            help='视频预处理分辨率（默认: 512 512）')
    config_group.add_argument('--syncnet_model', type=str, default='models/syncnet.pth',
                        help='SyncNet模型路径（用于LSE-C/D指标）')
    
    # 输出配置
    output_group = parser.add_argument_group('输出配置')
    output_group.add_argument('--output_dir', type=str, default='evaluation_results',
                            help='输出目录（默认: evaluation_results）')
    output_group.add_argument('--batch', action='store_true',
                            help='批量模式（处理目录下所有视频）')
    output_group.add_argument('--device', type=str, default='cuda',
                            choices=['cuda', 'cpu'],
                            help='计算设备（默认: cuda）')
    output_group.add_argument('--verbose', action='store_true',
                            help='详细输出模式')
    
    return parser.parse_args()

def check_dependencies():
    """检查依赖"""
    required_packages = ['torch', 'torchvision', 'cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("错误: 缺少必要依赖包:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n请使用以下命令安装:")
        print("pip install torch torchvision opencv-python numpy")
        return False
    
    # 检查pyiqa（可选但推荐）
    try:
        import pyiqa
        print("✓ pyiqa 已安装")
    except ImportError:
        print("⚠ pyiqa 未安装，部分指标将不可用")
        print("  建议安装: pip install pyiqa")
    
    # 检查facenet-pytorch（可选）
    try:
        import facenet_pytorch
        print("✓ facenet-pytorch 已安装")
    except ImportError:
        print("⚠ facenet-pytorch 未安装，身份相似度指标将使用简化版本")
        print("  建议安装: pip install facenet-pytorch")
    
    return True

def process_single_video(args):
    """处理单个视频"""
    print(f"\n处理单个视频:")
    print(f"  参考视频: {args.reference if args.reference else '无（部分指标将跳过）'}")
    print(f"  生成视频: {args.generated}")
    
    # 检查文件是否存在
    if not os.path.exists(args.generated):
        print(f"错误: 生成视频不存在: {args.generated}")
        return False
    
    if args.reference and not os.path.exists(args.reference):
        print(f"错误: 参考视频不存在: {args.reference}")
        return False
    
    # 创建配置
    config = DEFAULT_CONFIG.copy()
    config.update({
        'video_resolution': tuple(args.resolution),
        'num_frames': args.num_frames,
        'device': args.device,
        'preset': args.preset,
        'output_dir': args.output_dir
    })
    
    if args.metrics:
        config['metrics'] = args.metrics
    
    # 创建评测器
    evaluator = MainEvaluator(config)
    
    # 设置视频
    if args.reference:
        evaluator.set_reference_video(args.reference)
    evaluator.set_generated_video(args.generated)
    
    # 执行评测
    results = evaluator.evaluate()
    
    return results is not None

def process_batch_videos(args):
    """批量处理视频"""
    print(f"\n批量处理模式:")
    print(f"  参考视频目录: {args.reference_dir}")
    print(f"  生成视频目录: {args.generated_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(args.reference_dir):
        print(f"错误: 参考视频目录不存在: {args.reference_dir}")
        return False
    
    if not os.path.exists(args.generated_dir):
        print(f"错误: 生成视频目录不存在: {args.generated_dir}")
        return False
    
    # 查找视频文件
    from utils.file_utils import FileUtils
    
    ref_videos = FileUtils.find_video_files(args.reference_dir)
    gen_videos = FileUtils.find_video_files(args.generated_dir)
    
    if not ref_videos:
        print(f"错误: 在 {args.reference_dir} 中未找到视频文件")
        return False
    
    if not gen_videos:
        print(f"错误: 在 {args.generated_dir} 中未找到视频文件")
        return False
    
    print(f"  找到 {len(ref_videos)} 个参考视频")
    print(f"  找到 {len(gen_videos)} 个生成视频")
    
    # 匹配视频对（按文件名）
    video_pairs = []
    for ref_video in ref_videos:
        ref_name = FileUtils.get_video_basename(ref_video)
        
        # 查找对应的生成视频
        for gen_video in gen_videos:
            gen_name = FileUtils.get_video_basename(gen_video)
            if ref_name == gen_name:
                video_pairs.append((ref_video, gen_video))
                break
    
    if not video_pairs:
        print("错误: 未找到匹配的视频对")
        return False
    
    print(f"  匹配到 {len(video_pairs)} 对视频")
    
    # 创建配置
    config = DEFAULT_CONFIG.copy()
    config.update({
        'video_resolution': tuple(args.resolution),
        'num_frames': args.num_frames,
        'device': args.device,
        'preset': args.preset,
        'output_dir': args.output_dir
    })
    
    if args.metrics:
        config['metrics'] = args.metrics
    config['syncnet_model_path'] = args.syncnet_model
    
    # 处理每个视频对
    all_results = {}
    successful = 0
    
    for i, (ref_video, gen_video) in enumerate(video_pairs, 1):
        print(f"\n{'='*60}")
        print(f"处理第 {i}/{len(video_pairs)} 对视频")
        print(f"  参考: {os.path.basename(ref_video)}")
        print(f"  生成: {os.path.basename(gen_video)}")
        
        try:
            # 创建评测器
            evaluator = MainEvaluator(config)
            evaluator.set_reference_video(ref_video)
            evaluator.set_generated_video(gen_video)
            
            # 执行评测
            results = evaluator.evaluate()
            
            if results:
                video_name = FileUtils.get_video_basename(gen_video)
                all_results[video_name] = results
                successful += 1
                
        except Exception as e:
            print(f"  处理失败: {e}")
    
    # 保存批量结果
    if all_results:
        batch_summary = {
            'total_pairs': len(video_pairs),
            'successful': successful,
            'failed': len(video_pairs) - successful,
            'results': all_results
        }
        
        summary_file = os.path.join(args.output_dir, 'batch_summary.json')
        FileUtils.save_json(batch_summary, summary_file)
        
        print(f"\n批量处理完成!")
        print(f"  成功: {successful}/{len(video_pairs)}")
        print(f"  失败: {len(video_pairs) - successful}/{len(video_pairs)}")
        print(f"  总结已保存: {summary_file}")
        
        return True
    
    return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("Talking Face Generation 综合评测系统")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 解析参数
    args = parse_arguments()
    
    # 检查设备
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("警告: CUDA不可用，将使用CPU")
        args.device = 'cpu'
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        if args.batch:
            # 批量模式
            if not args.reference_dir or not args.generated_dir:
                print("错误: 批量模式需要指定 --reference_dir 和 --generated_dir")
                return 1
            
            success = process_batch_videos(args)
        else:
            # 单视频模式
            if not args.generated:
                print("错误: 必须指定 --generated 参数")
                return 1
            
            success = process_single_video(args)
        
        if success:
            print(f"\n✅ 处理完成!")
            return 0
        else:
            print(f"\n❌ 处理失败!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())