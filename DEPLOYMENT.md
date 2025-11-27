# Transl8 - Deployment Guide

## Microservices Architecture

Transl8 is built as a microservices architecture with the following components:

### Services

| Service | Purpose | Replicas (Prod) | Resources |
|---------|---------|-----------------|-----------|
| **API** | FastAPI REST API | 2+ | 1-2 CPU, 1-2GB RAM |
| **Worker (Parsing)** | Parse uploaded files | 2+ | 1 CPU, 2GB RAM |
| **Worker (Translation)** | AI translation | 3+ | 2 CPU, 3GB RAM |
| **Worker (Export)** | Export translated files | 2+ | 1 CPU, 2GB RAM |
| **Beat** | Celery scheduler | 1 | 0.5 CPU, 512MB RAM |
| **Flower** | Celery monitoring | 1 | 0.5 CPU, 256MB RAM |
| **PostgreSQL** | Database | 1 | 2 CPU, 4GB RAM |
| **Redis** | Cache + Queue | 1 | 1 CPU, 2GB RAM |
| **Nginx** | Reverse proxy | 1 | 0.5 CPU, 256MB RAM |

---

## Local Development

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url> transl8
cd transl8

# 2. Create environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your keys

# 3. Start all services
make up

# 4. Run migrations
make migrate

# 5. Access services
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower: http://localhost:5555
```

### Makefile Commands

```bash
# Development
make build          # Build Docker images
make up             # Start all services
make down           # Stop all services
make restart        # Restart services
make logs           # View all logs
make logs-api       # View API logs
make logs-worker    # View worker logs

# Database
make migrate        # Run migrations
make migrate-create # Create new migration
make db-shell       # PostgreSQL shell

# Testing
make test           # Run tests
make test-cov       # Run tests with coverage

# Utilities
make shell          # Python shell
make ps             # List services
make health         # Check service health

# Cleanup
make clean          # Remove containers
make clean-all      # Remove everything
```

### Manual Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## Production Deployment

### 1. Prepare Environment

```bash
# Copy production environment template
cp backend/.env.production.example backend/.env.production

# Edit with production values
nano backend/.env.production
```

**Important variables to set:**
- `SECRET_KEY` - Random secure string
- `DB_PASSWORD` - Strong database password
- `REDIS_PASSWORD` - Redis password
- `CLERK_JWT_PUBLIC_KEY` - Production Clerk key
- `DEEPL_API_KEY` - DeepL API key
- `S3_*` - S3/R2 credentials
- `CORS_ORIGINS` - Production frontend URLs

### 2. Build Production Images

```bash
# Build optimized Alpine images
docker-compose -f docker-compose.prod.yml build

# Or using Makefile
make prod-build
```

### 3. Deploy to Production

```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Or using Makefile
make prod-up

# Check status
make prod-ps

# View logs
make prod-logs
```

### 4. Run Migrations

```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 5. Configure Nginx/SSL

For HTTPS in production:

