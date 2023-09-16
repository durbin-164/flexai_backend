from typing import List

from pydantic import BaseModel


class UserRegistration(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    phone: str
    is_staff: bool
    roles: List[str]