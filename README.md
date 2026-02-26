# Task Manager API

A RESTful Task Manager API built using **FastAPI**, **SQLAlchemy 2.0 (Async)**, **SQLite**, and **Alembic**.

This project demonstrates a properly structured backend application with CRUD operations, filtering, sorting, pagination, and environment-based configuration.

---

## Features

* Create, Read, Update, Delete tasks
* Filter by status & priority
* Sorting (ascending / descending)
* Pagination support
* Async SQLAlchemy integration
* Alembic database migrations
* Pydantic v2 validation
* Environment-based configuration
* Swagger API documentation

---

## Tech Stack

* FastAPI
* SQLAlchemy 2.0 (Async)
* SQLite
* Alembic
* Pydantic v2
* Uvicorn

---

## Project Structure

```
task_manager_api/
│
├─ app/
│  ├─ main.py
│  ├─ database.py
│  ├─ config.py
|
│  ├─ routers/
│  │   └─ task.py
|
│  ├─ models/
│  │   └─ task.py
|
│  └─ schemas/
│      └─ task.py
│
|   └─ __init__.py  (in every folder)
|
├─ alembic/
|  alembic.ini
├─ task_manager.db
├─ requirements.txt
└─ README.md

```
---

## Setup Instructions

### 1. Clone project & enter folder

```
git clone https://github.com/MuhammadKhuzaimaIqbal/task-manager-service.git
cd task_manager_api

```

### 2. Create virtual environment

```
python -m venv venv 
venv\Scripts\activate

```

### 3. Install dependencies

```
pip install -r requirements.txt

```

### 4. Run migrations

```
alembic upgrade head

```

### 5. Start server

```
uvicorn app.main:app --reload

```

Server will run at:

```
http://127.0.0.1:8000

```

Swagger Docs:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Create Task

POST /tasks

### Get All Tasks

GET /tasks

Query Parameters:

* status
* priority
* sort_by
* order
* page
* page_size

### Get Task By ID

GET /tasks/{task_id}

### Update Task

PUT /tasks/{task_id}

### Delete Task

DELETE /tasks/{task_id}

---

## Example Request

```
POST /tasks
{
  "title": "Learn FastAPI",
  "description": "Build a CRUD project",
  "status": "todo",
  "priority": "high",
  "due_date": "2026-03-01T10:00:00"
}

```

---

## HTTP Status Codes

* 201 → Created
* 204 → Deleted
* 404 → Not Found
* 422 → Validation Error

---

## Author

Muhammad Khuzaima
