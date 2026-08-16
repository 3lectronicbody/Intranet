from enum import Enum


API_PATH = "http://127.0.0.1:8000" # TODO ! ! !

class Role(Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"