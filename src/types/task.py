class Task:
    """Represents a task in a task management system.
    Attributes:
        task_id (int): Snowflake ID of the task.
        name (str): Name of the task.
        description (str | None): Description of the task, can be None.
        date_created (int): Unix Timestamp when the task was created.
        date_deadline (int | None): Unix timestamp for the task deadline, can be None.
        date_completed (int | None): Unix Timestamp when the task was completed, can be None.
        assignees (list[int] | None): List of user IDs assigned to the task, can be None if no user has been assigned yet.
        current_column ("pool" | "in_progress" | "testing" | "done"): Current column of the task in the task management system.
    """
    def __init__(
        self,
        id: int,
        task_name: str,
        task_description: str | None = None,
        date_created: int = 0,
        date_deadline: int | None = None,
        date_completed: int | None = None,
        current_column: "pool" | "in_progress" | "testing" | "done" = "pool",
    ):
        self.task_id = id
        self.name = task_name
        self.description = task_description
        self.date_created = date_created
        self.date_deadline = date_deadline
        self.date_completed = date_completed
        self.current_column = current_column

    def __repr__(self):
        return f"Task(id={self.task_id}, name={self.name}, description={self.description}, date_created={self.date_created}, date_deadline={self.date_deadline}, date_completed={self.date_completed}, current_column={self.current_column})"
    
    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (
            self.task_id == other.task_id and
            self.name == other.name and
            self.description == other.description and
            self.date_created == other.date_created and
            self.date_deadline == other.date_deadline and
            self.date_completed == other.date_completed and
            self.current_column == other.current_column
        )
    
    def __hash__(self):
        return hash((self.task_id, self.name, self.description, self.date_created, self.date_deadline, self.date_completed, self.current_column))