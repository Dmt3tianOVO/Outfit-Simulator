# Web应用使用说明

## 启动应用

### 方法1：直接运行

```bash
python src/web/app.py
```

### 方法2：使用Flask命令

```bash
export FLASK_APP=src/web/app.py
flask run
```

### 方法3：使用Python模块方式

```bash
python -m flask --app src/web/app run
```

应用将在 `http://localhost:5000` 启动。

## 功能说明

### 1. 上传分析 (`/`)
- 支持拖拽或点击上传图片
- 支持PNG、JPG、JPEG、GIF、BMP格式
- 最大文件大小：16MB
- 可选择场景（正式场合、商务、工作、休闲、运动、聚会）

### 2. 图片上传 (`POST /upload`)
- 接收图片文件
- 保存到 `static/images/uploads/` 目录
- 返回文件路径和URL

### 3. 穿搭分析 (`POST /analyze`)
- 调用core模块进行颜色提取、款式识别、规则评估
- 返回JSON格式的分析结果
- 包含颜色分析、款式识别、规则评估等信息

### 4. 场景推荐 (`GET /recommend`)
- 根据场景类型提供穿搭建议
- 支持场景：正式场合、商务、工作、休闲、运动、聚会
- 返回颜色建议、款式建议和搭配技巧

### 5. 虚拟衣柜 (`GET /wardrobe`)
- 显示所有上传的图片
- 点击图片可以重新分析
- 按上传时间排序

## API接口

### POST /upload
上传图片文件

**请求：**
- Content-Type: multipart/form-data
- 参数：`file` (图片文件)

**响应：**
```json
{
    "success": true,
    "filepath": "static/images/uploads/20231203_120000_image.jpg",
    "filename": "20231203_120000_image.jpg",
    "url": "/images/uploads/20231203_120000_image.jpg"
}
```

### POST /analyze
分析穿搭

**请求：**
```json
{
    "filepath": "static/images/uploads/image.jpg",
    "context": {
        "type": "休闲"
    }
}
```

**响应：**
```json
{
    "success": true,
    "image_url": "/images/uploads/image.jpg",
    "colors": [
        {
            "rgb": [255, 0, 0],
            "percentage": 45.2,
            "name": "红",
            "tone": "暖色"
        }
    ],
    "color_evaluation": {
        "score": 85.5,
        "suggestions": ["建议..."]
    },
    "style_predictions": [
        {
            "class": "T恤",
            "confidence": 0.95
        }
    ],
    "rule_evaluation": {
        "score": 90.0,
        "passed": true,
        "results": [...],
        "suggestions": [...]
    }
}
```

### GET /recommend?context=休闲
获取场景推荐

**响应：**
```json
{
    "success": true,
    "context": "休闲",
    "recommendations": ["建议1", "建议2"],
    "color_suggestions": ["白", "蓝", "灰"],
    "style_suggestions": {
        "top": "T恤",
        "bottom": "牛仔裤",
        "shoes": "运动鞋"
    }
}
```

### GET /wardrobe
获取虚拟衣柜

**响应：**
```json
{
    "success": true,
    "images": [
        {
            "filename": "image.jpg",
            "url": "/images/uploads/image.jpg",
            "uploaded_at": "2023-12-03T12:00:00",
            "size": 102400
        }
    ],
    "count": 10
}
```

## 配置说明

### 模型路径
默认款式识别模型路径：`models/best_model.h5`
如果模型不存在，款式识别功能将被禁用，但颜色分析和规则评估仍可使用。

### 上传目录
默认上传目录：`static/images/uploads/`
确保该目录存在且有写入权限。

### 文件大小限制
默认最大文件大小：16MB
可在 `app.py` 中修改 `MAX_CONTENT_LENGTH` 配置。

## 错误处理

应用包含完整的错误处理：
- 文件格式错误
- 文件大小超限
- 文件不存在
- 分析失败
- 服务器错误

所有错误都会返回JSON格式的错误信息。

## 前端功能

- **响应式设计**：支持桌面和移动设备
- **拖拽上传**：支持拖拽文件上传
- **实时反馈**：上传和分析过程有加载提示
- **结果可视化**：颜色展示、评分圆圈、建议列表等
- **标签页切换**：上传分析、虚拟衣柜、场景推荐

## 注意事项

1. 首次运行需要确保上传目录存在
2. 如果使用款式识别功能，需要先训练模型
3. 建议在生产环境中使用WSGI服务器（如Gunicorn）
4. 可以配置环境变量来修改默认设置