1. Obtain SSL certificate (Let's Encrypt, Cloudflare, etc.)
2. Place certificate files in `nginx/ssl/`
3. Uncomment HTTPS server block in `nginx/nginx.conf`
4. Restart nginx:
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

---

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Push images to ECR:**
   ```bash
   # Create ECR repositories
   aws ecr create-repository --repository-name transl8/api
   aws ecr create-repository --repository-name transl8/worker

   # Build and push
   docker build -t transl8/api -f backend/Dockerfile.alpine backend/
   docker tag transl8/api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/transl8/api:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/transl8/api:latest
   ```

2. **Create ECS Task Definitions** for each service

3. **Set up RDS** for PostgreSQL

4. **Set up ElastiCache** for Redis

5. **Configure ALB** (Application Load Balancer)

#### Using EKS (Kubernetes)

See `kubernetes/` directory for manifests (to be added).

### Railway Deployment

Railway supports docker-compose directly:

1. Connect GitHub repository
2. Railway will detect `docker-compose.yml`
3. Configure environment variables
4. Deploy

### Render Deployment

1. Create separate services for each component
2. Configure environment variables
3. Set up PostgreSQL and Redis add-ons
4. Deploy

### DigitalOcean App Platform

1. Create app from GitHub
2. Configure Dockerfile
3. Add PostgreSQL and Redis managed databases
4. Deploy

---

## Scaling

### Horizontal Scaling

Scale specific services based on load:

```bash
# Scale API to 3 replicas
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Scale translation workers to 5 replicas
docker-compose -f docker-compose.prod.yml up -d --scale worker-translation=5
```

### Kubernetes Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Monitoring

### Health Checks

Each service has health checks:

```bash
# Check API health
curl http://localhost:8000/health

# Check all services
make health
```

### Celery Monitoring with Flower

Access Flower at http://localhost:5555

- View task queues
- Monitor worker performance
- Track task execution
- View task history

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api
docker-compose logs -f worker-translation

# Follow last 100 lines
docker-compose logs -f --tail=100
```

### Recommended Monitoring Stack

- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger or DataDog
- **Error Tracking**: Sentry
- **Uptime Monitoring**: UptimeRobot or Pingdom

---

## Database Management

### Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U transl8 transl8 > backup.sql

# Restore
docker-compose exec -T postgres psql -U transl8 transl8 < backup.sql
```

### Automated Backups

Add to `docker-compose.prod.yml`:

```yaml
  backup:
    image: prodrigestivill/postgres-backup-local
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=transl8
      - POSTGRES_USER=transl8
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - SCHEDULE=@daily
      - BACKUP_KEEP_DAYS=7
    volumes:
      - ./backups:/backups
    depends_on:
      - postgres
```

### Migrations

```bash
# Create migration
make migrate-create

# Apply migrations
make migrate

# Rollback
make migrate-downgrade
```

---

## Security Best Practices

### 1. Environment Variables

- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Rotate credentials regularly

### 2. Network Security

- Use internal Docker networks
- Only expose necessary ports
- Enable firewall rules
- Use VPC in cloud environments

### 3. Container Security

- Run containers as non-root user ✅ (implemented)
- Use minimal base images ✅ (Alpine)
- Scan images for vulnerabilities
- Keep images updated

### 4. API Security

- Enable rate limiting ✅ (Nginx)
- Use HTTPS in production
- Validate JWT tokens ✅
- Implement CORS properly ✅

### 5. Database Security

- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular backups

---

## Troubleshooting

### API won't start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Database not ready: Wait for postgres health check
# - Migration failed: Check alembic version
# - Port conflict: Change port in docker-compose.yml
```

### Workers not processing tasks

```bash
# Check worker logs
docker-compose logs worker-translation

# Check Flower
open http://localhost:5555

# Restart workers
make restart-workers
```

### Database connection errors

```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection string
docker-compose exec api env | grep DATABASE_URL

# Restart database
make restart-db
```

### Out of memory errors

```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

---

## Performance Tuning

### Database

- Add indexes for frequently queried fields
- Configure connection pooling
- Enable query optimization
- Use read replicas for high traffic

### Redis

- Configure maxmemory policy
- Use Redis Cluster for high availability
- Enable persistence (AOF or RDB)

### API

- Enable response caching
- Use async endpoints
- Optimize database queries
- Enable compression

### Workers

- Tune concurrency settings
- Use appropriate queue priorities
- Monitor task execution times
- Scale based on queue length

---

## Cost Optimization

### Development

- Use local development (cheapest)
- Share development databases
- Stop services when not needed

### Production

- Use spot instances for workers (AWS)
- Enable auto-scaling
- Use managed databases (RDS, etc.)
- Monitor resource usage
- Right-size containers

---

## Support

For deployment issues:
- Check logs: `make logs`
- Review health checks: `make health`
- Consult documentation
- Open GitHub issue

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Celery Production](https://docs.celeryproject.org/en/stable/userguide/deployment.html)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
