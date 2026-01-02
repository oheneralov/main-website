# Environment Setup & Deployment Guide

## Environment Variables

Create a `.env` file in the root `mainwebsite/` directory:

### Development Environment
```bash
# Server Configuration
PORT=3000
NODE_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=password
DB_NAME=website

# SendGrid Email Configuration
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
CONTACT_EMAIL=admin@your-domain.com
SENDER_EMAIL=noreply@your-domain.com

# Google Cloud Logging (Optional)
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id
```

### Production Environment
```bash
# Server Configuration
PORT=3000
NODE_ENV=production

# Database Configuration (Use production database)
DB_HOST=your-prod-db-host.example.com
DB_PORT=3306
DB_USERNAME=prod_db_user
DB_PASSWORD=secure_production_password
DB_NAME=website_prod

# SendGrid Email Configuration
SENDGRID_API_KEY=SG.your_prod_sendgrid_api_key
CONTACT_EMAIL=hello@your-domain.com
SENDER_EMAIL=noreply@your-domain.com

# Google Cloud Logging (Optional)
GOOGLE_CLOUD_PROJECT_ID=your_prod_gcp_project_id
```

---

## Local Development Setup

### Prerequisites
- Node.js 16 or higher
- npm or yarn
- MySQL 5.7 or higher
- SendGrid account (for email)

### Step-by-Step Setup

1. **Create local MySQL database**
   ```sql
   CREATE DATABASE website;
   CREATE USER 'website_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON website.* TO 'website_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **Create `.env` file** in root directory
   ```bash
   cp .env.example .env
   # Edit .env with your local credentials
   ```

3. **Install dependencies**
   ```bash
   npm install
   cd react
   npm install
   cd ..
   ```

4. **Start MySQL service**
   ```bash
   # macOS
   brew services start mysql

   # Linux
   sudo systemctl start mysql

   # Windows
   net start MySQL80  # or your MySQL version
   ```

5. **Run in development mode**
   ```bash
   npm run start:dev
   ```

6. **Access the application**
   - Open http://localhost:3000
   - Test contact form
   - Check logs in console

---

## Docker Deployment

### Dockerfile (for backend)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy built application (after npm run build)
COPY dist ./dist
COPY public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/auth/status', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start application
CMD ["node", "dist/main.js"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: website
      MYSQL_USER: website_user
      MYSQL_PASSWORD: user_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 3s
      retries: 10

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USERNAME: website_user
      DB_PASSWORD: user_password
      DB_NAME: website
      NODE_ENV: production
      PORT: 3000
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

volumes:
  mysql_data:
```

### Deploy with Docker
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

---

## Kubernetes Deployment

### ConfigMap for environment
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-info-website-config
data:
  NODE_ENV: "production"
  DB_HOST: "mysql-service.default.svc.cluster.local"
  DB_PORT: "3306"
  DB_NAME: "website"
```

### Secret for sensitive data
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-info-website-secret
type: Opaque
stringData:
  DB_USERNAME: website_user
  DB_PASSWORD: secure_password
  SENDGRID_API_KEY: SG.your_api_key
  CONTACT_EMAIL: admin@your-domain.com
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aws-info-website
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aws-info-website
  template:
    metadata:
      labels:
        app: aws-info-website
    spec:
      containers:
      - name: aws-info-website
        image: your-registry/aws-info-website:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: aws-info-website-config
        - secretRef:
            name: aws-info-website-secret
        livenessProbe:
          httpGet:
            path: /auth/status
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /auth/status
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: aws-info-website-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: aws-info-website
```

---

## AWS Deployment (ECS)

### Task Definition (ECS)
```json
{
  "family": "aws-info-website",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "aws-info-website",
      "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/aws-info-website:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "hostPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "DB_HOST",
          "value": "your-rds-endpoint.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:account:secret:db-password"
        },
        {
          "name": "SENDGRID_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:account:secret:sendgrid-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aws-info-website",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## Heroku Deployment

### Procfile
```
web: npm run build && npm run start:prod
```

### Deploy
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set DB_HOST=your-db-host
heroku config:set DB_USERNAME=your_username
heroku config:set DB_PASSWORD=your_password
heroku config:set SENDGRID_API_KEY=SG.your_key

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## PM2 Process Management

### ecosystem.config.js
```javascript
module.exports = {
  apps: [
    {
      name: 'aws-info-website',
      script: './dist/main.js',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        DB_HOST: 'localhost',
        DB_PORT: 3306
      },
      error_file: './logs/error.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
```

### Deploy with PM2
```bash
# Install PM2 globally
npm install -g pm2

# Start with PM2
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs

# Restart
pm2 restart aws-info-website

# Stop
pm2 stop aws-info-website
```

---

## Database Migration

### Generate TypeORM Migrations
```bash
npm run typeorm migration:generate -- -n InitialSchema
npm run typeorm migration:run
```

### Backup Before Deployment
```bash
# MySQL backup
mysqldump -u website_user -p website > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
mysql -u website_user -p website < backup.sql
```

---

## SSL/TLS Configuration

### Using Nginx as Reverse Proxy with SSL
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-domain.com.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.com.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Monitoring & Logging

### Google Cloud Logging
```typescript
// Already configured in LoggingService
// Logs automatically sent if GOOGLE_CLOUD_PROJECT_ID is set
```

### CloudWatch (AWS)
```bash
# View logs
aws logs tail /ecs/aws-info-website --follow

# Create log group
aws logs create-log-group --log-group-name /app/aws-info-website
```

---

## Performance Optimization

### Environment variables for caching
```bash
# Cache control headers
CACHE_CONTROL=public, max-age=31536000

# CDN configuration
CDN_URL=https://cdn.your-domain.com
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process
lsof -i :3000
kill -9 <PID>

# Or use different port
PORT=3001 npm run start:prod
```

### Database Connection Error
```bash
# Test connection
mysql -h DB_HOST -u DB_USERNAME -p

# Check environment variables
echo $DB_HOST
echo $DB_USERNAME
```

### SendGrid Email Not Working
```bash
# Verify API key
curl -X GET https://api.sendgrid.com/v3/mail/settings \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

---

**Your AWS Info Website is ready for production deployment! 🚀**
