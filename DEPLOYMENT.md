# Deployment Guide for Flash News AI

This guide will help you deploy both the frontend (React) and backend (Flask) to production.

## Prerequisites

- GitHub account
- API keys: Gemini API Key
- Accounts on hosting platforms (see options below)

## Deployment Options

### Option 1: Railway (Recommended - Easy Setup)

Railway can host both frontend and backend easily.

#### Backend Deployment (Railway)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `MODEL` folder as the root directory
   - Railway will auto-detect Python

3. **Configure Environment Variables**
   - Go to Variables tab
   - Add:
     ```
     GEMINI_API_KEY=your_actual_api_key
     FLASK_ENV=production
     FRONTEND_URL=https://your-frontend-url.vercel.app
     ```

4. **Deploy**
   - Railway will automatically deploy
   - Note the generated URL (e.g., `https://your-app.railway.app`)

#### Frontend Deployment (Vercel)

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Deploy Frontend**
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - Framework Preset: Vite
     - Root Directory: `./` (root)
   - Add Environment Variable:
     ```
     VITE_API_URL=https://your-backend.railway.app
     ```

3. **Deploy**
   - Click Deploy
   - Vercel will build and deploy your frontend

---

### Option 2: Render (Free Tier Available)

#### Backend Deployment (Render)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: `flash-news-backend`
     - Environment: Python 3
     - Build Command: `cd MODEL && pip install -r requirements.txt`
     - Start Command: `cd MODEL && gunicorn api:app --bind 0.0.0.0:$PORT`
     - Root Directory: `MODEL`

3. **Environment Variables**
   ```
   GEMINI_API_KEY=your_actual_api_key
   FLASK_ENV=production
   FRONTEND_URL=https://your-frontend.onrender.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Note the URL (e.g., `https://flash-news-backend.onrender.com`)

#### Frontend Deployment (Render)

1. **Create Static Site**
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Configure:
     - Build Command: `npm run build`
     - Publish Directory: `dist`
   - Add Environment Variable:
     ```
     VITE_API_URL=https://flash-news-backend.onrender.com
     ```

---

### Option 3: Heroku (Paid)

#### Backend Deployment (Heroku)

1. **Install Heroku CLI**
   ```bash
   # Download from heroku.com/cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   cd MODEL
   heroku create flash-news-backend
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_actual_api_key
   heroku config:set FLASK_ENV=production
   heroku config:set FRONTEND_URL=https://your-frontend.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

#### Frontend Deployment (Vercel/Netlify)
   - Same as Option 1

---

### Option 4: AWS/DigitalOcean (Advanced)

For AWS or DigitalOcean, you'll need to:
1. Set up a VPS/EC2 instance
2. Install Python, Node.js
3. Use PM2 or systemd for process management
4. Set up Nginx as reverse proxy
5. Configure SSL with Let's Encrypt

---

## Step-by-Step: Railway + Vercel (Easiest)

### Backend Setup (Railway)

1. **Prepare Repository**
   ```bash
   # Make sure MODEL/Procfile exists
   # Make sure MODEL/requirements.txt includes gunicorn
   ```

2. **Deploy to Railway**
   - Go to railway.app
   - New Project → Deploy from GitHub
   - Select your repo
   - Set Root Directory to `MODEL`
   - Add environment variables
   - Deploy

3. **Get Backend URL**
   - Copy the Railway URL (e.g., `https://flash-news-production.up.railway.app`)

### Frontend Setup (Vercel)

1. **Prepare Environment**
   ```bash
   # Create .env file in root
   VITE_API_URL=https://your-railway-backend-url.railway.app
   ```

2. **Deploy to Vercel**
   - Go to vercel.com
   - New Project → Import from GitHub
   - Add environment variable: `VITE_API_URL`
   - Deploy

3. **Update Backend CORS**
   - In Railway, update `FRONTEND_URL` to your Vercel URL

---

## Environment Variables

### Backend (.env in MODEL folder)
```
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=production
FRONTEND_URL=https://your-frontend-domain.com
PORT=5000  # Usually set by platform
```

### Frontend (.env in root)
```
VITE_API_URL=https://your-backend-domain.com
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible at `/api/health`
- [ ] Frontend can fetch articles from backend
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] Articles folder is accessible (for persistent storage)
- [ ] Background scheduler is running
- [ ] SSL/HTTPS is enabled

---

## Troubleshooting

### CORS Errors
- Make sure `FRONTEND_URL` in backend matches your frontend domain
- Check that CORS is configured in `api.py`

### API Not Found
- Verify `VITE_API_URL` in frontend matches backend URL
- Check backend logs for errors

### Articles Not Generating
- Verify `GEMINI_API_KEY` is set correctly
- Check backend logs for API errors
- Ensure background scheduler is running

### Storage Issues
- On some platforms, you may need to use external storage (S3, etc.)
- For persistent storage, consider using a database or cloud storage

---

## Cost Estimates

- **Railway**: Free tier available, then ~$5-20/month
- **Vercel**: Free tier for frontend
- **Render**: Free tier available
- **Heroku**: $7-25/month (no free tier)

---

## Recommended Setup

**Best for Free:**
- Backend: Railway or Render
- Frontend: Vercel or Netlify

**Best for Production:**
- Backend: Railway or AWS
- Frontend: Vercel
- Storage: AWS S3 or Railway volumes

---

## Need Help?

Check the logs:
- Railway: Dashboard → Deployments → View Logs
- Vercel: Dashboard → Project → Deployments → View Logs

