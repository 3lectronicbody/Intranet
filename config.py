from enum import Enum


API_PATH = "http://192.168.0.4:8000"

class Role(Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"