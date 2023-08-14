from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_name: str
    password: str
    first_name: str
    last_name: str
