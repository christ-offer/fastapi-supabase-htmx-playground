from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str
    options: dict = {
        "is_admin": bool,
        "username": str,
        "first_name": str,
        "last_name": str,
    }
