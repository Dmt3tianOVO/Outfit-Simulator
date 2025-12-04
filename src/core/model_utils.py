"""
模型工具函数模块

提供模型定义、数据增强、模型保存和加载等功能。
使用MobileNetV2作为基础模型进行迁移学习。
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
from typing import Tuple, Optional


# 服装类别定义
CLASS_NAMES = [
    'T恤',      # 0
    '衬衫',      # 1
    '卫衣',      # 2
    '外套',      # 3
    '牛仔裤',    # 4
    '休闲裤',    # 5
    '运动鞋',    # 6
    '皮鞋'       # 7
]

NUM_CLASSES = len(CLASS_NAMES)
IMG_SIZE = 224  # MobileNetV2输入尺寸


def create_model(input_shape: Tuple[int, int, int] = (IMG_SIZE, IMG_SIZE, 3),
                 num_classes: int = NUM_CLASSES,
                 base_model_trainable: bool = False) -> keras.Model:
    """
    创建基于MobileNetV2的迁移学习模型
    
    参数:
        input_shape: 输入图像形状，默认(224, 224, 3)
        num_classes: 分类数量，默认8类
        base_model_trainable: 是否冻结基础模型权重，默认False（冻结）
    
    返回:
        keras.Model: 编译好的模型
    """
    # 加载预训练的MobileNetV2模型（不包含顶层）
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet',
        alpha=1.0  # 控制网络宽度，1.0为标准宽度
    )
    
    # 冻结基础模型权重（迁移学习标准做法）
    base_model.trainable = base_model_trainable
    
    # 构建模型
    inputs = keras.Input(shape=input_shape)
    
    # 注意：预处理在数据生成器中完成（rescale=1./255）
    # 这里直接使用归一化后的输入（0-1范围）
    x = inputs
    
    # 通过基础模型
    x = base_model(x, training=False)
    
    # 全局平均池化
    x = layers.GlobalAveragePooling2D()(x)
    
    # Dropout层防止过拟合
    x = layers.Dropout(0.2)(x)
    
    # 分类层
    outputs = layers.Dense(num_classes, activation='softmax', name='predictions')(x)
    
    # 创建模型
    model = keras.Model(inputs, outputs, name='outfit_classifier')
    
    return model


def get_data_generators(train_dir: str,
                       validation_dir: str,
                       batch_size: int = 32,
                       img_size: int = IMG_SIZE) -> Tuple[ImageDataGenerator, ImageDataGenerator]:
    """
    创建数据生成器，包含数据增强
    
    参数:
        train_dir: 训练数据目录路径
        validation_dir: 验证数据目录路径
        batch_size: 批次大小
        img_size: 图像尺寸
    
    返回:
        Tuple[ImageDataGenerator, ImageDataGenerator]: (训练生成器, 验证生成器)
    """
    # 训练数据增强
    # 注意：使用rescale=1./255将像素值归一化到[0, 1]范围
    # MobileNetV2的preprocess_input会将值缩放到[-1, 1]，但这里我们使用简单的归一化
    train_datagen = ImageDataGenerator(
        rescale=1./255,  # 归一化到0-1
        rotation_range=20,  # 随机旋转20度
        width_shift_range=0.2,  # 水平平移
        height_shift_range=0.2,  # 垂直平移
        shear_range=0.2,  # 剪切变换
        zoom_range=0.2,  # 随机缩放
        horizontal_flip=True,  # 水平翻转
        fill_mode='nearest',  # 填充模式
        brightness_range=[0.8, 1.2],  # 亮度调整
    )
    
    # 验证数据只进行归一化，不做增强
    validation_datagen = ImageDataGenerator(
        rescale=1./255  # 归一化到0-1
    )
    
    # 创建数据生成器
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True,
        seed=42
    )
    
    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False,
        seed=42
    )
    
    return train_generator, validation_generator


def compile_model(model: keras.Model, learning_rate: float = 0.0001) -> keras.Model:
    """
    编译模型
    
    参数:
        model: 未编译的模型
        learning_rate: 学习率，默认0.0001（迁移学习建议使用较小学习率）
    
    返回:
        keras.Model: 编译好的模型
    """
    # 使用TopKCategoricalAccuracy代替字符串'top_3_accuracy'
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')
        ]
    )
    
    return model


def save_model(model: keras.Model, model_dir: str, model_name: str = 'outfit_classifier'):
    """
    保存模型
    
    参数:
        model: 要保存的模型
        model_dir: 模型保存目录
        model_name: 模型名称
    """
    os.makedirs(model_dir, exist_ok=True)
    
    # 保存完整模型
    model_path = os.path.join(model_dir, f'{model_name}.h5')
    model.save(model_path)
    print(f"模型已保存到: {model_path}")
    
    # 保存模型架构为JSON
    json_path = os.path.join(model_dir, f'{model_name}_architecture.json')
    with open(json_path, 'w') as f:
        f.write(model.to_json())
    print(f"模型架构已保存到: {json_path}")


def load_model(model_path: str) -> keras.Model:
    """
    加载保存的模型
    
    参数:
        model_path: 模型文件路径
    
    返回:
        keras.Model: 加载的模型
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    model = keras.models.load_model(model_path)
    print(f"模型已从 {model_path} 加载")
    
    return model


def get_class_name(class_index: int) -> str:
    """
    根据类别索引获取类别名称
    
    参数:
        class_index: 类别索引（0-7）
    
    返回:
        str: 类别名称
    """
    if 0 <= class_index < len(CLASS_NAMES):
        return CLASS_NAMES[class_index]
    else:
        raise ValueError(f"无效的类别索引: {class_index}, 应该在0-{len(CLASS_NAMES)-1}之间")


def preprocess_image(image_path: str, img_size: int = IMG_SIZE) -> np.ndarray:
    """
    预处理单张图像用于预测
    
    参数:
        image_path: 图像文件路径
        img_size: 图像尺寸
    
    返回:
        np.ndarray: 预处理后的图像数组，形状为(1, img_size, img_size, 3)
    """
    from PIL import Image
    
    # 读取图像
    img = Image.open(image_path)
    
    # 转换为RGB（处理RGBA等情况）
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 调整大小
    img = img.resize((img_size, img_size))
    
    # 转换为numpy数组
    img_array = np.array(img)
    
    # 归一化到0-1
    img_array = img_array.astype('float32') / 255.0
    
    # 添加批次维度
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def predict_image(model: keras.Model, image_path: str, top_k: int = 3) -> list:
    """
    预测单张图像的类别
    
    参数:
        model: 训练好的模型
        image_path: 图像文件路径
        top_k: 返回前k个预测结果
    
    返回:
        list: 预测结果列表，每个元素为{'class': 类别名, 'confidence': 置信度}
    """
    # 预处理图像
    img_array = preprocess_image(image_path)
    
    # 预测
    predictions = model.predict(img_array, verbose=0)
    
    # 获取top_k预测结果
    top_indices = np.argsort(predictions[0])[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'class': get_class_name(idx),
            'confidence': float(predictions[0][idx])
        })
    
    return results

