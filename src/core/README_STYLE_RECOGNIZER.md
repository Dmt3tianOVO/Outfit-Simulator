# 款式识别模块使用说明

## 概述

款式识别模块使用MobileNetV2进行迁移学习，可以识别8种服装类别：
- T恤
- 衬衫
- 卫衣
- 外套
- 牛仔裤
- 休闲裤
- 运动鞋
- 皮鞋

## 文件结构

```
src/core/
├── model_utils.py      # 模型工具函数（模型定义、数据增强等）
├── train.py            # 训练脚本
├── predict.py          # 预测接口（命令行）
└── style_recognizer.py # Python API接口
```

## 数据准备

训练数据需要按照以下目录结构组织：

```
data/
├── train/
│   ├── T恤/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   ├── 衬衫/
│   │   └── ...
│   ├── 卫衣/
│   ├── 外套/
│   ├── 牛仔裤/
│   ├── 休闲裤/
│   ├── 运动鞋/
│   └── 皮鞋/
└── validation/
    ├── T恤/
    ├── 衬衫/
    └── ... (同样的结构)
```

## 训练模型

### 基本训练

```bash
# 在项目根目录下运行
python -m src.core.train \
    --train_dir data/train \
    --validation_dir data/validation \
    --model_dir models \
    --batch_size 32 \
    --epochs 50 \
    --learning_rate 0.0001
```

### 带微调的训练

```bash
python -m src.core.train \
    --train_dir data/train \
    --validation_dir data/validation \
    --model_dir models \
    --batch_size 32 \
    --epochs 50 \
    --learning_rate 0.0001 \
    --fine_tune \
    --fine_tune_epochs 10 \
    --fine_tune_lr 0.00001
```

### 参数说明

- `--train_dir`: 训练数据目录路径（必需）
- `--validation_dir`: 验证数据目录路径（必需）
- `--model_dir`: 模型保存目录（默认: models）
- `--batch_size`: 批次大小（默认: 32）
- `--epochs`: 训练轮数（默认: 50）
- `--learning_rate`: 初始学习率（默认: 0.0001）
- `--fine_tune`: 是否进行微调（解冻部分层）
- `--fine_tune_epochs`: 微调轮数（默认: 10）
- `--fine_tune_lr`: 微调学习率（默认: 0.00001）

### 训练输出

训练完成后，会在 `model_dir` 目录下生成：
- `best_model.h5`: 验证集上表现最好的模型
- `outfit_classifier_final.h5`: 最终训练完成的模型
- `outfit_classifier_final_architecture.json`: 模型架构JSON文件
- `training_log.csv`: 训练日志
- `training_history.png`: 训练曲线图

## 预测

### 命令行预测

#### 单张图像预测

```bash
python -m src.core.predict \
    --model models/best_model.h5 \
    --image path/to/image.jpg \
    --top_k 3
```

#### 批量预测

```bash
python -m src.core.predict \
    --model models/best_model.h5 \
    --image_dir path/to/images \
    --top_k 3 \
    --output results.csv
```

### Python API使用

```python
from src.core.style_recognizer import StyleRecognizer

# 创建识别器
recognizer = StyleRecognizer('models/best_model.h5')

# 预测单张图像
results = recognizer.predict('image.jpg', top_k=3)
for result in results:
    print(f"{result['class']}: {result['confidence']*100:.2f}%")

# 批量预测
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
batch_results = recognizer.predict_batch(image_paths, top_k=3)
for result in batch_results:
    if result['success']:
        print(f"{result['image_path']}: {result['predictions'][0]['class']}")
    else:
        print(f"{result['image_path']}: 预测失败 - {result['error']}")

# 获取类别列表
class_names = recognizer.get_class_names()
print(f"支持的类别: {class_names}")
```

### 在代码中使用

```python
from src.core import create_recognizer

# 创建识别器
recognizer = create_recognizer('models/best_model.h5')

# 预测
results = recognizer.predict('image.jpg')
print(f"预测结果: {results[0]['class']}")
```

## 模型特点

1. **迁移学习**: 使用ImageNet预训练的MobileNetV2作为基础模型
2. **数据增强**: 包含旋转、平移、缩放、翻转、亮度调整等
3. **轻量级**: MobileNetV2模型参数量少，推理速度快
4. **两阶段训练**: 
   - 第一阶段：冻结基础模型，只训练分类层
   - 第二阶段（可选）：解冻部分层进行微调

## 注意事项

1. **数据量**: 建议每个类别至少100-200张图像
2. **数据质量**: 图像应该清晰，背景尽量简单
3. **类别平衡**: 尽量保持各类别样本数量平衡
4. **GPU**: 训练建议使用GPU加速，预测可以在CPU上运行
5. **内存**: 如果内存不足，可以减小batch_size

## 性能优化建议

1. **数据增强**: 如果数据量少，可以增加数据增强的强度
2. **学习率**: 迁移学习建议使用较小的学习率（0.0001-0.001）
3. **早停**: 训练脚本已包含早停机制，防止过拟合
4. **微调**: 如果第一阶段训练效果不理想，可以尝试微调

## 故障排除

### 导入错误

如果遇到导入错误，确保：
1. 已安装所有依赖：`pip install -r requirements.txt`
2. 在项目根目录下运行脚本
3. 使用 `python -m src.core.train` 而不是直接运行 `train.py`

### 内存不足

- 减小 `batch_size`
- 减小图像尺寸（修改 `IMG_SIZE`）
- 使用数据生成器而不是一次性加载所有数据

### 训练不收敛

- 检查数据质量和标注是否正确
- 尝试调整学习率
- 增加训练数据量
- 检查数据增强是否过度

