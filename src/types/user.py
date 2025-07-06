class User:
    """Represents a user in the Kanban application.
    Attributes:
        id (int): Snowflake ID of the user.
        username (str): Username of the user.
        password (str): argon2id password of the user.
        display_name (str): Display name of the user.
        profile_picture (str): URL or path to the user's profile picture at ./assets/avatars/<snowflake>.<extension>.
        tasks_assigned (list[int] | None): List of task IDs assigned to the user, can be None if no tasks are assigned.
        is_admin (bool): Flag indicating if the user is an admin.
        date_created (int): Unix Timestamp when the user was created.
    """    
    def __init__(
        self,
        id: int,
        username: str,
        password: str,
        display_name: str,
        profile_picture: str,
        tasks_assigned: list[int] | None = None,
        is_admin: bool = False,
        date_created: int = 0,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.display_name = display_name
        self.profile_picture = profile_picture
        self.tasks_assigned = tasks_assigned if tasks_assigned is not None else []
        self.is_admin = is_admin
        self.date_created = date_created
    
    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, display_name={self.display_name}, profile_picture={self.profile_picture}, tasks_assigned={self.tasks_assigned}, is_admin={self.is_admin}, date_created={self.date_created})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return (
            self.id == other.id and
            self.username == other.username and
            self.password == other.password and
            self.display_name == other.display_name and
            self.profile_picture == other.profile_picture and
            self.tasks_assigned == other.tasks_assigned and
            self.is_admin == other.is_admin and
            self.date_created == other.date_created
        )
    
    def __hash__(self):
        return hash((self.id, self.username, self.password, self.display_name, self.profile_picture, tuple(self.tasks_assigned), self.is_admin, self.date_created))
    

