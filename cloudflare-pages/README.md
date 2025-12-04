# Cloudflare Pages 前端

这是穿搭分析系统的静态前端版本，专为 Cloudflare Pages 部署设计。

## 📁 文件结构

```
cloudflare-pages/
├── index.html          # 主页面
├── css/
│   └── style.css      # 样式文件
├── js/
│   └── main.js        # JavaScript 逻辑（调用后端 API）
├── _headers           # Cloudflare 安全配置
└── README.md          # 本文件
```

## 🚀 部署到 Cloudflare Pages

### 方法 1：通过 GitHub（推荐）

1. 将代码推送到 GitHub
2. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
3. 进入 "Workers & Pages"
4. 点击 "Create application" → "Pages" → "Connect to Git"
5. 选择你的 GitHub 仓库
6. 配置构建设置：
   - **Build output directory**: `cloudflare-pages`
   - **Build command**: 留空
7. 点击 "Save and Deploy"

### 方法 2：通过 Wrangler CLI

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署
wrangler pages publish cloudflare-pages --project-name=outfit-simulator
```

## ⚙️ 配置后端 API

部署完成后，需要配置后端 API 地址：

1. 打开部署好的网站
2. 滚动到页面底部
3. 点击 "⚙️ API 配置"
4. 输入后端 API 地址（例如：`https://your-api.vercel.app`）
5. 点击 "保存"

API 地址会保存在浏览器的 localStorage 中。

## 🔧 本地开发

由于这是纯静态前端，可以直接用浏览器打开：

```bash
# 使用 Python 简单服务器
cd cloudflare-pages
python -m http.server 8000

# 或使用 Node.js
npx serve .
```

然后访问 `http://localhost:8000`

**注意**：本地开发时需要先配置后端 API 地址。

## 📝 API 接口

前端调用以下后端 API：

### 1. 上传图片
```
POST /upload
Content-Type: multipart/form-data

Body: file (图片文件)

Response:
{
  "success": true,
  "filepath": "static/images/uploads/xxx.jpg",
  "url": "/images/uploads/xxx.jpg"
}
```

### 2. 分析穿搭
```
POST /analyze
Content-Type: application/json

Body:
{
  "filepath": "static/images/uploads/xxx.jpg",
  "context": { "type": "休闲" },
  "styles": {
    "top": "T恤",
    "bottom": "牛仔裤",
    "shoes": "运动鞋"
  }
}

Response:
{
  "success": true,
  "colors": [...],
  "color_evaluation": {...},
  "rule_evaluation": {...}
}
```

### 3. 获取历史记录
```
GET /wardrobe

Response:
{
  "success": true,
  "images": [...]
}
```

## 🎨 自定义样式

编辑 `css/style.css` 中的 CSS 变量：

```css
:root {
    --bg-primary: #1a1a1a;      /* 主背景色 */
    --bg-secondary: #2d2d2d;    /* 次背景色 */
    --accent: #4a9eff;          /* 强调色 */
    --success: #4caf50;         /* 成功色 */
    --error: #f44336;           /* 错误色 */
}
```

## 🔒 安全配置

`_headers` 文件配置了安全响应头：

```
Access-Control-Allow-Origin: *
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

## 📱 响应式设计

前端已适配移动设备：

- 桌面：最大宽度 800px
- 平板：自适应布局
- 手机：单列布局

## 🐛 故障排除

### 问题：无法上传图片

**检查**：
1. 是否配置了后端 API 地址
2. 后端是否正常运行
3. 浏览器控制台是否有 CORS 错误

### 问题：图片无法显示

**检查**：
1. 后端返回的图片 URL 是否正确
2. API 地址配置是否包含协议（https://）

### 问题：分析失败

**检查**：
1. 后端日志（Vercel/Railway）
2. 浏览器 Network 标签查看请求详情

## 📞 获取帮助

- 查看完整部署指南：`../Cloudflare混合部署完整指南.md`
- 查看后端配置：`../vercel.json`
- 查看 Python 后端：`../src/web/app.py`

---

**Happy Deploying!** 🚀
