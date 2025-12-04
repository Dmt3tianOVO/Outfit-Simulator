# 🚀 Quick Deployment Guide

## 5-Minute Deployment Checklist

### ✅ Prerequisites
- [ ] Code pushed to GitHub
- [ ] Vercel account (free)
- [ ] Cloudflare account (free)

---

## 📝 Step-by-Step

### 1️⃣ Deploy Backend (3 min)

```
1. Go to: https://vercel.com
2. Login with GitHub
3. Click "Add New..." → "Project"
4. Select your repository
5. Click "Deploy"
6. Copy API URL: https://your-app.vercel.app
```

**Test**: Visit `https://your-app.vercel.app/wardrobe`
Should return JSON (may be empty array)

---

### 2️⃣ Deploy Frontend (2 min)

```
1. Go to: https://dash.cloudflare.com
2. Click "Workers & Pages"
3. Click "Create application" → "Pages"
4. Connect GitHub, select repository
5. Configure:
   - Build output directory: cloudflare-pages
   - Build command: (leave empty)
6. Click "Save and Deploy"
```

---

### 3️⃣ Configure API (1 min)

```
1. Open your Cloudflare Pages URL
2. Scroll to bottom
3. Click "⚙️ API 配置"
4. Enter Vercel API URL
5. Click "保存"
```

---

### 4️⃣ Test (1 min)

```
1. Upload an image
2. Select scene and style
3. Click "开始分析"
4. View results
```

---

## 🎯 Architecture

```
Browser → Cloudflare Pages (Frontend)
              ↓ API calls
          Vercel (Backend)
```

---

## 🔧 Troubleshooting

### Upload fails?
- Check API URL is configured
- Check backend is deployed
- Open browser console (F12)

### CORS error?
- Verify `flask-cors` in requirements.txt
- Redeploy backend

### Image not showing?
- Check browser Network tab
- Verify API URL format

---

## 📚 Full Documentation

- **Complete Guide**: `Cloudflare混合部署完整指南.md`
- **Setup Summary**: `部署完成说明.md`
- **Frontend Docs**: `cloudflare-pages/README.md`

---

## 💰 Cost

- Vercel: **FREE** (100GB/month)
- Cloudflare Pages: **FREE** (unlimited)

**Total: $0**

---

## 🎉 Done!

Your outfit analysis system is now live on:
- Frontend: `https://your-project.pages.dev`
- Backend: `https://your-project.vercel.app`

**Enjoy!** 🚀
