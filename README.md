# Ecommerce API (Django + DRF)

A Django REST Framework project for managing users, products, carts, and orders with role-based authentication (Manager and Customer).
Customers can browse and order products, while the Manager can manage products and view stock updates.

## Features

- User authentication system
  - Register (Required details username, strong password, unique email,unique phone number)
  - Login (should enter the username and password which was created while regestering)
  - Logout (Some user should be logged in before logout)
  - Update profile (username,email and phone number can be updated by logging in)
  - Delete account (Some user should be logged in before delete)
  - Manager Role Restriction
    - Only one manager can exist in the system
    - Manager can create, update, and delete products
    - Superuser should assign the manager role
- Product management (Manager only)
  - Add products (name, description, price, stock)
  - Update product details
  - Delete products
  - View product list (public)
  - View product details (public)
- Cart and Orders (Customer)
  - Add to cart (select product and quantity)
  - View cart
  - Delete from cart
  - Place order from cart
    - Automatically updates stock quantity after order is placed
    - Customers cannot see stock quantity (only Manager can)

---

## Stock Management Logic

- Manager adds product with initial stock (e.g., 25)
- Customer orders quantity (e.g., 5)
- Stock is automatically reduced (25 to 20)
- Stock updates are only visible to the manager

---

## Database

- PostgreSQL integration
- Custom User Model with is_manager field and unique manager constraint

---

## Technologies and Libraries Used

- Django (web framework for rapid backend development)
- Django REST Framework (for building REST APIs)
- PostgreSQL (relational database)
- datetime and timedelta (Python’s built-in library for handling date and time operations)
  - timedelta is used to represent differences between two dates or times, and perform operations such as adding or subtracting hours, days, or seconds from a timestamp.
- Asia/Kolkata Timezone (The application is configured to use the Indian Standard Time (IST) timezone for all datetime operations, ensuring consistency in timestamps for Indian users.)
- drf-yasg (for Swagger and Redoc API documentation)

---

## How to Run

- Ensure you have **Python 3.x** installed on your system.
- Ensure you have **Django 5.2.4** installed on your system.
- Ensure you have some app for PostgreSQL like PGAdmin.
- Download or clone this repository.
- Navigate to the project directory in the terminal.
- Run the local server.

---

## Install required dependencies:

- pip install -r requirements.txt
- python manage.py makemigrations
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py runserver

---

## API Documentation:

- Swagger UI is available at
  - http://127.0.0.1:8000/swagger/
- Redoc is available at
  - http://127.0.0.1:8000/redoc/
