# Database Configuration

This project is configured to use different databases for different environments:

## Local Development (SQLite)

**Automatic** - No setup required!

- Database: SQLite (file-based)
- Location: `db.sqlite3` in project root
- Settings: `config.settings.local`

### Usage:
```bash
# Set environment to local (already default in .env)
DJANGO_SETTINGS_MODULE=config.settings.local

# Run migrations
uv run manage.py migrate

# Run server
uv run manage.py runserver
```

## Production (PostgreSQL)

Requires PostgreSQL server installation and configuration.

### Prerequisites:
1. PostgreSQL server installed and running
2. Database created
3. User with proper permissions

### Configuration:

Update `.env` file with production settings:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL Configuration
DB_NAME=fastprint_production
DB_USER=fastprint_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=600
```

### Usage:
```bash
# Run migrations
uv run manage.py migrate --settings=config.settings.production

# Run server (use gunicorn in production)
uv run manage.py runserver --settings=config.settings.production
```

## Switching Between Environments

### Method 1: Environment Variable
```bash
# Local (SQLite)
$env:DJANGO_SETTINGS_MODULE="config.settings.local"

# Production (PostgreSQL)
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
```

### Method 2: Command Line
```bash
# Local
uv run manage.py migrate --settings=config.settings.local

# Production
uv run manage.py migrate --settings=config.settings.production
```

## Database Features by Environment

| Feature | Local (SQLite) | Production (PostgreSQL) |
|---------|----------------|-------------------------|
| Setup | Automatic | Manual |
| Performance | Good for development | Optimized for production |
| Concurrent Users | Limited | High |
| Connection Pooling | No | Yes (CONN_MAX_AGE=600) |
| Backup | Copy db.sqlite3 | pg_dump |

## Notes

- SQLite is **perfect for local development** - no installation needed
- PostgreSQL is **recommended for production** - better performance and scalability
- All Django models work identically in both databases
- Migrations are compatible between both databases
