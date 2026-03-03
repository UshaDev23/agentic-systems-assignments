from pydantic import BaseModel, EmailStr, Field, ValidationError


class UserRegister(BaseModel):
    username: str = Field(..., min_length=5)
    email: EmailStr = Field(description = "Provide a valid email address", examples={"user@gmail.com"})
    age: int = Field(..., ge = 18)

try:
    user_info = {'username': 'John Mathew', 'email': 'johng@gmail.com', 'age': 18}
    user = UserRegister(**user_info)
    print(user)

except ValidationError as e:
    print(e)