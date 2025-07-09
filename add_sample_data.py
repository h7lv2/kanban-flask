#!/usr/bin/env python3
"""
Script to add sample data to the kanban database for testing.
"""

import time
from src.database import SessionLocal, init_db
from src.models import Task

def add_sample_tasks():
    """Add sample tasks to the database."""
    # Initialize database first
    init_db()
    
    db = SessionLocal()
    try:
        # Check if we already have tasks
        existing_tasks = db.query(Task).count()
        if existing_tasks > 0:
            print(f"Database already has {existing_tasks} tasks. Skipping sample data creation.")
            return

        # Create sample tasks
        sample_tasks = [
            Task(
                title="Пример задачи 1",
                description="Это примерная задача для демонстрации интерфейса lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                priority="high",
                deadline="2025-07-15",
                current_column="todo",
                date_created=int(time.time())
            ),
            Task(
                title="Изучить Vue 3",
                description="Освоить основы Vue 3 и Composition API",
                priority="medium",
                current_column="todo",
                date_created=int(time.time())
            ),
            Task(
                title="Разработка компонентов",
                description="Создание переиспользуемых компонентов для канбан-доски",
                priority="high",
                deadline="2025-07-12",
                current_column="progress",
                date_created=int(time.time())
            ),
            Task(
                title="Код-ревью",
                description="Проверка кода новых функций",
                priority="medium",
                current_column="review",
                date_created=int(time.time())
            ),
            Task(
                title="Настройка проекта",
                description="Первоначальная настройка Vue проекта с TypeScript",
                priority="low",
                current_column="done",
                date_created=int(time.time()),
                date_completed=int(time.time())
            ),
        ]

        # Add tasks to database
        for task in sample_tasks:
            db.add(task)
        
        db.commit()
        print(f"Successfully added {len(sample_tasks)} sample tasks to the database.")
        
        # Print added tasks
        for task in sample_tasks:
            print(f"- {task.title} ({task.current_column})")

    except Exception as e:
        db.rollback()
        print(f"Error adding sample tasks: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_tasks()
