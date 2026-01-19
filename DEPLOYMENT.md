# Deploying to Render.com

This guide walks you through deploying the Cheating Detection application to Render.com using their free tier.

## Prerequisites
- GitHub account with this repository
- Render.com account (free - sign up at [render.com](https://render.com))

## Quick Start (Using Blueprint)

### 1. Push render.yaml to GitHub
The `render.yaml` file in the root directory defines all services. Make sure it's committed and pushed.

### 2. Deploy via Render Dashboard

1. **Log in to Render** → [dashboard.render.com](https://dashboard.render.com)

2. **Create New Blueprint Instance:**
   - Click "New" → "Blueprint"
   - Connect your GitHub account if not already connected
   - Select your repository: `Dragonballsuper-1995/Cryptography-Research-Paper`
   - Render will detect `render.yaml` automatically

3. **Configure Environment Variables:**
   Render will create services from the blueprint. You need to set one variable:
   
   - **Backend service** → Environment:
     - `CORS_ORIGINS` → Set to your frontend URL (Render will provide this after frontend deploys)
     - Format: `https://cheating-detector-frontend.onrender.com`

4. **Click "Apply"**
   - Render creates: Database, Backend API, Frontend
   - Initial deployment takes ~5-10 minutes

### 3. Post-Deployment Configuration

Once deployed, update the frontend URL:

1. Go to **Backend service** → Environment
2. Update `CORS_ORIGINS` with actual frontend URL
3. Save and redeploy

## Services Created

| Service | Type | URL |
|---------|------|-----|
| Database | PostgreSQL | Internal only |
| Backend API | Web Service | `https://cheating-detector-backend.onrender.com` |
| Frontend | Web Service | `https://cheating-detector-frontend.onrender.com` |

## Environment Variables Reference

### Backend
- `DATABASE_URL` - Auto-configured from database
- `SECRET_KEY` - Auto-generated
- `CORS_ORIGINS` - **YOU MUST SET THIS** to frontend URL
- `SIMILARITY_THRESHOLD` - Default: 0.85
- `RISK_THRESHOLD` - Default: 0.75
- `MIN_PAUSE_DURATION` - Default: 2000
- `MAX_TYPING_SPEED` - Default: 150

### Frontend  
- `NEXT_PUBLIC_API_URL` - Auto-configured to backend URL
- `NODE_ENV` - Set to `production`

## Free Tier Limits
- **Database:** 1GB storage, expires after 90 days
- **Web Services:** 750 hours/month, sleeps after 15min inactivity
- **Bandwidth:** More than enough for development

## Troubleshooting

### Services won't start
- Check build logs in Render dashboard
- Ensure Dockerfiles are working (they should - CI/CD validates them)

### CORS errors
- Update `CORS_ORIGINS` in backend to match frontend URL
- Include protocol: `https://your-frontend.onrender.com`

### Database connection issues
- Render auto-configures `DATABASE_URL`
- Check backend logs if connection fails

### Frontend can't reach backend
- Verify `NEXT_PUBLIC_API_URL` is set
- Check backend service is running

## Manual Alternative

If Blueprint doesn't work, you can create services manually:

1. **Database:** New → PostgreSQL → Free tier
2. **Backend:** New → Web Service → Connect repo → `/backend` as root directory
3. **Frontend:** New → Web Service → Connect repo → `/frontend` as root directory

Then configure environment variables as listed above.

## Next Steps

After successful deployment:
1. Visit your frontend URL
2. Test the exam functionality
3. Check admin dashboard with simulated data
4. Monitor logs in Render dashboard

## Keeping It Free

To maximize free tier:
- Services sleep after inactivity (normal, wakes on request)
- Database has 90-day limit - export data before expiry
- Consider upgrading if you need 24/7 uptime

---

**Need Help?** Check Render docs at [render.com/docs](https://render.com/docs)
