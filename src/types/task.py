from typing import Literal

# Priority constants to match Vue frontend
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH]

# Column constants to match Vue frontend
COLUMN_TODO = "todo"
COLUMN_PROGRESS = "progress"
COLUMN_REVIEW = "review"
COLUMN_DONE = "done"
VALID_COLUMNS = [COLUMN_TODO, COLUMN_PROGRESS, COLUMN_REVIEW, COLUMN_DONE]

class Task:
    """Represents a task in a task management system.
    Attributes:
        task_id (int): Snowflake ID of the task.
        title (str): Title of the task.
        description (str): Description of the task.
        priority (Literal["low", "medium", "high"]): Priority level of the task.
        deadline (str | None): Deadline in YYYY-MM-DD format, can be None.
        date_created (int): Unix Timestamp when the task was created.
        date_completed (int | None): Unix Timestamp when the task was completed, can be None.
        assignees (list[int] | None): List of user IDs assigned to the task, can be None if no user has been assigned yet.
        current_column (Literal["todo", "progress", "review", "done"]): Current column of the task in the task management system.
    """
    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        priority: Literal["low", "medium", "high"] = "medium",
        deadline: str | None = None,
        date_created: int = 0,
        date_completed: int | None = None,
        current_column: Literal["todo", "progress", "review", "done"] = "todo",
    ):
        self.task_id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.date_created = date_created
        self.date_completed = date_completed
        self.current_column = current_column

    def __repr__(self):
        return f"Task(id={self.task_id}, title={self.title}, description={self.description}, priority={self.priority}, deadline={self.deadline}, date_created={self.date_created}, date_completed={self.date_completed}, current_column={self.current_column})"
    
    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (
            self.task_id == other.task_id and
            self.title == other.title and
            self.description == other.description and
            self.priority == other.priority and
            self.deadline == other.deadline and
            self.date_created == other.date_created and
            self.date_completed == other.date_completed and
            self.current_column == other.current_column
        )
    
    def __hash__(self):
        return hash((self.task_id, self.title, self.description, self.priority, self.deadline, self.date_created, self.date_completed, self.current_column))