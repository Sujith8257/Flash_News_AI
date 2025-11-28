# Quick Deployment Guide

## Fastest Way: Railway (Backend) + Vercel (Frontend)

### Step 1: Deploy Backend to Railway (5 minutes)

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. **Important**: Set Root Directory to `MODEL`
5. Add Environment Variables:
   - `GEMINI_API_KEY` = your Gemini API key
   - `FLASK_ENV` = `production`
   - `FRONTEND_URL` = (you'll add this after frontend is deployed)
6. Railway will auto-deploy
7. Copy your Railway URL (e.g., `https://flash-news.up.railway.app`)

### Step 2: Deploy Frontend to Vercel (3 minutes)

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "New Project" → Import from GitHub
3. Select your repository
4. Add Environment Variable:
   - `VITE_API_URL` = your Railway backend URL (from Step 1)
5. Click Deploy
6. Copy your Vercel URL (e.g., `https://flash-news-ai.vercel.app`)

### Step 3: Update Backend CORS

1. Go back to Railway
2. Update `FRONTEND_URL` environment variable to your Vercel URL
3. Railway will automatically redeploy

### Done! 🎉

Your app is now live at your Vercel URL!

---

## Testing Your Deployment

1. **Backend Health Check**: Visit `https://your-backend.railway.app/api/health`
   - Should return: `{"status": "healthy"}`

2. **Frontend**: Visit your Vercel URL
   - Should load the homepage
   - Feed page should show articles (may take a few minutes for first article)

3. **Check Logs**:
   - Railway: Dashboard → Your Project → View Logs
   - Vercel: Dashboard → Your Project → Deployments → View Logs

---

## Troubleshooting

**CORS Error?**
- Make sure `FRONTEND_URL` in Railway matches your Vercel URL exactly
- Check that CORS is configured in `api.py`

**Articles Not Loading?**
- Check Railway logs for errors
- Verify `GEMINI_API_KEY` is set correctly
- Wait a few minutes for the first article to generate

**Build Fails?**
- Check that all dependencies are in `requirements.txt`
- Verify Python version (3.11+)
- Check build logs for specific errors

---

## Cost

- **Railway**: Free tier (500 hours/month), then ~$5/month
- **Vercel**: Free tier (unlimited for personal projects)

**Total: FREE for small projects!**

