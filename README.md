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

## Installation
**Clone the repository**
```bash
git clone https://github.com/Pradi8/project.KanMind-backend.git
cd kanban-app

python -m venv venv
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

kanban_app/
├── models.py        # Boards, Tasks, Comments
├── views.py         # API views
├── serializers.py   # DRF serializers
├── urls.py

auth_app/
├── views.py         # Registration, login, logout
├── serializers.py   # DRF serializers
├── urls.py
├── permissions.py   # Custom permissions

manage.py
requirements.txt
README.md
