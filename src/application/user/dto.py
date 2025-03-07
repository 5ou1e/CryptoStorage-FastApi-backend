from fastapi_users import schemas
from pydantic import BaseModel, Field, model_validator


class UserRead(schemas.BaseUser[int]):
    username: str | None = Field(None, max_length=150)


class UserCreate(schemas.BaseUserCreate):
    username: str | None = Field(None, max_length=150)

    @model_validator(mode="before")
    def set_username(cls, data):
        # Устанавливаем email в username, если не передан
        if "username" not in data or not data["username"]:
            data["username"] = data["email"]
        return data


class UserUpdate(UserRead):
    pass


class UserResponse(BaseModel):
    username: str | None = Field(None, max_length=150)

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    data: list[UserResponse]
