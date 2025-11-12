# 🚀 Deployment Guide - Render.com

## Quick Deploy to Render

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub** (including the `render.yaml` file)

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**:
   - In Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add: `HF_TOKEN` = your Hugging Face token
   - `PORT` is already set to 10000 in render.yaml

4. **Deploy**:
   - Render will automatically build and deploy
   - Your API will be available at: `https://your-service-name.onrender.com`

### Option 2: Manual Configuration

If you prefer manual setup:

1. **Create New Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure Build Settings**:
   - **Name**: `logo-generator-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Region**: Choose your preferred region

3. **Environment Variables**:
   - Add `HF_TOKEN` with your Hugging Face API token
   - Add `PORT` = `10000` (Render provides this automatically)

4. **Deploy**: Click "Create Web Service"

## Environment Variables Required

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | Hugging Face API Token | ✅ Yes |
| `PORT` | Server port (auto-set by Render) | ✅ Yes |

## Post-Deployment

### Test Your API

Once deployed, test your endpoints:

```bash
# Health check
curl https://your-service-name.onrender.com/health

# Generate logo
curl -X POST https://your-service-name.onrender.com/api/generate_logo \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Modern tech startup",
    "sizes": [256, 512]
  }'
```

### Access API Documentation

- **Swagger UI**: `https://your-service-name.onrender.com/docs`
- **ReDoc**: `https://your-service-name.onrender.com/redoc`

## Troubleshooting

### Common Issues

1. **"No such file or directory" error**:
   - ✅ Fixed by using `render.yaml` with correct `startCommand`
   - Make sure `run.py` is in the root directory

2. **Port binding issues**:
   - Render automatically sets `PORT` environment variable
   - Our app reads from `Config.PORT` which uses `os.getenv("PORT", 8000)`

3. **Module import errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check build logs for installation errors

4. **HF_TOKEN not found**:
   - Add `HF_TOKEN` in Render's Environment Variables
   - Don't commit `.env` file to git

### View Logs

- Go to your service in Render Dashboard
- Click "Logs" tab to see real-time logs
- Check for startup messages and errors

## Performance Tips

1. **Free Tier Limitations**:
   - Free services spin down after 15 minutes of inactivity
   - First request after spin-down will be slow (~30 seconds)
   - Consider upgrading to paid tier for production

2. **Cold Start Optimization**:
   - The app is already optimized for fast startup
   - Model initialization happens on first request

3. **Monitoring**:
   - Use Render's built-in metrics
   - Monitor response times and error rates

## Updating Your Deployment

### Automatic Deploys

Enable auto-deploy in Render:
- Go to Settings → "Auto-Deploy"
- Enable for your main branch
- Every push will trigger a new deployment

### Manual Deploy

- Go to your service
- Click "Manual Deploy" → "Deploy latest commit"

## Security Checklist

- ✅ Never commit `.env` file
- ✅ Use environment variables for secrets
- ✅ Keep `HF_TOKEN` secure
- ✅ Configure CORS appropriately for production
- ✅ Monitor API usage and costs

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Hugging Face Documentation](https://huggingface.co/docs)

