from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(max_length = 5)
    email: EmailStr = Field(description = "Provide a valid email address", examples={"user@gmail.com"})
    age: int = Field(ge = 18)

user_info = {'username': 'John', 'email': 'johng@gmail.com', 'age': 18}
user = UserRegister(**user_info)
print(user)