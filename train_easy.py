"""
简化的模型训练脚本

这个脚本提供了一个更简单的训练接口，适合快速开始。
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.train import train_model


def main():
    """简化的训练流程"""
    
    print("=" * 70)
    print("欢迎使用服装款式识别模型训练工具")
    print("=" * 70)
    
    # 检查数据目录
    train_dir = 'data/train'
    validation_dir = 'data/validation'
    
    print("\n【步骤1】检查数据目录...")
    
    if not os.path.exists(train_dir):
        print(f"\n❌ 错误: 训练数据目录不存在: {train_dir}")
        print("\n请按以下步骤准备数据:")
        print("1. 创建目录结构:")
        print("   data/")
        print("   ├── train/")
        print("   │   ├── T恤/")
        print("   │   ├── 衬衫/")
        print("   │   ├── 卫衣/")
        print("   │   ├── 外套/")
        print("   │   ├── 牛仔裤/")
        print("   │   ├── 休闲裤/")
        print("   │   ├── 运动鞋/")
        print("   │   └── 皮鞋/")
        print("   └── validation/")
        print("       └── (同上)")
        print("\n2. 将图片放入对应的类别文件夹")
        print("3. 每个类别至少需要50-100张图片")
        print("\n详细说明请查看: TRAINING_GUIDE.md")
        return
    
    if not os.path.exists(validation_dir):
        print(f"\n❌ 错误: 验证数据目录不存在: {validation_dir}")
        print("\n请创建验证数据目录并放入图片")
        print("详细说明请查看: TRAINING_GUIDE.md")
        return
    
    # 检查是否有数据
    train_classes = [d for d in os.listdir(train_dir) 
                     if os.path.isdir(os.path.join(train_dir, d))]
    
    if not train_classes:
        print(f"\n❌ 错误: {train_dir} 中没有找到类别文件夹")
        print("\n请确保数据按以下结构组织:")
        print("data/train/T恤/img001.jpg")
        print("data/train/衬衫/img001.jpg")
        print("...")
        return
    
    print(f"✓ 找到训练数据目录: {train_dir}")
    print(f"✓ 找到验证数据目录: {validation_dir}")
    print(f"✓ 检测到 {len(train_classes)} 个类别: {', '.join(train_classes)}")
    
    # 统计图片数量
    total_train = 0
    total_val = 0
    
    print("\n类别统计:")
    for cls in train_classes:
        train_path = os.path.join(train_dir, cls)
        val_path = os.path.join(validation_dir, cls)
        
        train_count = len([f for f in os.listdir(train_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        val_count = 0
        if os.path.exists(val_path):
            val_count = len([f for f in os.listdir(val_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        total_train += train_count
        total_val += val_count
        
        print(f"  {cls:10s}: 训练 {train_count:3d} 张, 验证 {val_count:3d} 张")
    
    print(f"\n总计: 训练 {total_train} 张, 验证 {total_val} 张")
    
    if total_train < 100:
        print("\n⚠️  警告: 训练数据较少（少于100张）")
        print("   建议每个类别至少准备50-100张图片以获得更好的效果")
    
    if total_val < 20:
        print("\n⚠️  警告: 验证数据较少（少于20张）")
        print("   建议准备至少20-50张验证图片")
    
    # 询问用户是否继续
    print("\n" + "=" * 70)
    print("【步骤2】配置训练参数")
    print("=" * 70)
    
    print("\n使用默认配置:")
    print("  - 训练轮数: 30 轮（快速训练）")
    print("  - 批次大小: 32")
    print("  - 学习率: 0.0001")
    print("  - 预计时间: 30-90分钟（取决于硬件）")
    
    response = input("\n是否开始训练? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n训练已取消")
        return
    
    # 开始训练
    print("\n" + "=" * 70)
    print("【步骤3】开始训练")
    print("=" * 70)
    print("\n提示:")
    print("  - 训练过程中可以按 Ctrl+C 停止")
    print("  - 最佳模型会自动保存到 models/best_model.h5")
    print("  - 训练曲线会保存到 models/training_history.png")
    print("\n")
    
    try:
        model, history = train_model(
            train_dir=train_dir,
            validation_dir=validation_dir,
            model_dir='models',
            batch_size=32,
            epochs=30,  # 快速训练，可以改为50或更多
            learning_rate=0.0001,
            fine_tune=False,  # 快速训练不微调，如需更高精度可改为True
            fine_tune_epochs=10,
            fine_tune_learning_rate=0.00001
        )
        
        print("\n" + "=" * 70)
        print("【训练完成】")
        print("=" * 70)
        print("\n✓ 模型已保存到: models/best_model.h5")
        print("✓ 训练曲线已保存到: models/training_history.png")
        print("✓ 训练日志已保存到: models/training_log.csv")
        
        print("\n下一步:")
        print("1. 查看训练曲线: models/training_history.png")
        print("2. 启动应用测试: python run.py")
        print("3. 访问 http://localhost:5000 上传图片测试效果")
        
        print("\n如果效果不理想，可以:")
        print("- 增加训练数据")
        print("- 增加训练轮数（修改 train_easy.py 中的 epochs 参数）")
        print("- 启用微调（修改 train_easy.py 中的 fine_tune=True）")
        
    except KeyboardInterrupt:
        print("\n\n训练已被用户中断")
        print("部分训练的模型可能已保存到 models/ 目录")
    except Exception as e:
        print(f"\n\n❌ 训练出错: {e}")
        import traceback
        traceback.print_exc()
        print("\n请检查:")
        print("1. 数据目录结构是否正确")
        print("2. 图片格式是否支持（JPG、PNG）")
        print("3. 是否有足够的磁盘空间")
        print("\n详细说明请查看: TRAINING_GUIDE.md")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
