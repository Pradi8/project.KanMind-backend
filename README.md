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
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

## API Endpoints

| Endpoint                                      | Method                  | Description                                | 
| --------------------------------------------- | ----------------------- | ------------------------------------------ | 
| `/api/registration/`                          | POST                    | Register a new user                        | 
| `/api/login/`                                 | POST                    | Login and obtain token                     | 
| `/api/logout/`                                | POST                    | Logout user                                | 
| `/api/email-check/`                           | GET, POST               | Check if an email is already registered    | 
| `/api/boards/`                                | GET, POST               | List all boards or create a new board      | 
| `/api/boards/<int:pk>/`                       | GET, PUT, PATCH, DELETE | Retrieve, update, or delete a board by ID  | 
| `/api/tasks/`                                 | GET, POST               | List all tasks or create a new task        | 
| `/api/tasks/assigned-to-me/`                  | GET                     | List tasks assigned to the logged-in user  | 
| `/api/tasks/reviewing/`                       | GET                     | List tasks the logged-in user is reviewing | 
| `/api/tasks/<int:pk>/`                        | GET, PUT, PATCH, DELETE | Retrieve, update, or delete a task by ID   | 
| `/api/tasks/<int:task_pk>/comments/`          | GET, POST               | List or create comments for a task         | 
| `/api/tasks/<int:task_pk>/comments/<int:pk>/` | GET, PUT, PATCH, DELETE | Retrieve, update, or delete a comment      | 
| `/api-auth/login/`                            | GET, POST               | DRF Browsable API login (optional)         | 
| `/api-auth/logout/`                           | POST                    | DRF Browsable API logout (optional)        | 


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
