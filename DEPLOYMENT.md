# Deployment Guide

> Production deployment documentation for the Cheating Detection System

---

## Deployment Options

| Method | Use Case |
|--------|----------|
| Docker Compose | Full production stack |
| Render.com | Cloud PaaS deployment |
| Manual | Development/testing |

---

## Docker Compose Deployment

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                      NGINX                          │
│              (Reverse Proxy, SSL)                   │
│                  Ports: 80, 443                     │
└─────────────────┬───────────────────┬───────────────┘
                  │                   │
         ┌────────▼────────┐ ┌────────▼────────┐
         │    Frontend     │ │    Backend      │
         │   (Next.js)     │ │   (FastAPI)     │
         │   Port: 3000    │ │   Port: 8000    │
         └─────────────────┘ └────────┬────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                      │
          ┌────────▼────────┐               ┌────────────▼────────────┐
          │   PostgreSQL    │               │        Redis            │
          │   Port: 5432    │               │      Port: 6379         │
          └─────────────────┘               └─────────────────────────┘
```

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Configuration

1. **Create environment file**:

```bash
cp .env.example .env
```

2. **Edit `.env` with secure values**:

```env
# Database
DB_NAME=cheating_detector
DB_USER=cheating_user
DB_PASSWORD=<secure-password>

# Redis
REDIS_PASSWORD=<redis-password>

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
ALLOWED_ORIGINS=https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Launch

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Services

| Service | Container Name | Port | Health Check |
|---------|---------------|------|--------------|
| PostgreSQL | cheating-detector-db | 5432 | `pg_isready` |
| Redis | cheating-detector-redis | 6379 | `redis-cli ping` |
| Backend | cheating-detector-backend | 8000 | `GET /health` |
| Frontend | cheating-detector-frontend | 3000 | `GET /` |
| NGINX | cheating-detector-nginx | 80, 443 | `nginx -t` |

---

## Render.com Deployment

The project includes `render.yaml` for Render Blueprint deployment.

### Deploy Steps

1. Push code to GitHub
2. Connect repository to Render
3. Render auto-detects `render.yaml`
4. Configure environment variables in Render dashboard
5. Deploy

### Required Environment Variables (Render)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` | Backend API URL |

---

## Manual Deployment

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/cheating_detector"
export SECRET_KEY="your-secret-key"
export ENVIRONMENT="production"

# Run with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm run start
```

---

## Dependencies

### Backend (`requirements.txt`)

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.25
psycopg2-binary>=2.9.9
scikit-learn>=1.4.0
sentence-transformers>=2.2.2
torch>=2.0.0
pandas>=2.1.4
numpy>=1.26.3
pydantic>=2.5.3
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-dom": "18.x"
  }
}
```

---

## SSL/TLS Configuration

NGINX config location: `nginx/nginx.conf`

For SSL:
1. Place certificates in `nginx/ssl/`
2. Update `nginx.conf` with certificate paths
3. Restart NGINX container

---

## Volumes

| Volume | Purpose |
|--------|---------|
| `postgres_data` | Database persistence |
| `redis_data` | Cache persistence |
| `backend_data` | Event logs, training data |
| `backend_logs` | Application logs |
| `nginx_logs` | Access/error logs |

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - DATABASE_URL not set
# - Port 8000 already in use
# - Missing requirements
```

### Database connection failed

```bash
# Verify PostgreSQL is running
docker-compose ps db

# Check connection
docker-compose exec db psql -U cheating_user -d cheating_detector
```

### Frontend build fails

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and rebuild
rm -rf frontend/.next frontend/node_modules
npm install
npm run build
```
