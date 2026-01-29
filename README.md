# Test Junior Programmer – Product Management

This project is a solution for the **Junior Programmer Test**.
The application fetches product data from an external API, stores it in a database,
and provides CRUD functionality with filtering based on product status.

---

## Project Overview

The application performs the following:
- Fetch product data from a protected external API
- Store products, categories, and statuses into a relational database
- Display products that have status **"bisa dijual"** and **"Semua Produk"**
- Provide CRUD features with validation and confirmation

---

## Tech Stack

- Python 3.13
- Django 
- Django REST Framework (Serializer usage)
- PostgreSQL (production-ready) & SQLite (local development)
- django-environ
- django-filter
- django-crispy-forms
- uv (virtual environment)
- psycopg2-binary
- requests
- pytest
- pytest-django
- ruff
- black

---

## Features

- Import products from external API 
- Product listing filtered by status **"Bisa Dijual"** and **"Semua Produk"
- Add, edit, and delete products 
- Form validation:
  - Product name is required
  - Price must be a number
- Delete confirmation alert
- Environment-based configuration (local & production)

---

## Project Structure

fastprint_test/                  # project root
├── manage.py
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       └── production.py
├── products/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tests.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── import_products.py
│   └── management/
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── import_products.py
├── pyproject.toml
|── requirements.txt
├── .env.example
└── README.md

---

## Setup & Instalation

1. Clone repository
git clone https://github.com/Rendbagoez93/fastprint-test.git
cd (project folder)

2. Create virtual environment
uv venv
source .venv/bin/activate

3. Install dependencies
uv pip install -r requirements.txt

## Environment Configuration

Create .env file based on .env.example:
DJANGO_SETTINGS_MODULE=config.settings.local

## Database Choice & Database Setup

### Database Choice

SQLite was used for local development to simplify setup and speed up development.
The application uses Django ORM and environment-based configuration, so switching
to PostgreSQL or MySQL requires only a database configuration change. 

### Database Setup

This project uses PostgreSQL as the database. Connection settings are managed
via environment variables using django-environ. Run migrations after configuring the database:

python manage.py migrate

## Importing Data from API

Product data is fetched from the provided API and stored using a Django management command.

Run: 
python manage.py import_products

This will:
- Fetch data from API (https://recruitment.fastprint.co.id/tes/api_tes_programmer) 
- Create categories and statuses if they do not exist
- Store products into the database

## Running the Application

python manage.py runserver 

Access aplications at: 

http://127.0.0.1:8000/

## CRUD Usage

- Add Product: Use form with validation
- Edit Product: Update existing data
- Delete Product: Confirmation alert required
- Filter: Only products with status "bisa dijual" and "Semua Produk" are displayed

## Notes & Assumption

- SQLite is used for local development for simplicity
- PostgreSQL configuration is prepared for production use
- API access was verified manually (headers, response, cookies) before integration
- Management command is used to ensure clean and repeatable data import 

## Author 

Created by : Rendy Herdianto