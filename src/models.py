from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """SQLAlchemy model for users table."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Argon2id hashed password
    display_name = Column(String(255), nullable=False)
    profile_picture = Column(String(500))
    is_admin = Column(Boolean, nullable=False, default=False)
    date_created = Column(Integer, nullable=False)  # Unix timestamp
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationship to tasks through bridge table
    task_assignments = relationship("UserTaskAssignment", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the user to a dictionary."""
        return {
            'id': str(self.id),  # Convert to string to prevent JS precision loss
            'username': self.username,
            'display_name': self.display_name,
            'profile_picture': self.profile_picture,
            'is_admin': self.is_admin,
            'date_created': self.date_created,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tasks_assigned': [str(assignment.task_id) for assignment in self.task_assignments]  # Convert to strings
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', display_name='{self.display_name}')>"


class Task(Base):
    """SQLAlchemy model for tasks table."""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)  # Changed from 'name' to 'title'
    description = Column(Text, nullable=False, default='')  # Made non-nullable with default
    priority = Column(String(10), nullable=False, default='medium')  # Added priority field: 'low', 'medium', 'high'
    deadline = Column(String(10))  # Changed to string format (YYYY-MM-DD) to match Vue
    date_created = Column(Integer, nullable=False)  # Unix timestamp
    date_completed = Column(Integer)  # Unix timestamp
    current_column = Column(String(20), nullable=False, default='todo')  # Changed default from 'pool' to 'todo'
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationship to users through bridge table
    user_assignments = relationship("UserTaskAssignment", back_populates="task", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the task to a dictionary."""
        return {
            'id': str(self.id),  # Convert large IDs to strings to prevent JS precision loss
            'title': self.title,  # Changed from 'name' to 'title'
            'description': self.description,
            'priority': self.priority,  # Added priority field
            'deadline': self.deadline,  # Changed from 'date_deadline' to 'deadline'
            'date_created': self.date_created,
            'date_completed': self.date_completed,
            'current_column': self.current_column,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'assignees': [str(assignment.user_id) for assignment in self.user_assignments]  # Convert to strings
        }
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', column='{self.current_column}')>"


class UserTaskAssignment(Base):
    """SQLAlchemy model for user_task_assignments bridge table."""
    __tablename__ = 'user_task_assignments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    assigned_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="task_assignments")
    task = relationship("Task", back_populates="user_assignments")
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (UniqueConstraint('user_id', 'task_id', name='unique_user_task'),)
    
    def to_dict(self):
        """Convert the assignment to a dictionary."""
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'task_id': str(self.task_id),
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None
        }
    
    def __repr__(self):
        return f"<UserTaskAssignment(user_id={self.user_id}, task_id={self.task_id})>"
