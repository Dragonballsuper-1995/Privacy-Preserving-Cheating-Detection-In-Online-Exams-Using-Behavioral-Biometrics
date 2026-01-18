# Deployment Guide - Cheating Detector

**Version:** 1.0.0  
**Last Updated:** January 18, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Checklist](#security-checklist)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 10 GB
- OS: Linux, macOS, or Windows

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- OS: Ubuntu 22.04 LTS or similar

### Software Requirements

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher
- **PostgreSQL:** 14 or higher (production)
- **Redis:** 7.0 or higher (optional, for caching)
- **Docker:** 24.0+ and Docker Compose 2.20+ (for containerized deployment)

---

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/cheating-detector.git
cd cheating-detector
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt  # for testing

# Download datasets (optional)
python scripts/download_datasets.py

# Train models (optional, pre-trained models included)
python scripts/train_all_models.py

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 4. Run Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

---

## Production Deployment

### Option 1: Traditional Deployment (Ubuntu/Debian)

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3-pip python3-venv \
  postgresql postgresql-contrib nginx supervisor

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Setup User

```bash
# Create application user
sudo useradd -m -s /bin/bash cheating-detector
sudo su - cheating-detector
```

#### 3. Deploy Backend

```bash
# Clone and setup
git clone <repo_url> ~/app
cd ~/app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy trained models
mkdir -p models
cp /path/to/trained/models/* models/

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/cheating_detector
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
EOF
```

#### 4. Setup PostgreSQL

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE cheating_detector;
CREATE USER cheating_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cheating_detector TO cheating_user;
EOF

# Run migrations (when ready)
# python scripts/run_migrations.py
```

#### 5. Setup Supervisor (Process Management)

```bash
sudo nano /etc/supervisor/conf.d/cheating-detector.conf
```

Add:
```ini
[program:cheating-detector-backend]
directory=/home/cheating-detector/app/backend
command=/home/cheating-detector/app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
user=cheating-detector
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/cheating-detector/backend.err.log
stdout_logfile=/var/log/cheating-detector/backend.out.log
environment=PATH="/home/cheating-detector/app/backend/venv/bin"
```

```bash
# Create log directory
sudo mkdir -p /var/log/cheating-detector
sudo chown cheating-detector:cheating-detector /var/log/cheating-detector

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cheating-detector-backend
```

#### 6. Deploy Frontend

```bash
cd ~/app/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server (with PM2)
sudo npm install -g pm2
pm2 start npm --name "cheating-detector-frontend" -- start
pm2 save
pm2 startup
```

#### 7. Setup Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/cheating-detector
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cheating-detector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. Setup SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker Deployment

### 1. Create Docker Files

**backend/Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Copy trained models
COPY models/ /app/models/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**frontend/Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

### 2. Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: cheating_detector
      POSTGRES_USER: cheating_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cheating_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://cheating_user:${DB_PASSWORD}@db/cheating_detector
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend/models:/app/models
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### 3. Environment File

**.env:**
```bash
DB_PASSWORD=your_secure_db_password
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
```

### 4. Deploy with Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Environment Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/cheating_detector

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Storage
MODELS_DIR=./models
DATA_DIR=./data
EVENT_LOGS_DIR=./data/event_logs

# Features
MIN_PAUSE_DURATION=2000
RISK_THRESHOLD=0.75

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

---

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE cheating_detector
  WITH ENCODING 'UTF8'
  LC_COLLATE='en_US.UTF-8'
  LC_CTYPE='en_US.UTF-8'
  TEMPLATE=template0;
```

### 2. Run Migrations

```bash
# Using Alembic (when implemented)
cd backend
alembic upgrade head
```

### 3. Backup Strategy

```bash
# Create backup
pg_dump -U cheating_user cheating_detector > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U cheating_user cheating_detector < backup_20260118.sql

# Automated daily backups (cron)
0 2 * * * pg_dump -U cheating_user cheating_detector | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring & Logging

### 1. Application Logs

```bash
# Using systemd
sudo journalctl -u cheating-detector -f

# Using supervisor
tail -f /var/log/cheating-detector/backend.out.log

# Using Docker
docker-compose logs -f backend
```

### 2. Performance Monitoring

Install and configure monitoring tools:

```bash
# Prometheus + Grafana
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3000:3000 grafana/grafana
```

### 3. Error Tracking

Consider integrating:
- **Sentry** for error tracking
- **DataDog** for application monitoring
- **New Relic** for performance monitoring

---

## Security Checklist

### Pre-Deployment

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW/iptables)
- [ ] Enable rate limiting
- [ ] Set up CORS properly
- [ ] Disable DEBUG mode in production
- [ ] Review and secure all environment variables
- [ ] Enable database connection encryption
- [ ] Set up regular backups
- [ ] Configure log rotation
- [ ] Implement authentication & authorization
- [ ] Enable CSRF protection
- [ ] Sanitize all user inputs
- [ ] Set proper file permissions

### Post-Deployment

- [ ] Monitor logs for suspicious activity
- [ ] Set up alerting for critical errors
- [ ] Perform security audit
- [ ] Review access logs regularly
- [ ] Keep dependencies updated
- [ ] Monitor resource usage
- [ ] Test disaster recovery plan

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
sudo supervisorctl tail -f cheating-detector-backend

# Check if port is in use
sudo lsof -i :8000

# Verify database connection
psql -U cheating_user -d cheating_detector

# Check environment variables
env | grep DATABASE_URL
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep uvicorn

# Monitor in real-time
htop

# Reduce worker count in production
# uvicorn --workers 2 instead of --workers 4
```

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U cheating_user -d cheating_detector

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Model Loading Errors

```bash
# Verify models exist
ls -la backend/models/

# Check file permissions
chmod 644 backend/models/*.pkl

# Retrain if necessary
cd backend
python scripts/train_all_models.py
```

---

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml with multiple backend instances
services:
  backend-1:
    build: ./backend
    # ...
  
  backend-2:
    build: ./backend
    # ...

  load-balancer:
    image: nginx
    # Configure load balancing
```

### Caching Strategy

- Use Redis for session caching
- Cache analysis results for completed sessions
- Implement CDN for static assets

### Database Optimization

- Add indexes on frequently queried columns
- Use connection pooling
- Consider read replicas for analytics queries
- Partition large tables by date

---

## Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor error logs
- Check disk space
- Verify backups completed

**Weekly:**
- Review performance metrics
- Update dependencies (security patches)
- Test backup restoration

**Monthly:**
- Security audit
- Performance optimization review
- Capacity planning

---

## Additional Resources

- **Documentation:** See README.md and API.md
- **Training Guide:** backend/TRAINING_GUIDE.md
- **Test Documentation:** backend/tests/README.md
- **Results Report:** RESULTS.md

---

**For production support, contact:** devops@example.com
