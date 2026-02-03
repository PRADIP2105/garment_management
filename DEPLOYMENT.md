# Deployment Guide

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd garment-management-system
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Manual Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### Installation Steps

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb garment_management
   
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run setup script**
   ```bash
   python setup.py
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Start mobile app**
   ```bash
   python mobile_app.py
   ```

## Production Deployment

### Environment Variables

Create a `.env` file with production settings:

```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=garment_management
DB_USER=your_db_user
DB_PASSWORD=your_secure_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

### Using Gunicorn

1. **Install gunicorn** (already in requirements.txt)

2. **Run with gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:8000 garment_management.wsgi:application
   ```

### Nginx Configuration

Create `/etc/nginx/sites-available/garment-management`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /path/to/your/app/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL with Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Systemd Service

Create `/etc/systemd/system/garment-management.service`:

```ini
[Unit]
Description=Garment Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/app/garment_management.sock garment_management.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable garment-management
sudo systemctl start garment-management
```

## Database Backup

### Backup
```bash
pg_dump garment_management > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore
```bash
psql garment_management < backup_file.sql
```

## Monitoring

### Log Files
- Application logs: Check Django logs
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u garment-management`

### Health Check Endpoint
The application includes basic health checks at `/api/dashboard/stats/`

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] Regular backups configured
- [ ] Firewall configured
- [ ] Regular security updates

## Scaling

### Database
- Use connection pooling
- Consider read replicas for heavy read workloads
- Regular database maintenance

### Application
- Use multiple gunicorn workers
- Consider load balancing for multiple servers
- Implement caching (Redis/Memcached)

### Static Files
- Use CDN for static files
- Enable gzip compression
- Optimize images

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check database credentials
   - Ensure PostgreSQL is running
   - Verify network connectivity

2. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check nginx static file configuration

3. **Permission errors**
   - Check file permissions
   - Ensure correct user/group ownership

4. **Memory issues**
   - Monitor memory usage
   - Adjust gunicorn worker count
   - Consider adding swap space

### Getting Help

1. Check application logs
2. Review Django debug information
3. Check system resources
4. Verify configuration files

## Performance Optimization

### Database
- Add appropriate indexes
- Use select_related() and prefetch_related()
- Monitor slow queries

### Caching
- Implement Redis for session storage
- Cache frequently accessed data
- Use template fragment caching

### Frontend
- Minimize HTTP requests
- Optimize images
- Use browser caching headers