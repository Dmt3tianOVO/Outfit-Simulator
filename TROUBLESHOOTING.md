# 故障排除指南

## 上传功能不工作

### 症状

- 点击上传区域没有反应
- 无法选择文件
- 上传按钮不可用

### 诊断步骤

#### 1. 检查浏览器控制台

```
按 F12 打开开发者工具
→ 选择 Console 标签
→ 查看是否有红色错误信息
```

**常见错误**:
- `Uncaught SyntaxError` - JavaScript语法错误
- `Cannot read property` - 元素不存在
- `CORS error` - 跨域问题

#### 2. 清除缓存

```
Ctrl + Shift + Delete  (打开清除缓存对话框)
→ 选择 "所有时间"
→ 勾选 "Cookie和其他网站数据"
→ 点击 "清除数据"
```

#### 3. 硬刷新页面

```
Ctrl + Shift + R  (Windows/Linux)
Cmd + Shift + R   (Mac)
```

#### 4. 检查应用状态

```bash
# 查看应用是否运行
curl http://localhost:5000

# 查看上传目录是否存在
ls -la static/images/uploads/

# 查看应用日志
tail -f src/logs/app.log
```

### 解决方案

#### 方案1: 重启应用

```bash
# 停止应用 (Ctrl+C)
# 重新启动
python run.py
```

#### 方案2: 检查JavaScript

```bash
# 验证JavaScript语法
node -c static/js/main.js

# 运行上传测试
python test_upload_fix.py
```

#### 方案3: 检查HTML

```bash
# 验证HTML中的必要元素
grep -n "id=\"uploadArea\"" static/templates/index.html
grep -n "id=\"fileInput\"" static/templates/index.html
grep -n "id=\"analyzeBtn\"" static/templates/index.html
```

---

## 分析功能不工作

### 症状

- 点击"开始分析"没有反应
- 分析按钮被禁用
- 显示加载状态但不完成

### 诊断步骤

#### 1. 检查是否上传了图片

```
上传区域应该显示图片预览
"开始分析"按钮应该是蓝色且可点击
```

#### 2. 检查网络请求

```
F12 → Network 标签
→ 点击"开始分析"
→ 查看 /analyze 请求
→ 检查响应状态和内容
```

#### 3. 查看应用日志

```bash
# 查看最近的错误
tail -50 src/logs/app.log
```

### 解决方案

#### 方案1: 检查模型文件

```bash
# 检查模型是否存在
ls -la models/

# 如果不存在，这是正常的
# 系统会自动降级为仅使用颜色和规则分析
```

#### 方案2: 检查颜色分析

```bash
# 运行颜色分析测试
python test_analyze.py
```

#### 方案3: 检查规则引擎

```bash
# 运行规则引擎测试
python test_context_rule.py
```

---

## 场景推荐不工作

### 症状

- 场景按钮不响应
- 款式选择器不更新
- 推荐信息不显示

### 诊断步骤

#### 1. 检查场景按钮

```
应该有4个按钮：休闲、工作、正式、运动
点击时应该高亮显示
```

#### 2. 检查款式选择器

```
应该有3个下拉菜单：上衣、下装、鞋子
选择场景时应该自动填充
```

#### 3. 检查API响应

```bash
# 测试推荐API
curl "http://localhost:5000/recommend?context=工作"

# 应该返回JSON格式的推荐数据
```

### 解决方案

#### 方案1: 检查JavaScript

```bash
# 验证场景选择器初始化
grep -n "initContextSelector" static/js/main.js

# 验证款式选择器初始化
grep -n "initStyleSelector" static/js/main.js
```

#### 方案2: 运行场景测试

```bash
# 测试所有场景
python test_scenarios.py

# 测试带款式信息的场景
python test_scenarios_with_styles.py
```

---

## 评分异常

### 症状

- 所有场景分数相同
- 分数不随场景变化
- 分数不随款式变化

