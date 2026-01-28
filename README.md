# FastPrint Test

## Overview
This web-based App is used as a test to qualify as Junior Programmer in Fast Print Indonesia Surabaya Branch. 

## Tech Stack

### Core Framework
- **Django 6.0.1**: High-level Python web framework for rapid development
- **Django REST Framework 3.16.1**: Powerful toolkit for building Web APIs

### Database
- **psycopg2-binary 2.9.11**: PostgreSQL database adapter for Python (For Production)

### Form & Filter
- **django-crispy-forms 2.5**: Enhanced form rendering with Bootstrap support
- **django-filter 25.2**: Declarative filtering for Django querysets and REST Framework

### Utilities
- **django-environ 0.12.0**: Environment variable configuration for Django
- **requests 2.32.5**: HTTP library for consuming external APIs

### Development Tools
- **black 26.1.0**: Python code formatter for consistent code style
- **ruff 0.14.14**: Fast Python linter and code checker
- **pytest 9.0.2**: Testing framework for Python
- **pytest-django 4.11.1**: Django plugin for pytest

## Setup

### Prerequisites
- Python 3.13+
- PostgreSQL

### Installation

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your database credentials

4. Install dependencies:
   ```bash
   uv sync
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
fastprint-test/
├── config/              # Project configuration
│   ├── settings/        # Settings split by environment
│   │   ├── base.py      # Base settings
│   │   ├── local.py     # Development settings
│   │   └── production.py # Production settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── products/            # Products app
├── static/              # Static files
├── templates/           # HTML templates
└── manage.py            # Django management script
```

## Environment Variables

See `.env.example` for required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

## Running with Different Settings

### Local Development
```bash
python manage.py runserver --settings=config.settings.local
```

### Production
```bash
python manage.py runserver --settings=config.settings.production
```
