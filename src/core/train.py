"""
训练脚本

使用MobileNetV2进行迁移学习，训练服装款式识别模型。
支持数据增强、模型保存、训练过程可视化等功能。
"""

import os
import argparse
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
import matplotlib.pyplot as plt
try:
    from .model_utils import (
        create_model,
        get_data_generators,
        compile_model,
        save_model,
        NUM_CLASSES,
        IMG_SIZE,
        CLASS_NAMES
    )
except ImportError:
    # 如果作为脚本直接运行，使用绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model_utils import (
        create_model,
        get_data_generators,
        compile_model,
        save_model,
        NUM_CLASSES,
        IMG_SIZE,
        CLASS_NAMES
    )


def plot_training_history(history, save_path: str = None):
    """
    绘制训练历史曲线
    
    参数:
        history: 训练历史对象
        save_path: 保存路径，如果为None则显示图像
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # 准确率曲线
    axes[0].plot(history.history['accuracy'], label='训练准确率')
    axes[0].plot(history.history['val_accuracy'], label='验证准确率')
    axes[0].set_title('模型准确率')
    axes[0].set_xlabel('轮次')
    axes[0].set_ylabel('准确率')
    axes[0].legend()
    axes[0].grid(True)
    
    # 损失曲线
    axes[1].plot(history.history['loss'], label='训练损失')
    axes[1].plot(history.history['val_loss'], label='验证损失')
    axes[1].set_title('模型损失')
    axes[1].set_xlabel('轮次')
    axes[1].set_ylabel('损失')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"训练曲线已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()


def train_model(train_dir: str,
                validation_dir: str,
                model_dir: str = 'models',
                batch_size: int = 32,
                epochs: int = 50,
                learning_rate: float = 0.0001,
                fine_tune: bool = False,
                fine_tune_epochs: int = 10,
                fine_tune_learning_rate: float = 0.00001):
    """
    训练模型
    
    参数:
        train_dir: 训练数据目录
        validation_dir: 验证数据目录
        model_dir: 模型保存目录
        batch_size: 批次大小
        epochs: 训练轮数
        learning_rate: 初始学习率
        fine_tune: 是否进行微调（解冻部分层）
        fine_tune_epochs: 微调轮数
        fine_tune_learning_rate: 微调学习率
    """
    print("=" * 60)
    print("开始训练服装款式识别模型")
    print("=" * 60)
    
    # 检查数据目录
    if not os.path.exists(train_dir):
        raise ValueError(f"训练数据目录不存在: {train_dir}")
    if not os.path.exists(validation_dir):
        raise ValueError(f"验证数据目录不存在: {validation_dir}")
    
    # 创建模型保存目录
    os.makedirs(model_dir, exist_ok=True)
    
    # 创建数据生成器
    print("\n创建数据生成器...")
    train_generator, validation_generator = get_data_generators(
        train_dir, validation_dir, batch_size=batch_size
    )
    
    print(f"训练样本数: {train_generator.samples}")
    print(f"验证样本数: {validation_generator.samples}")
    print(f"类别数: {len(train_generator.class_indices)}")
    print(f"类别: {CLASS_NAMES}")
    
    # 创建模型
    print("\n创建模型...")
    model = create_model(num_classes=NUM_CLASSES, base_model_trainable=False)
    model = compile_model(model, learning_rate=learning_rate)
    
    print(f"模型参数总数: {model.count_params():,}")
    print(f"可训练参数: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    
    # 定义回调函数
    callbacks = [
        # 模型检查点：保存最佳模型
        ModelCheckpoint(
            filepath=os.path.join(model_dir, 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        # 早停：防止过拟合
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        # 学习率衰减
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        # 记录训练日志
        CSVLogger(
            filename=os.path.join(model_dir, 'training_log.csv'),
            append=False
        )
    ]
    
    # 第一阶段训练：冻结基础模型
    print("\n" + "=" * 60)
    print("第一阶段训练：冻结基础模型（迁移学习）")
    print("=" * 60)
    
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # 可选：第二阶段微调（解冻部分层）
    if fine_tune:
        print("\n" + "=" * 60)
        print("第二阶段训练：微调（解冻部分层）")
        print("=" * 60)
        
        # 解冻基础模型的最后几层
        base_model = model.layers[2]  # MobileNetV2层
        base_model.trainable = True
        
        # 只微调最后几层
        for layer in base_model.layers[:-30]:
            layer.trainable = False
        
        # 重新编译模型（使用更小的学习率）
        model = compile_model(model, learning_rate=fine_tune_learning_rate)
        
        print(f"微调可训练参数: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
        
        # 继续训练
        fine_tune_history = model.fit(
            train_generator,
            epochs=fine_tune_epochs,
            validation_data=validation_generator,
            callbacks=callbacks,
            verbose=1,
            initial_epoch=len(history.history['loss'])
        )
        
        # 合并历史记录
        for key in history.history.keys():
            history.history[key].extend(fine_tune_history.history[key])
    
    # 保存最终模型
    print("\n保存最终模型...")
    save_model(model, model_dir, 'outfit_classifier_final')
    
    # 绘制训练曲线
    plot_training_history(history, save_path=os.path.join(model_dir, 'training_history.png'))
    
    print("\n" + "=" * 60)
    print("训练完成！")
    print("=" * 60)
    print(f"最佳验证准确率: {max(history.history['val_accuracy']):.4f}")
    print(f"最终验证准确率: {history.history['val_accuracy'][-1]:.4f}")
    print(f"模型保存在: {model_dir}")
    print("=" * 60)
    
    return model, history


def main():
    """主函数：解析命令行参数并开始训练"""
    parser = argparse.ArgumentParser(description='训练服装款式识别模型')
    
    parser.add_argument('--train_dir', type=str, required=True,
                       help='训练数据目录路径')
    parser.add_argument('--validation_dir', type=str, required=True,
                       help='验证数据目录路径')
    parser.add_argument('--model_dir', type=str, default='models',
                       help='模型保存目录（默认: models）')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='批次大小（默认: 32）')
    parser.add_argument('--epochs', type=int, default=50,
                       help='训练轮数（默认: 50）')
    parser.add_argument('--learning_rate', type=float, default=0.0001,
                       help='初始学习率（默认: 0.0001）')
    parser.add_argument('--fine_tune', action='store_true',
                       help='是否进行微调（解冻部分层）')
    parser.add_argument('--fine_tune_epochs', type=int, default=10,
                       help='微调轮数（默认: 10）')
    parser.add_argument('--fine_tune_lr', type=float, default=0.00001,
                       help='微调学习率（默认: 0.00001）')
    
    args = parser.parse_args()
    
    # 开始训练
    train_model(
        train_dir=args.train_dir,
        validation_dir=args.validation_dir,
        model_dir=args.model_dir,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        fine_tune=args.fine_tune,
        fine_tune_epochs=args.fine_tune_epochs,
        fine_tune_learning_rate=args.fine_tune_lr
    )


if __name__ == '__main__':
    # 设置GPU内存增长（避免一次性分配所有GPU内存）
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)
    
    main()

