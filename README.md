# 穿搭分析系统 (Outfit Simulator) 👔

基于 AI 的智能穿搭分析和推荐系统，帮助用户进行服装搭配评估。

---

## ✨ 功能特点

- 🎨 **颜色分析**：提取主色调、颜色分类、色系识别
- 📏 **规则引擎**：三色原则、上浅下深、禁忌搭配等专业规则
- 🎭 **场景推荐**：休闲、工作、正式场合、运动等场景建议
- 📊 **评分系统**：综合评分（0-100分）和详细改进建议
- 🖼️ **图片上传**：支持拖拽上传和点击上传
- 📱 **响应式设计**：支持桌面和移动设备

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python run.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:5000

---

## 📁 项目结构

```
Outfit Simulator/
├── src/                    # 源代码
│   ├── core/              # 核心算法
│   │   ├── color_analyzer.py      # 颜色分析
│   │   ├── rule_engine.py         # 规则引擎
│   │   ├── style_recognizer.py    # 款式识别
│   │   └── model_utils.py         # 模型工具
│   ├── web/               # Web 应用
│   │   └── app.py         # Flask 应用
│   └── main.py            # 主程序入口
├── static/                # 静态资源
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript 文件
│   ├── images/           # 图片资源
│   └── templates/        # HTML 模板
├── models/               # 模型文件
│   └── best_model.h5     # 训练好的模型
├── config/               # 配置文件
├── tests/                # 测试文件
├── api/                  # API 入口（用于部署）
├── run.py                # 快速启动脚本
├── requirements.txt      # 依赖列表
└── README.md            # 项目说明
```

---

## 🎯 核心功能

### 颜色分析

- K-means 聚类提取主色调
- 识别 20+ 种颜色
- 冷色/暖色/中性色分类
- 颜色搭配协调度评估

### 规则引擎

- **三色原则**：主色调不超过3种
- **上浅下深**：上衣浅色，下装深色
- **禁忌搭配**：避免冲突色组合
- **款式协调**：服装款式匹配度
- **场景适宜**：不同场景的穿搭建议

### 场景推荐

- 🏃 **休闲**：舒适、轻松的搭配
- 💼 **工作**：专业、得体的着装
- 🎩 **正式场合**：庄重、优雅的装扮
- ⚽ **运动**：活力、实用的运动装

---

## 🛠️ 技术栈

### 后端

- **Python 3.8+**
- **Flask 2.3+** - Web 框架
- **TensorFlow 2.13+** - 深度学习
- **OpenCV 4.8+** - 图像处理
- **scikit-learn 1.3+** - 机器学习

### 前端

- **HTML5 / CSS3**
- **JavaScript (ES6+)**
- **响应式设计**

---

## 📚 文档

- **QUICKSTART.md** - 快速开始指南
- **TRAINING_GUIDE.md** - 模型训练指南
- **MODEL_SETUP_GUIDE.md** - 模型设置说明
- **快速部署指南.md** - 部署到云平台
- **TROUBLESHOOTING.md** - 常见问题解决

---

## 🌐 部署

### 推荐平台

1. **Railway** - 最简单，1分钟部署
2. **Vercel** - 最快，无冷启动
3. **Render** - 完全免费

详细步骤请查看：**快速部署指南.md**

### 快速部署

```bash
# 1. 推送到 GitHub
git init
git add .
git commit -m "部署"
git push

# 2. 访问 Railway
# https://railway.app
# 导入仓库，自动部署
```

---

## 🎓 模型训练（可选）

系统已包含预训练模型，可直接使用。如需训练自己的模型：

```bash
# 简化训练
python train_easy.py

# 完整训练
python src/core/train.py --train_dir data/train --validation_dir data/validation
```

详细说明请查看：**TRAINING_GUIDE.md**

---

## 🔧 配置

### 应用配置

编辑 `config/config.json`：

```json
{
  "app": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "model": {
    "path": "models/best_model.h5"
  },
  "upload": {
    "max_size": 16777216,
    "allowed_extensions": ["png", "jpg", "jpeg", "gif", "bmp"]
  }
}
```

---

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 测试颜色分析
python tests/test_color_analyzer.py

# 测试规则引擎
python tests/test_rule_engine.py
```

---

## 📊 系统要求

### 最低要求

- Python 3.8+
- 2GB RAM
- 1GB 磁盘空间

### 推荐配置

- Python 3.10+
- 4GB RAM
- 2GB 磁盘空间
- GPU（可选，用于模型训练）

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- TensorFlow - 深度学习框架
- Flask - Web 框架
- OpenCV - 图像处理
- scikit-learn - 机器学习

---

## 📞 联系方式

如有问题或建议，请：
- 提交 Issue
- 查看文档
- 参考 TROUBLESHOOTING.md

---

## 🎉 开始使用

```bash
# 克隆项目
git clone https://github.com/你的用户名/outfit-simulator.git

# 进入目录
cd outfit-simulator

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py

# 访问 http://localhost:5000
```

**祝使用愉快！** 🚀
