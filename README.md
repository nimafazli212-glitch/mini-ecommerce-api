
# Mini E-Commerce API

A production-oriented REST API for a mini e-commerce platform built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic**, and **JWT Authentication**.

This project demonstrates a clean backend architecture with authentication, authorization, product management, order processing, inventory control, database migrations, Docker support, and automated testing.

---

# Features

## Authentication & Security

- User registration
- JWT-based authentication
- Password hashing with pwdlib
- Protected API routes
- Role-based authorization
- Customer/Admin access control

## User Management

- Create user account
- Get current authenticated user
- Admin user management
- User permission validation

## Product Management

- Product CRUD operations
- Product activation/deactivation (Soft Delete)
- Product search
- Price filtering
- Pagination
- Stock management

## Order Management

- Create orders
- View user orders
- Order details
- Cancel pending orders
- Admin order management
- Order status workflow

Supported order statuses:
PENDING
CONFIRMED
SHIPPED
DELIVERED
CANCELLED


## Inventory Safety

- Stock validation before purchase
- Database row locking for stock-sensitive operations
- Prevent overselling during concurrent purchases

## Database

- PostgreSQL
- Async SQLAlchemy 2.0
- Alembic migrations
- Database version control

## API Quality

- OpenAPI documentation
- Swagger UI
- Request/Response validation
- Automated API tests

---

# Tech Stack

| Technology | Usage |
|---|---|
| Python 3.11 | Backend language |
| FastAPI | Web framework |
| SQLAlchemy 2.0 | ORM |
| PostgreSQL | Database |
| Alembic | Database migrations |
| Pydantic v2 | Data validation |
| JWT | Authentication |
| AsyncPG | Async PostgreSQL driver |
| Docker | Containerization |
| Pytest | Testing |

---

# Project Structure
mini-ecommerce-api/

├── app/
│
│ ├── api/
│ │ ├── auth.py
│ │ ├── users.py
│ │ ├── products.py
│ │ └── orders.py
│ │
│ ├── core/
│ │ ├── config.py
│ │ ├── dependencies.py
│ │ ├── permissions.py
│ │ ├── security.py
│ │ └── exceptions.py
│ │
│ ├── db/
│ │ ├── database.py
│ │ ├── dependencies.py
│ │ └── models/
│ │
│ ├── schemas/
│ │
│ ├── services/
│ │ └── order_service.py
│ │
│ └── main.py
│
├── alembic/
│ └── versions/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md

بعد از این پیام، قسمت دوم را می‌فرستم که شامل Installation تا آخر README است.


نه فایلشو بساز برام 

آماده شد داش. فایل README.md ساخته شد.

می‌تونی مستقیم جایگزین README پروژه کنی:

دریافت README.md

بعد از جایگزینی:

git add README.md
git commit -m "Improve project documentation"
بزن. 


README.md
Document


Library
/
backend
/
README.md


Mini E-Commerce API
A production-oriented REST API for a mini e-commerce platform built with
FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, and JWT Authentication.

Features
JWT authentication

Password hashing

Role-based authorization (customer/admin)

Product CRUD

Product search and pagination

Soft delete products

Order creation and cancellation

Inventory validation

Row-level locking for stock operations

PostgreSQL database

Async SQLAlchemy

Alembic migrations

Automated tests

Tech Stack
Python 3.11

FastAPI

SQLAlchemy 2.0

PostgreSQL

Alembic

Pydantic v2

JWT

AsyncPG

Docker

Pytest

Structure
mini-ecommerce-api/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
Installation
git clone <YOUR_REPOSITORY_URL>
cd mini-ecommerce-api
Create environment:

python -m venv .venv
.venv\Scripts\activate
Install:

pip install -r requirements.txt
Environment
Create .env:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ecommerce
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
Database
Run migrations:

alembic upgrade head
Run
uvicorn app.main:app --reload
Swagger:

http://127.0.0.1:8000/docs
Docker
docker compose up --build
Testing
pytest -v
Covered tests:

Authentication

Users

Permissions

Products

Search

Pagination

Orders

Stock validation

Security
Implemented:

JWT authentication

Password hashing

Admin permissions

Transaction handling

Inventory locking

Future Improvements
Refresh tokens

Payment gateway

Redis cache

CI/CD pipeline

License
Portfolio project.


CI test

CI/CD test - Railway auto deploy
