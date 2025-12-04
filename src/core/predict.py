"""
预测接口模块

提供单张图像预测和批量预测功能。
"""

import os
import argparse
import numpy as np
from PIL import Image
import tensorflow as tf
try:
    from .model_utils import (
        load_model,
        predict_image,
        preprocess_image,
        get_class_name,
        CLASS_NAMES,
        NUM_CLASSES
    )
except ImportError:
    # 如果作为脚本直接运行，使用绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model_utils import (
        load_model,
        predict_image,
        preprocess_image,
        get_class_name,
        CLASS_NAMES,
        NUM_CLASSES
    )


def predict_single_image(model_path: str, image_path: str, top_k: int = 3):
    """
    预测单张图像
    
    参数:
        model_path: 模型文件路径
        image_path: 图像文件路径
        top_k: 返回前k个预测结果
    """
    print("=" * 60)
    print("服装款式识别预测")
    print("=" * 60)
    
    # 加载模型
    print(f"\n加载模型: {model_path}")
    model = load_model(model_path)
    
    # 检查图像文件
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    print(f"\n预测图像: {image_path}")
    
    # 预测
    results = predict_image(model, image_path, top_k=top_k)
    
    # 显示结果
    print("\n预测结果:")
    print("-" * 60)
    for i, result in enumerate(results, 1):
        confidence_percent = result['confidence'] * 100
        print(f"{i}. {result['class']:8} - 置信度: {confidence_percent:.2f}%")
    
    print("=" * 60)
    
    return results


def predict_batch(model_path: str, image_dir: str, top_k: int = 3, output_file: str = None):
    """
    批量预测图像
    
    参数:
        model_path: 模型文件路径
        image_dir: 图像目录路径
        top_k: 返回前k个预测结果
        output_file: 输出文件路径（CSV格式），如果为None则只打印结果
    """
    print("=" * 60)
    print("批量预测服装款式")
    print("=" * 60)
    
    # 加载模型
    print(f"\n加载模型: {model_path}")
    model = load_model(model_path)
    
    # 获取所有图像文件
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    image_files = []
    
    for file in os.listdir(image_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(image_dir, file))
    
    if not image_files:
        print(f"在 {image_dir} 中未找到图像文件")
        return
    
    print(f"\n找到 {len(image_files)} 张图像")
    
    # 预测所有图像
    all_results = []
    
    for image_path in image_files:
        try:
            results = predict_image(model, image_path, top_k=top_k)
            all_results.append({
                'image': os.path.basename(image_path),
                'predictions': results
            })
            
            # 显示结果
            print(f"\n{os.path.basename(image_path)}:")
            for i, result in enumerate(results, 1):
                confidence_percent = result['confidence'] * 100
                print(f"  {i}. {result['class']:8} - {confidence_percent:.2f}%")
        
        except Exception as e:
            print(f"\n{os.path.basename(image_path)}: 预测失败 - {e}")
            all_results.append({
                'image': os.path.basename(image_path),
                'predictions': None,
                'error': str(e)
            })
    
    # 保存到文件
    if output_file:
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['图像文件', '预测类别1', '置信度1', '预测类别2', '置信度2', '预测类别3', '置信度3'])
            
            for result in all_results:
                if result['predictions']:
                    row = [result['image']]
                    for pred in result['predictions']:
                        row.extend([pred['class'], f"{pred['confidence']*100:.2f}%"])
                    # 补齐到6列（3个预测结果）
                    while len(row) < 7:
                        row.extend(['', ''])
                    writer.writerow(row)
                else:
                    writer.writerow([result['image'], '预测失败', result.get('error', '')])
        
        print(f"\n结果已保存到: {output_file}")
    
    print("\n" + "=" * 60)
    print("批量预测完成")
    print("=" * 60)
    
    return all_results


def main():
    """主函数：解析命令行参数并执行预测"""
    parser = argparse.ArgumentParser(description='服装款式识别预测')
    
    parser.add_argument('--model', type=str, required=True,
                       help='模型文件路径')
    parser.add_argument('--image', type=str, default=None,
                       help='单张图像文件路径')
    parser.add_argument('--image_dir', type=str, default=None,
                       help='图像目录路径（批量预测）')
    parser.add_argument('--top_k', type=int, default=3,
                       help='返回前k个预测结果（默认: 3）')
    parser.add_argument('--output', type=str, default=None,
                       help='批量预测结果输出文件路径（CSV格式）')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.image and not args.image_dir:
        parser.error("必须指定 --image 或 --image_dir 参数")
    
    if args.image and args.image_dir:
        parser.error("不能同时指定 --image 和 --image_dir 参数")
    
    # 执行预测
    if args.image:
        predict_single_image(args.model, args.image, args.top_k)
    else:
        predict_batch(args.model, args.image_dir, args.top_k, args.output)


if __name__ == '__main__':
    main()

