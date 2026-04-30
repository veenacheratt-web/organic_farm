# 🌱 Organic Fruits and Vegetables Selling WebApp

A full-featured e-commerce platform connecting organic farmers directly with consumers. Built with Django, Bootstrap 5, and SQLite.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [User Roles](#user-roles)

---

## 🎯 Project Overview

The **Organic Fruits and Vegetables Selling WebApp** is a web-based platform designed to eliminate intermediaries in the organic produce supply chain. It provides a transparent marketplace where:

- **Farmers** can showcase their organic products, manage inventory, and process orders
- **Customers** can browse, purchase, and review organic produce directly from verified farmers
- **Admins** can manage users, verify farmer credentials, and oversee platform operations

---

## ✨ Features

### 👨‍🌾 Farmer Features
- Farmer registration and profile management
- Product CRUD operations (Create, Read, Update, Delete)
- Inventory management with stock tracking
- View orders received for their products
- Update order status (Confirmed → Processing → Shipped → Delivered)
- Sales analytics dashboard
- Low stock alerts
- Public farmer storefront

### 👤 Customer Features
- Customer registration and profile management
- Browse products with search and filter
- Shopping cart management
- Secure checkout with multiple payment options
- Order history and tracking
- Write and edit product reviews
- Rate products (1-5 stars)
- Mark reviews as helpful

### 🔧 Admin Features
- User management (activate/deactivate)
- Farmer verification
- Order oversight
- Category management
- Platform analytics

### 🛒 General Features
- Responsive Bootstrap 5 design
- Role-based authentication
- Search and filter products by:
  - Category
  - Price range
  - Organic certification
  - Stock availability
- Pagination for product listings
- Session-based shopping cart
- Order status tracking
- Verified purchase reviews

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+ / Django 5.2 |
| **Database** | SQLite (development) / PostgreSQL (production) |
| **Frontend** | Django Templates + Bootstrap 5 |
| **Styling** | Custom CSS + Bootstrap Icons |
| **Forms** | Django Crispy Forms + Bootstrap 5 |
| **Authentication** | Django Custom User Model |
| **Images** | Pillow |
| **Payments** | Dummy Payment Gateway (COD + Card Sandbox) |
| **Deployment** | Gunicorn + Nginx / PythonAnywhere / Heroku |

### Required Python Packages

Django==5.2
pillow==11.0.0
django-crispy-forms==2.3
crispy-bootstrap5==2024.10

---

## 📁 Project Structure

- **organic_farm_project/**
  - `manage.py`
  - `requirements.txt`
  - `db.sqlite3`
  - **config/**
    - `__init__.py`
    - `settings.py`
    - `urls.py`
    - `wsgi.py`
  - **apps/**
    - **accounts/**
      - `__init__.py`
      - `admin.py`
      - `apps.py`
      - `models.py`
      - `views.py`
      - `urls.py`
      - `forms.py`
      - **migrations/**
    - **products/**
      - `__init__.py`
      - `admin.py`
      - `apps.py`
      - `models.py`
      - `views.py`
      - `urls.py`
      - `forms.py`
      - **migrations/**
    - **cart/**
      - `__init__.py`
      - `models.py`
      - `views.py`
      - `urls.py`
      - `forms.py`
      - `context_processors.py`
      - **migrations/**
    - **orders/**
      - `__init__.py`
      - `models.py`
      - `views.py`
      - `urls.py`
      - `forms.py`
      - **migrations/**
    - **reviews/**
      - `__init__.py`
      - `models.py`
      - `views.py`
      - `urls.py`
      - `forms.py`
      - **migrations/**
    - **pages/**
      - `__init__.py`
      - `views.py`
      - `urls.py`
  - **static/**
    - **css/**
      - `custom.css`
    - **js/**
      - `main.js`
  - **media/**
    - **products/**
    - **profile_pics/**
  - **templates/**
    - `base.html`
    - **accounts/**
    - **products/**
    - **cart/**
    - **orders/**
    - **reviews/**
    - **pages/**

## 🔥 Installation Guide
Prerequisites
Python 3.10 or higher

pip (Python package manager)

virtualenv (recommended)

Step 1: Clone the Repository

git clone https://github.com/veenacheratt/organic-farm-market.git
cd organic-farm-market

Step 2: Create Virtual Environment

## Windows
python -m venv venv
venv\Scripts\activate

## Step 3: Install Dependencies

pip install -r requirements.txt

## Step 4: Apply Migrations

python manage.py makemigrations
python manage.py migrate

## Step 5: Create Superuser (Admin)

python manage.py createsuperuser

## 🚀 Running the Application

python manage.py runserver

## 👥 User Roles
1. Administrator
Access to Django admin panel (/admin)

Manage all users and farmers

Verify farmer profiles

Oversee orders and products

2. Farmer
Register as farmer

Add/Edit/Delete products

Manage inventory

View orders for their products

Update order status

View sales analytics

3. Customer
Register as customer

Browse products

Add to cart and checkout

View order history

Write product reviews

Rate products