"""
款式识别模块使用示例

演示如何使用款式识别模块进行训练和预测。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.style_recognizer import StyleRecognizer, create_recognizer


def example_predict():
    """预测示例"""
    print("=" * 60)
    print("款式识别预测示例")
    print("=" * 60)
    
    # 方法1：使用StyleRecognizer类
    model_path = 'models/best_model.h5'
    
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        print("请先训练模型或提供正确的模型路径")
        return
    
    recognizer = StyleRecognizer(model_path)
    
    # 预测单张图像
    image_path = 'static/images/test.jpg'
    if os.path.exists(image_path):
        results = recognizer.predict(image_path, top_k=3)
        print(f"\n预测结果 ({image_path}):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['class']:8} - 置信度: {result['confidence']*100:.2f}%")
    else:
        print(f"测试图像不存在: {image_path}")
    
    # 方法2：使用便捷函数
    recognizer2 = create_recognizer(model_path)
    print(f"\n支持的类别: {recognizer2.get_class_names()}")


def example_batch_predict():
    """批量预测示例"""
    print("\n" + "=" * 60)
    print("批量预测示例")
    print("=" * 60)
    
    model_path = 'models/best_model.h5'
    image_dir = 'static/images'
    
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return
    
    if not os.path.exists(image_dir):
        print(f"图像目录不存在: {image_dir}")
        return
    
    recognizer = StyleRecognizer(model_path)
    
    # 获取所有图像文件
    image_files = []
    for file in os.listdir(image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(os.path.join(image_dir, file))
    
    if not image_files:
        print(f"在 {image_dir} 中未找到图像文件")
        return
    
    # 批量预测
    results = recognizer.predict_batch(image_files[:5], top_k=3)  # 只预测前5张
    
    print(f"\n批量预测结果:")
    for result in results:
        if result['success']:
            top_prediction = result['predictions'][0]
            print(f"  {os.path.basename(result['image_path']):30} -> {top_prediction['class']:8} ({top_prediction['confidence']*100:.2f}%)")
        else:
            print(f"  {os.path.basename(result['image_path']):30} -> 预测失败: {result['error']}")


if __name__ == '__main__':
    print("款式识别模块使用示例")
    print("\n注意：运行此示例需要先训练模型")
    print("训练命令：python -m src.core.train --train_dir data/train --validation_dir data/validation")
    print("\n" + "=" * 60)
    
    # 运行预测示例
    example_predict()
    
    # 运行批量预测示例
    example_batch_predict()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)