### 原因

**没有提供款式信息** - 系统无法判断是否符合场景

### 解决方案

#### 方案1: 提供款式信息

```
1. 选择场景 → 自动填充款式建议
2. 修改款式（如需要）
3. 上传图片
4. 点击分析 → 分数会根据场景变化
```

#### 方案2: 理解评分系统

```
查看 SCORING_EXPLANATION.md 了解详细信息
```

#### 方案3: 运行诊断测试

```bash
# 测试场景规则
python test_context_rule.py

# 测试带款式信息的场景
python test_scenarios_with_styles.py
```

---

## 性能问题

### 症状

- 应用响应缓慢
- 分析需要很长时间
- 页面卡顿

### 诊断步骤

#### 1. 检查系统资源

```bash
# 查看内存使用
ps aux | grep python

# 查看磁盘空间
df -h
```

#### 2. 检查应用日志

```bash
# 查看是否有错误
grep "ERROR" src/logs/app.log

# 查看分析耗时
grep "分析" src/logs/app.log
```

### 解决方案

#### 方案1: 优化图片

```
- 使用较小的图片（< 5MB）
- 使用常见格式（JPG, PNG）
- 避免过大的分辨率
```

#### 方案2: 重启应用

```bash
# 停止应用
Ctrl+C

# 重新启动
python run.py
```

#### 方案3: 检查模型

```bash
# 如果加载了模型，可能会很慢
# 查看是否有模型文件
ls -la models/

# 如果不需要款式识别，可以删除模型
```

---

## 数据库/存储问题

### 症状

- 上传的图片丢失
- 历史记录不显示
- 无法保存分析结果

### 诊断步骤

#### 1. 检查上传目录

```bash
# 查看上传目录
ls -la static/images/uploads/

# 查看目录权限
stat static/images/uploads/
```

#### 2. 检查磁盘空间

```bash
# 查看磁盘使用情况
df -h

# 查看上传目录大小
du -sh static/images/uploads/
```

### 解决方案

#### 方案1: 创建目录

```bash
# 如果目录不存在，创建它
mkdir -p static/images/uploads/

# 设置权限
chmod 755 static/images/uploads/
```

#### 方案2: 清理空间

```bash
# 删除旧的上传文件
rm -rf static/images/uploads/*

# 清理日志
rm -rf src/logs/*
```

---

## 获取帮助

### 收集诊断信息

```bash
# 生成诊断报告
python verify_project.py > diagnosis.txt

# 查看应用日志
tail -100 src/logs/app.log > logs.txt

# 查看系统信息
python -c "import sys; print(sys.version)" > system_info.txt
```

### 常用命令

```bash
# 运行所有测试
python test_upload_fix.py
python test_analyze.py
python test_scenarios.py
python test_context_rule.py

# 验证项目完整性
python verify_project.py

# 启动应用
python run.py
```

### 查看文档

- `README.md` - 项目说明
- `QUICKSTART.md` - 快速开始
- `SCORING_EXPLANATION.md` - 评分系统
- `SCENARIOS_GUIDE.md` - 场景指南
- `UPLOAD_FIX_GUIDE.md` - 上传修复

---

## 常见问题

### Q: 应用无法启动

A: 
1. 检查Python版本 (需要 3.8+)
2. 检查依赖是否安装 (`pip install -r requirements.txt`)
3. 检查端口是否被占用 (`lsof -i :5000`)

### Q: 模型加载失败

A: 这是正常的，系统会自动降级。如需款式识别，需要训练模型。

### Q: 上传的图片无法显示

A:
1. 检查文件格式是否支持
2. 检查文件大小是否超过16MB
3. 检查上传目录权限

### Q: 分析结果不准确

A:
1. 提供款式信息以获得更准确的结果
2. 使用清晰的服装图片
3. 确保图片包含完整的服装

---

**最后更新**: 2025年12月4日  
**版本**: 1.0.0
