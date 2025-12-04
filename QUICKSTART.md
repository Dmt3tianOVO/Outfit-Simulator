# 快速开始指南

## 项目概述

Outfit Simulator 是一个基于深度学习和计算机视觉的智能穿搭分析系统。通过上传服装图片，系统可以：

- 提取主色调并分析颜色搭配
- 识别服装款式（如需模型）
- 基于规则引擎评估穿搭搭配
- 提供智能搭配建议

## 环境要求

- Python 3.8+
- pip 或 conda

## 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行项目

#### 方式一：使用 run.py（简单）

```bash
python run.py
```

#### 方式二：使用 src/main.py（完整配置）

```bash
python -m src.main --host 0.0.0.0 --port 5000 --debug
```

### 4. 访问应用

打开浏览器访问：http://localhost:5000

## 功能说明

### 1. 图片上传
- 支持拖拽上传或点击选择
- 支持格式：PNG, JPG, JPEG, GIF, BMP
- 最大文件大小：16MB

### 2. 场景选择
- 休闲：日常穿搭
- 工作：职场穿搭
- 正式场合：正装穿搭
- 运动：运动穿搭

### 3. 分析功能

#### 颜色分析
- 提取图片中的主色调（最多5种）
- 分析颜色名称和色系（冷色/暖色/中性）
- 评估颜色搭配协调度

#### 款式识别（可选）
- 需要加载预训练模型
- 识别服装类型（T恤、衬衫、牛仔裤等）
- 显示识别置信度

#### 规则评估
- 三色原则：全身主色调不超过3种
- 上浅下深原则：上衣颜色比下装浅
- 禁忌颜色组合：避免互补色直接搭配
- 款式协调：正装配正装，休闲配休闲
- 场景适宜：根据场景选择合适风格

### 4. 历史记录
- 自动保存上传的图片
- 可快速重新分析历史图片

## 项目结构

```
OutfitSimulator/
├── src/
│   ├── core/              # 核心算法
│   │   ├── color_analyzer.py      # 颜色分析
│   │   ├── style_recognizer.py    # 款式识别
│   │   ├── rule_engine.py         # 规则引擎
│   │   └── model_utils.py         # 模型工具
│   ├── web/
│   │   └── app.py         # Flask应用
│   └── main.py            # 主程序入口
├── static/
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   ├── templates/         # HTML模板
│   └── images/            # 图片资源
├── tests/                 # 测试文件
├── config/                # 配置文件
├── requirements.txt       # 依赖列表
└── run.py                 # 快速启动脚本
```

## 命令行参数

使用 `src/main.py` 时支持以下参数：

```bash
python -m src.main [OPTIONS]

OPTIONS:
  --host HOST              服务器绑定地址（默认: 0.0.0.0）
  --port PORT              服务器端口（默认: 5000）
  --debug                  启用 Flask Debug 模式
  --model-path PATH        款式识别模型路径
  --log-level LEVEL        日志级别（DEBUG/INFO/WARNING/ERROR）
  --log-file PATH          日志文件路径
```

示例：

```bash
# 启用调试模式，监听本地8080端口
python -m src.main --host localhost --port 8080 --debug

# 指定模型路径和日志级别
python -m src.main --model-path models/my_model.h5 --log-level DEBUG
```

## 测试

### 运行颜色分析测试

```bash
python tests/test_color_analyzer.py
```

### 运行规则引擎测试

```bash
python tests/test_rule_engine.py
```

## 常见问题

### Q: 模型文件不存在怎么办？
A: 模型文件是可选的。系统会自动检测模型是否存在，如果不存在，将仅使用颜色分析和规则评估功能。

### Q: 如何添加自定义规则？
A: 在 `src/core/rule_engine.py` 中继承 `BaseRule` 类，实现 `evaluate` 方法，然后在 `RuleLibrary` 中注册。

### Q: 如何训练自己的款式识别模型？
A: 参考 `src/core/train.py` 中的训练脚本，准备数据集后运行训练。

### Q: 上传的图片存储在哪里？
A: 上传的图片存储在 `static/images/uploads/` 目录中。

## 开发指南

### 添加新的分析功能

1. 在 `src/core/` 中创建新的模块
2. 在 `src/web/app.py` 中添加新的路由
3. 在前端 `static/js/main.js` 中添加相应的处理逻辑

### 修改前端样式

编辑 `static/css/style.css` 文件。

### 修改前端逻辑

编辑 `static/js/main.js` 文件。

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
