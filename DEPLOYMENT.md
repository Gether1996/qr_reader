# QR Reader - Production Deployment Guide

## Zmeny pre Production

### 1. **Security Settings** ✅
- DEBUG je teraz kontrolovaný cez environment variable
- SECRET_KEY by mal byť unikátny pre production
- ALLOWED_HOSTS je whitelist povolených domén
- SSL/HTTPS security headers (HSTS, Secure Cookies, etc.)
- CSRF a Session cookie security

### 2. **Web Server** ✅
- Zmenený z `runserver` na **Gunicorn** (production WSGI server)
- 4 worker procesy pre lepší výkon
- Timeout 120 sekúnd

### 3. **Docker Optimalizácie** ✅
- Použitý `python:3.10-slim` namiesto full image (menší)
- Multi-stage prístup k dependencies
- Non-root user pre bezpečnosť
- Healthcheck pre monitoring
- Persistent volumes pre databázu, média a logy

### 4. **Logging** ✅
- Konfigurácia logov do súboru `logs/django.log`
- Console aj file handlers
- WARNING level pre production

### 5. **Static Files** ✅
- WhiteNoise middleware správne umiestnený
- Compressed a hashed static files

## Deployment Kroky

### Prvé nasadenie:

```bash
# 1. Vytvor .env súbor
cp .env.example .env
# Uprav SECRET_KEY a ostatné nastavenia

# 2. Vytvor potrebné adresáre
mkdir -p logs media

# 3. Build a spusti kontajner
docker compose down
docker compose build --no-cache
docker compose up -d

# 4. Spusti migrácie (len pri prvom nasadení)
docker exec qr_reader python manage.py migrate

# 5. Vytvor superusera (voliteľné)
docker exec -it qr_reader python manage.py createsuperuser

# 6. Skontroluj logy
docker logs qr_reader -f
```

### Update aplikácie:

```bash
# 1. Pull zmeny z gitu
git pull

# 2. Rebuild a restart
docker compose down
docker compose build
docker compose up -d

# 3. Spusti nové migrácie (ak sú)
docker exec qr_reader python manage.py migrate

# 4. Skontroluj status
docker ps
docker logs qr_reader -f
```

## Nginx Konfigurácia (Odporúčaná)

Vytvor `/etc/nginx/sites-available/qr_reader`:

```nginx
server {
    listen 80;
    server_name dqr.314.sk;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dqr.314.sk;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/dqr.314.sk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dqr.314.sk/privkey.pem;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Max upload size
    client_max_body_size 10M;

    # Proxy to Django
    location / {
        proxy_pass http://localhost:9005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    # Static files (optional - Gunicorn can handle this with WhiteNoise)
    location /static/ {
        alias /path/to/qr_reader/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/qr_reader/media/;
        expires 7d;
    }
}
```

Aktivuj konfiguráciu:
```bash
sudo ln -s /etc/nginx/sites-available/qr_reader /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certifikát (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dqr.314.sk
```

## Monitoring

### Skontroluj zdravie aplikácie:
```bash
# Container status
docker ps

# Logy
docker logs qr_reader -f

# Health check
docker inspect qr_reader | grep Health -A 10

# Resource usage
docker stats qr_reader
```

### Databáza backup:
```bash
# Backup
docker exec qr_reader cp /app/db.sqlite3 /app/db.sqlite3.backup
docker cp qr_reader:/app/db.sqlite3.backup ./backups/db_$(date +%Y%m%d).sqlite3

# Restore
docker cp ./backups/db_20251201.sqlite3 qr_reader:/app/db.sqlite3
docker restart qr_reader
```

## Environment Variables

Dôležité production nastavenia v `.env`:

```bash
SECRET_KEY=generuj-novy-tajny-kluc-min-50-znakov
DEBUG=False
ALLOWED_HOSTS=dqr.314.sk
```

Vygeneruj nový SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Bezpečnostný Checklist

- ✅ DEBUG=False v produkcii
- ✅ Unikátny SECRET_KEY
- ✅ ALLOWED_HOSTS správne nastavený
- ✅ HTTPS/SSL certifikát
- ✅ Secure cookies
- ✅ CSRF protection
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection headers
- ✅ Non-root user v Docker
- ✅ Regular security updates
- ✅ Database backups
- ✅ Logging enabled

## Výkonnostné Tipy

1. **Database**: Pre väčšie nasadenie zvážte PostgreSQL namiesto SQLite
2. **Cache**: Pridaj Redis pre session a cache
3. **CDN**: Použij CDN pre static files
4. **Monitoring**: Pridaj Sentry pre error tracking
5. **Backup**: Automatizuj denné backupy databázy

## Troubleshooting

### Aplikácia sa nespúšťa:
```bash
docker logs qr_reader
docker exec -it qr_reader bash
```

### Static files sa nenačítavajú:
```bash
docker exec qr_reader python manage.py collectstatic --noinput
```

### Database problémy:
```bash
docker exec qr_reader python manage.py migrate
docker exec qr_reader python manage.py check
```

## Support

Pre problémy check Django logs v `logs/django.log` alebo Docker logs.
