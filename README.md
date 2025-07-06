# Kanban Flask API

A RESTful API for managing users and tasks in a Kanban-style task management system, built with Flask and SQLAlchemy.

## Features

- User management (CRUD operations)
- Task management (CRUD operations)
- User-task assignments (many-to-many relationship)
- Password hashing with Argon2
- Snowflake ID generation
- SQLite database with SQLAlchemy ORM
- RESTful API endpoints

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### Users
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get a specific user
- `POST /api/users` - Create a new user
- `PUT /api/users/{id}` - Update a user
- `DELETE /api/users/{id}` - Delete a user

### Tasks
- `GET /api/tasks` - Get all tasks (optional: `?column=pool` to filter by column)
- `GET /api/tasks/{id}` - Get a specific task
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

### Task Assignments
- `POST /api/tasks/{id}/assign` - Assign a user to a task
- `POST /api/tasks/{id}/unassign` - Unassign a user from a task
- `GET /api/assignments` - Get all task assignments

### Authentication
- `POST /api/auth/login` - Authenticate a user

## Request/Response Examples

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword",
    "display_name": "John Doe",
    "profile_picture": "/assets/avatars/john.png"
  }'
```

### Create a Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Implement user authentication",
    "description": "Add login and registration functionality",
    "current_column": "pool",
    "assignees": [1, 2]
  }'
```

### Update Task Status
```bash
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "current_column": "in_progress"
  }'
```

### Assign User to Task
```bash
curl -X POST http://localhost:5000/api/tasks/1/assign \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

## Database Schema

### Users Table
- `id` (INTEGER PRIMARY KEY) - Snowflake ID
- `username` (VARCHAR(255) UNIQUE) - Username
- `password` (VARCHAR(255)) - Argon2id hashed password
- `display_name` (VARCHAR(255)) - Display name
- `profile_picture` (VARCHAR(500)) - Profile picture path
- `is_admin` (BOOLEAN) - Admin flag
- `date_created` (INTEGER) - Unix timestamp
- `created_at` (TIMESTAMP) - SQL timestamp

### Tasks Table
- `id` (INTEGER PRIMARY KEY) - Snowflake ID
- `name` (VARCHAR(255)) - Task name
- `description` (TEXT) - Task description
- `date_created` (INTEGER) - Unix timestamp
- `date_deadline` (INTEGER) - Unix timestamp
- `date_completed` (INTEGER) - Unix timestamp
- `current_column` (VARCHAR(20)) - Current column (pool, in_progress, testing, done)
- `created_at` (TIMESTAMP) - SQL timestamp

### User Task Assignments Table
- `id` (INTEGER PRIMARY KEY) - Assignment ID
- `user_id` (INTEGER) - Foreign key to users
- `task_id` (INTEGER) - Foreign key to tasks
- `assigned_at` (TIMESTAMP) - Assignment timestamp

## Task Columns

Tasks can be in one of four columns:
- `pool` - Task backlog
- `in_progress` - Currently being worked on
- `testing` - Being tested
- `done` - Completed tasks
