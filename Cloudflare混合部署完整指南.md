# Cloudflare Pages 混合部署完整指南 ☁️

## 📋 部署架构说明

这是一个**混合架构**方案，将前端和后端分离部署：

```
用户浏览器
    ↓
Cloudflare Pages（静态前端 HTML/CSS/JS）
    ↓ HTTPS API 调用
Vercel/Railway（Python 后端 + Flask + ML 模型）
```

**优势**：
- ✅ 前端享受 Cloudflare 全球 CDN 加速
- ✅ 后端保留完整 Python 功能（颜色分析、ML 模型、规则引擎）
- ✅ 两者都免费部署
- ✅ 自动 HTTPS 和 SSL
- ✅ 无需重写代码

---

## 🎯 部署前准备

### 必需条件

1. **GitHub 账号** - 代码已上传到 GitHub
2. **Cloudflare 账号** - 免费注册 [cloudflare.com](https://cloudflare.com)
3. **Vercel 账号** - 免费注册 [vercel.com](https://vercel.com)（推荐）
   或 **Railway 账号** - [railway.app](https://railway.app)

### 文件检查

确保以下文件存在：

**后端文件**：
- `vercel.json` - Vercel 配置
- `api/index.py` - Vercel API 入口
- `requirements.txt` - Python 依赖（包含 `flask-cors`）
- `src/web/app.py` - Flask 应用（已添加 CORS）

**前端文件**：
- `cloudflare-pages/index.html` - 主页面
- `cloudflare-pages/css/style.css` - 样式
- `cloudflare-pages/js/main.js` - JavaScript
- `cloudflare-pages/_headers` - Cloudflare 配置

---

## 🚀 部署步骤

### 第一步：部署后端到 Vercel

#### 1.1 登录 Vercel

访问 [vercel.com](https://vercel.com)，使用 GitHub 账号登录。

#### 1.2 导入项目

1. 点击 "Add New..." → "Project"
2. 选择你的 GitHub 仓库
3. Vercel 会自动检测到 `vercel.json` 配置

#### 1.3 配置项目

- **Framework Preset**: Other
- **Root Directory**: `./`（保持默认）
- **Build Command**: 留空
- **Output Directory**: 留空

#### 1.4 部署

1. 点击 "Deploy"
2. 等待 2-3 分钟部署完成
3. **记录你的 API 地址**，例如：
   ```
   https://your-project-name.vercel.app
   ```

#### 1.5 测试后端

在浏览器访问：
```
https://your-project-name.vercel.app/wardrobe
```

应该返回 JSON 数据（可能是空的历史记录）。

---

### 第二步：部署前端到 Cloudflare Pages

#### 2.1 登录 Cloudflare

访问 [dash.cloudflare.com](https://dash.cloudflare.com)，登录你的账号。

#### 2.2 创建 Pages 项目

1. 点击左侧菜单 "Workers & Pages"
2. 点击 "Create application"
3. 选择 "Pages" 标签
4. 点击 "Connect to Git"

#### 2.3 连接 GitHub

1. 授权 Cloudflare 访问你的 GitHub
2. 选择你的仓库
3. 点击 "Begin setup"

#### 2.4 配置构建设置

**重要配置**：

- **Project name**: 自定义名称（例如：outfit-simulator）
- **Production branch**: `main`（或你的主分支）
- **Framework preset**: `None`
- **Build command**: 留空（不需要构建）
- **Build output directory**: `cloudflare-pages`
- **Root directory (advanced)**: `/`

#### 2.5 部署

1. 点击 "Save and Deploy"
2. 等待 1-2 分钟部署完成
3. **记录你的前端地址**，例如：
   ```
   https://outfit-simulator.pages.dev
   ```

---

### 第三步：配置 API 连接

#### 3.1 打开前端网站

访问你的 Cloudflare Pages 地址（第二步记录的地址）。

#### 3.2 配置 API

1. 滚动到页面底部
2. 点击 "⚙️ API 配置" 展开配置面板
3. 在 "后端 API 地址" 输入框中输入你的 Vercel API 地址（第一步记录的地址）
   ```
   https://your-project-name.vercel.app
   ```
4. 点击 "保存" 按钮
5. 看到 "API 地址已保存" 提示

---

### 第四步：测试完整功能

#### 4.1 上传图片

1. 点击上传区域或拖拽图片
2. 选择一张服装图片（JPG/PNG，最大 16MB）
3. 等待上传完成

#### 4.2 选择场景和款式

1. 选择场景：休闲、工作、正式场合、运动
2. 选择款式（可选）：上衣、下装、鞋子

#### 4.3 开始分析

1. 点击 "开始分析" 按钮
2. 等待 3-5 秒分析完成
3. 查看分析结果：
   - 综合评分
   - 颜色分析
   - 规则评估
   - 改进建议

---

## ✅ 验证部署成功

### 检查清单

- [ ] 后端 Vercel 部署成功（访问 `/wardrobe` 返回 JSON）
- [ ] 前端 Cloudflare Pages 部署成功（页面正常显示）
- [ ] API 地址已配置并保存
- [ ] 可以成功上传图片
- [ ] 可以获得分析结果
- [ ] 颜色、评分、建议都正常显示

---

## 🔧 常见问题排查

### 问题 1：上传失败 "请先配置后端 API 地址"

**原因**：未配置 API 地址

**解决方案**：
1. 打开前端网站
2. 点击底部 "⚙️ API 配置"
3. 输入 Vercel API 地址
4. 点击保存

---

### 问题 2：上传失败 "Failed to fetch"

**原因**：CORS 配置问题或 API 地址错误

**解决方案**：

1. **检查 API 地址**：
   - 确保地址正确（复制粘贴，不要手打）
   - 确保没有多余的斜杠 `/`
   - 正确格式：`https://your-app.vercel.app`

2. **检查后端 CORS**：
   - 打开 `requirements.txt`，确认包含 `flask-cors>=4.0.0`
   - 打开 `src/web/app.py`，确认有以下代码：
     ```python
     from flask_cors import CORS
     CORS(app, resources={
         r"/api/*": {
             "origins": ["*"],
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type"]
         }
     })
     ```
   - 重新部署后端到 Vercel

3. **测试后端**：
   - 在浏览器打开：`https://your-app.vercel.app/wardrobe`
   - 应该看到 JSON 响应

---

### 问题 3：图片上传成功但无法显示

**原因**：图片 URL 路径问题

**解决方案**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 是否有错误
3. 检查 Network 标签，查看图片请求是否成功
4. 确保后端返回的图片 URL 正确

---

### 问题 4：分析失败 "分析失败: 500"

**原因**：后端处理错误

**解决方案**：
1. 检查 Vercel 部署日志：
   - 进入 Vercel 项目
   - 点击 "Deployments"
   - 点击最新部署
   - 查看 "Functions" 日志
2. 常见原因：
   - 缺少依赖包（检查 `requirements.txt`）
   - 模型文件缺失（正常，系统会使用规则引擎）
   - 代码错误（查看日志详情）

---

### 问题 5：Cloudflare Pages 构建失败

**原因**：构建配置错误

**解决方案**：
1. 进入 Cloudflare Pages 项目设置
2. 点击 "Settings" → "Builds & deployments"
3. 确认配置：
   - Build command: 留空
   - Build output directory: `cloudflare-pages`
   - Root directory: `/`
4. 点击 "Retry deployment"

---

## 🎨 自定义配置

### 修改前端样式

编辑 `cloudflare-pages/css/style.css`，修改颜色变量：

```css
:root {
    --bg-primary: #1a1a1a;      /* 主背景色 */
    --bg-secondary: #2d2d2d;    /* 次背景色 */
    --accent: #4a9eff;          /* 强调色 */
    --success: #4caf50;         /* 成功色 */
    --error: #f44336;           /* 错误色 */
}
```

提交到 GitHub，Cloudflare Pages 会自动重新部署。

---

### 添加自定义域名

#### Cloudflare Pages（前端）

1. 进入 Cloudflare Pages 项目
2. 点击 "Custom domains"
3. 点击 "Set up a custom domain"
4. 输入你的域名（例如：`outfit.yourdomain.com`）
5. 按照提示添加 DNS 记录

#### Vercel（后端）

1. 进入 Vercel 项目设置
2. 点击 "Domains"
3. 添加自定义域名（例如：`api.yourdomain.com`）
4. 更新前端 API 配置为新域名

---

## 📊 监控和日志

### Vercel 日志

1. 进入 Vercel 项目
2. 点击 "Deployments"
3. 点击最新部署
4. 查看 "Functions" 标签查看运行日志

### Cloudflare Pages 日志

1. 进入 Cloudflare Pages 项目
2. 点击 "Deployments"
3. 查看构建日志

### 浏览器调试

1. 按 F12 打开开发者工具
2. 查看 Console 标签（JavaScript 错误）
3. 查看 Network 标签（API 请求）

---

## 🔄 更新部署

### 更新后端

1. 修改代码并提交到 GitHub
2. Vercel 会自动检测并重新部署
3. 等待部署完成（1-2 分钟）

### 更新前端

1. 修改 `cloudflare-pages/` 下的文件
2. 提交到 GitHub
3. Cloudflare Pages 会自动重新部署
4. 等待部署完成（1-2 分钟）

---

## 💰 费用说明

### Vercel 免费额度

- ✅ 100GB 带宽/月
- ✅ 无限请求
- ✅ 自动 HTTPS
- ✅ 全球 CDN

**足够个人项目使用**

### Cloudflare Pages 免费额度

- ✅ 无限带宽
- ✅ 无限请求
- ✅ 500 次构建/月
- ✅ 全球 CDN

**完全免费**

---

## 🎉 部署完成

恭喜！你的穿搭分析系统已成功部署：

- **前端**：Cloudflare Pages（全球 CDN 加速）
- **后端**：Vercel（Python + Flask + ML）
- **功能**：完整保留所有功能
- **费用**：完全免费

**访问地址**：
- 前端：`https://your-project.pages.dev`
- 后端：`https://your-project.vercel.app`

---

## 📞 获取帮助

如果遇到问题：

1. **检查部署日志**（Vercel 和 Cloudflare）
2. **查看浏览器控制台**（F12）
3. **确认 API 配置正确**
4. **测试后端 API**（访问 `/wardrobe`）

---

**祝部署顺利！** 🚀
