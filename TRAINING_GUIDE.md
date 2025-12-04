# 模型训练完整指南

本指南将教你如何训练一个真实的服装款式识别模型并投入使用。

---

## 📋 目录

1. [准备工作](#准备工作)
2. [数据准备](#数据准备)
3. [开始训练](#开始训练)
4. [使用训练好的模型](#使用训练好的模型)
5. [常见问题](#常见问题)

---

## 准备工作

### 1. 确认环境

确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 了解模型架构

- **基础模型**: MobileNetV2（预训练于ImageNet）
- **训练方式**: 迁移学习
- **支持类别**: 8类（可自定义）
  - T恤、衬衫、卫衣、外套
  - 牛仔裤、休闲裤
  - 运动鞋、皮鞋

---

## 数据准备

### 方案1：使用公开数据集（推荐）

#### Fashion-MNIST（入门级）
```bash
# 下载Fashion-MNIST数据集
# 这是一个简单的服装数据集，适合快速测试
```

#### DeepFashion（专业级）
- 网址: http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html
- 包含大量真实服装图片
- 需要申请下载权限

#### Kaggle服装数据集
- Fashion Product Images: https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset
- 包含44,000+服装图片

### 方案2：自己收集数据

#### 数据目录结构

训练数据需要按以下结构组织：

```
data/
├── train/                    # 训练集
│   ├── T恤/                 # 类别1
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   ├── 衬衫/                # 类别2
│   │   ├── img001.jpg
│   │   └── ...
│   ├── 卫衣/
│   ├── 外套/
│   ├── 牛仔裤/
│   ├── 休闲裤/
│   ├── 运动鞋/
│   └── 皮鞋/
│
└── validation/               # 验证集（结构同上）
    ├── T恤/
    ├── 衬衫/
    └── ...
```

#### 数据要求

- **图片格式**: JPG、PNG
- **图片数量**: 每类至少100张（越多越好）
- **训练/验证比例**: 80:20 或 70:30
- **图片质量**: 清晰、主体明显
- **背景**: 尽量简洁，避免复杂背景

#### 数据收集方法

1. **网络爬虫**（注意版权）
   ```python
   # 示例：使用Google Images下载
   # 可以使用 google-images-download 等工具
   ```

2. **手动收集**
   - 从电商网站截图
   - 拍摄实物照片
   - 使用免费图库

3. **数据增强**（自动生成更多样本）
   - 系统会自动进行数据增强
   - 包括旋转、翻转、缩放等

---

## 开始训练

### 快速开始脚本

我为你创建了一个简化的训练脚本，让我们创建它：

```bash
# 使用默认参数训练
python train_easy.py
```

### 标准训练命令

```bash
# 基础训练（50轮）
python src/core/train.py \
    --train_dir data/train \
    --validation_dir data/validation \
    --epochs 50 \
    --batch_size 32

# 高级训练（包含微调）
python src/core/train.py \
    --train_dir data/train \
    --validation_dir data/validation \
    --epochs 50 \
    --batch_size 32 \
    --fine_tune \
    --fine_tune_epochs 10
```

### 训练参数说明

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|--------|--------|
| `--train_dir` | 训练数据目录 | 必填 | `data/train` |
| `--validation_dir` | 验证数据目录 | 必填 | `data/validation` |
| `--model_dir` | 模型保存目录 | `models` | `models` |
| `--batch_size` | 批次大小 | 32 | 16-64 |
| `--epochs` | 训练轮数 | 50 | 30-100 |
| `--learning_rate` | 学习率 | 0.0001 | 0.0001 |
| `--fine_tune` | 是否微调 | False | True（数据充足时）|
| `--fine_tune_epochs` | 微调轮数 | 10 | 10-20 |

### 训练过程

训练时会看到类似输出：

```
============================================================
开始训练服装款式识别模型
============================================================

创建数据生成器...
训练样本数: 800
验证样本数: 200
类别数: 8

创建模型...
模型参数总数: 2,257,984

============================================================
第一阶段训练：冻结基础模型（迁移学习）
============================================================

Epoch 1/50
25/25 [==============================] - 45s 2s/step
    loss: 1.8234 - accuracy: 0.3250 
    val_loss: 1.5432 - val_accuracy: 0.4500

Epoch 2/50
25/25 [==============================] - 42s 2s/step
    loss: 1.4567 - accuracy: 0.4875
    val_loss: 1.2345 - val_accuracy: 0.5750

...

训练完成！
最佳验证准确率: 0.8750
```

### 训练时间估计

- **CPU训练**: 2-5小时（50轮）
- **GPU训练**: 20-60分钟（50轮）

---

## 使用训练好的模型

### 1. 模型文件位置

训练完成后，会生成以下文件：

```
models/
├── best_model.h5              # 最佳模型（自动使用）
├── outfit_classifier_final.h5 # 最终模型
├── training_log.csv           # 训练日志
└── training_history.png       # 训练曲线图
```

### 2. 自动使用

系统会自动使用 `models/best_model.h5`，无需额外配置！

只需重启应用：

```bash
python run.py
```

### 3. 测试模型

创建测试脚本：

```python
from src.core.style_recognizer import StyleRecognizer

# 加载模型
recognizer = StyleRecognizer('models/best_model.h5')

# 预测单张图片
results = recognizer.predict('test_image.jpg', top_k=3)

# 查看结果
for i, result in enumerate(results, 1):
    print(f"{i}. {result['class']}: {result['confidence']:.2%}")
```

### 4. 评估模型性能

```python
# 在验证集上评估
python -c "
from src.core.model_utils import load_model, get_data_generators
import tensorflow as tf

model = load_model('models/best_model.h5')
_, val_gen = get_data_generators('data/train', 'data/validation')
loss, accuracy = model.evaluate(val_gen)
print(f'验证准确率: {accuracy:.2%}')
"
```

---

## 常见问题

### Q1: 没有足够的数据怎么办？

**方案1**: 使用数据增强（已内置）
- 系统会自动旋转、翻转、缩放图片
- 可以将100张图片扩展到数千张

**方案2**: 使用预训练模型
- 当前的虚拟模型已经可以使用
- 系统主要依赖颜色分析和规则引擎

**方案3**: 下载公开数据集
- Fashion-MNIST（简单）
- DeepFashion（专业）
- Kaggle数据集

### Q2: 训练太慢怎么办？

**减少训练时间**:
```bash
# 减少轮数
--epochs 20

# 减少批次大小
--batch_size 16

# 不进行微调
# 不加 --fine_tune 参数
```

**使用GPU加速**:
- 如果有NVIDIA显卡，安装 `tensorflow-gpu`
- 训练速度可提升5-10倍

### Q3: 准确率不高怎么办？

**提升准确率的方法**:

1. **增加数据量**
   - 每类至少200-500张图片
   - 数据越多，效果越好

2. **提高数据质量**
   - 图片清晰、主体明显
   - 避免复杂背景
   - 类别标注准确

3. **调整训练参数**
   ```bash
   # 增加训练轮数
   --epochs 100
   
   # 启用微调
   --fine_tune --fine_tune_epochs 20
   ```

4. **数据平衡**
   - 确保每个类别的图片数量相近
   - 避免某些类别过多或过少

### Q4: 如何添加新的服装类别？

修改 `src/core/model_utils.py` 中的类别定义：

```python
# 原来的8类
CLASS_NAMES = ['T恤', '衬衫', '卫衣', '外套', '牛仔裤', '休闲裤', '运动鞋', '皮鞋']

# 修改为你需要的类别
CLASS_NAMES = ['T恤', '衬衫', '连衣裙', '短裤', '运动鞋']
NUM_CLASSES = len(CLASS_NAMES)
```

然后按新类别组织数据并重新训练。

### Q5: 训练出错怎么办？

**常见错误及解决方案**:

1. **找不到数据目录**
   ```
   错误: 训练数据目录不存在
   解决: 检查路径是否正确，确保目录存在
   ```

2. **内存不足**
   ```
   错误: OOM (Out of Memory)
   解决: 减小 batch_size，如 --batch_size 16
   ```

3. **类别不匹配**
   ```
   错误: 类别数量不匹配
   解决: 确保数据目录中的类别与 CLASS_NAMES 一致
   ```

---

## 完整示例：从零开始

### 步骤1: 准备数据

```bash
# 创建数据目录
mkdir -p data/train data/validation

# 为每个类别创建子目录
cd data/train
mkdir T恤 衬衫 卫衣 外套 牛仔裤 休闲裤 运动鞋 皮鞋

cd ../validation
mkdir T恤 衬衫 卫衣 外套 牛仔裤 休闲裤 运动鞋 皮鞋
```

### 步骤2: 收集图片

将图片放入对应的类别文件夹：
- 训练集：每类80-100张
- 验证集：每类20-30张

### 步骤3: 开始训练

```bash
# 返回项目根目录
cd ../..

# 开始训练
python src/core/train.py \
    --train_dir data/train \
    --validation_dir data/validation \
    --epochs 30 \
    --batch_size 32
```

### 步骤4: 等待训练完成

训练需要1-3小时（取决于数据量和硬件）

### 步骤5: 使用模型

```bash
# 启动应用
python run.py

# 访问 http://localhost:5000
# 上传图片测试效果
```

---

## 进阶技巧

### 1. 监控训练过程

查看训练日志：
```bash
# 实时查看
tail -f models/training_log.csv

# 查看训练曲线
# 打开 models/training_history.png
```

### 2. 继续训练（从检查点恢复）

```python
from src.core.model_utils import load_model

# 加载已有模型
model = load_model('models/best_model.h5')

# 继续训练
# 使用相同的训练命令即可
```

### 3. 模型对比

```bash
# 训练多个版本
python src/core/train.py ... --model_dir models/v1
python src/core/train.py ... --model_dir models/v2

# 对比效果，选择最佳版本
```

---

## 总结

✅ **准备数据** - 按类别组织图片  
✅ **开始训练** - 运行训练脚本  
✅ **等待完成** - 1-3小时  
✅ **自动使用** - 系统自动加载 best_model.h5  
✅ **测试效果** - 上传图片验证  

**记住**: 即使没有训练模型，系统的颜色分析和规则引擎也能提供很好的穿搭建议！

---

## 需要帮助？

- 查看 `MODEL_SETUP_GUIDE.md` - 模型设置指南
- 查看 `src/core/README_STYLE_RECOGNIZER.md` - 款式识别说明
- 运行 `python src/core/train.py --help` - 查看所有参数

祝训练顺利！🎉
