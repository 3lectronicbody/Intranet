from enum import Enum


API_PATH = "..." # TODO ! ! !

class Role(Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"