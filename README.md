# Mini E-Commerce API

A production-oriented REST API for a mini e-commerce system built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic**, and **JWT Authentication**.

The project includes user authentication, role-based authorization, product management, order management, stock control, pagination, filtering, and soft deletion.

---

## Features

* User registration and authentication
* JWT-based authentication
* Password hashing with `pwdlib`
* Role-based authorization (`customer` / `admin`)
* Product CRUD
* Product soft delete
* Product search and price filtering
* Pagination with total pages
* Order creation
* Order cancellation
* Order status management
* Stock management
* Row-level locking for stock-sensitive operations
* Order item price snapshot
* PostgreSQL database
* Async SQLAlchemy
* Alembic database migrations
* Pydantic request/response validation

---

## Tech Stack

* Python
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Alembic
* Pydantic v2
* Pydantic Settings
* PyJWT
* pwdlib
* AsyncPG

---

## Project Structure

```text
mini-ecommerce-api/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   └── orders.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── oauth2.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── models/
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd mini-ecommerce-api
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME
SECRET_KEY=YOUR_SECRET_KEY
```

Do not commit `.env` to GitHub.

---

## Database Setup

Make sure PostgreSQL is running.

Run the latest Alembic migrations:

```bash
alembic upgrade head
```

To check the current migration:

```bash
alembic current
```

---

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Authentication

Authentication uses JWT Bearer tokens.

### Login

```http
POST /auth/login
```

Example request:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

Example response:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "token_type": "bearer"
}
```

Use the returned token in protected endpoints:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Authorization

The API supports two user roles:

* `customer`
* `admin`

Admin-only operations use the `get_current_admin` dependency defined in:

```text
app/core/permissions.py
```

Customers cannot perform administrative product management or administrative order operations.

---

## Product API

### Create Product

```http
POST /products/
```

Admin access required.

### Get Products

```http
GET /products/
```

Supports:

* Pagination
* Name search
* Minimum price
* Maximum price

Example:

```text
GET /products/?page=1&limit=10&search=laptop&min_price=500&max_price=2000
```

Example response:

```json
{
  "items": [],
  "page": 1,
  "limit": 10,
  "total": 0,
  "pages": 0
}
```

### Get Product

```http
GET /products/{product_id}
```

### Update Product

```http
PATCH /products/{product_id}
```

Admin access required.

### Deactivate Product

```http
DELETE /products/{product_id}
```

Admin access required.

Products are soft-deleted rather than physically removed from the database. This preserves historical order data.

---

## Order API

### Create Order

```http
POST /orders/
```

Authenticated users can create orders.

Example:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

The API:

* Validates product availability
* Checks stock
* Locks the product row during the transaction
* Decreases stock
* Stores the purchase price in `OrderItem`
* Calculates the order total

### Get My Orders

```http
GET /orders/
```

Returns orders belonging to the authenticated user.

### Get Order

```http
GET /orders/{order_id}
```

Users can only access their own orders.

### Cancel Order

```http
PATCH /orders/{order_id}/cancel
```

Only pending orders can be cancelled.

When an order is cancelled, its quantities are returned to product stock.

### Update Order Status

```http
PATCH /orders/{order_id}/status
```

Supported status transitions:

```text
pending → confirmed
confirmed → shipped
shipped → delivered
```

Invalid status transitions are rejected by the API.

---

## Database Relationships

The main database relationships are:

```text
User
 │
 └──< Order
          │
          └──< OrderItem >── Product
```

A user can have multiple orders.

An order can contain multiple order items.

A product can appear in multiple order items.

---

## Order Price Snapshot

When an order is created, the current product price is copied into:

```text
OrderItem.unit_price
```

This means changing the product price later does not change historical orders.

For example:

```text
Product price at purchase: $999.99

OrderItem.unit_price: $999.99
```

If the product price later changes to:

```text
$1199.99
```

the existing order still contains:

```text
$999.99
```

This preserves historical purchase data.

---

## Product Lifecycle

Products use soft deletion.

Instead of permanently deleting a product:

```text
is_active = False
```

Inactive products:

* Are not shown in the public product list
* Cannot be retrieved through the public product endpoint
* Cannot be purchased
* Remain in the database
* Remain available for historical orders

---

## Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

Check migration history:

```bash
alembic history
```

---

## API Documentation

FastAPI automatically generates interactive documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

The `/docs` interface can be used to test authenticated endpoints using the JWT Bearer token.

---

## Security

The project includes:

* Password hashing
* JWT authentication
* Bearer token authentication
* Role-based authorization
* Protected user endpoints
* Protected order endpoints
* Admin-only product management
* User ownership checks
* Input validation with Pydantic
* Environment-based configuration
* `.env` excluded from version control

---

## Future Improvements

Possible improvements for a larger production system:

* Refresh tokens
* Email verification
* Password reset
* Rate limiting
* Redis caching
* Background tasks
* Payment integration
* Order history and admin dashboard
* Automated tests with Pytest
* Docker deployment
* CI/CD pipeline
* Production logging and monitoring

---

## License

This project was created as a backend portfolio project for learning and demonstrating modern Python backend development.
