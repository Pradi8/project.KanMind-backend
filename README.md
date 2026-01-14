# Kanban Board API

## Overview
Kanban Board API is a **Django REST Framework project** for managing boards, tasks, and comments with role-based permissions.  
It uses **Token Authentication** for secure access and supports a browsable API for development and testing.

---

## Features
- User registration, login, and logout
- CRUD operations for **Boards** and **Tasks**
- Commenting system for tasks
- Object-level permissions:
  - Only authors can edit their comments
  - Only admins or authors can delete comments
- Token-based authentication
- Browsable API for development

---

# Installation
## Follow these steps to set up the project locally:

## 1. Clone the repository
  git clone https://github.com/Pradi8/project.KanMind-backend.git <br>
  cd project.KanMind-backend

## 2. Create a virtual environment
  python -m venv env

## 3. Activate the virtual environment
  source env/bin/activate  # <b>Linux/Mac</b>  <br>
  env\Scripts\activate     # <b>Windows</b> 

## 4. Install Python dependencies
  pip install -r requirements.txt

## 5. Create database migrations
python manage.py makemigrations

## 6. Apply database migrations
  python manage.py migrate

## 7. Create a superuser (admin account)
  python manage.py createsuperuser

## 8. Start the development server
  python manage.py runserver  <br>
  The project will be running at http://127.0.0.1:8000/


# Project Structure
## kanban_app/
├── models.py        # Boards, Tasks, Comments <br>
├── views.py         # API views  <br>
├── serializers.py   # DRF serializers  <br>
├── urls.py

## auth_app/
├── views.py         # Registration, login, logout  <br>
├── serializers.py   # DRF serializers  <br>
├── urls.py  <br>
├── permissions.py   # Custom permissions

manage.py
requirements.txt
README.md
