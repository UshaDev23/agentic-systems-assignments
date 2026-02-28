from pydantic import BaseModel, EmailStr, Field, ValidationError, ConfigDict
from typing import Optional

class Address(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    city: str = Field(min_length = 3)
    pincode: str = Field(pattern=r'^\d{6}$')

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    user_id: int
    name: str
    email: EmailStr
    age: int = Field(ge = 18)
    address: Address
    is_premium: Optional[bool] = False


try:
    address_info = Address(city = "New Delhi", pincode = "400984")
    user_info = User(user_id = 1, name = "Maya Mathew", email = "maya.mathew@gmail.com", age = 25, address = address_info)
    print("User Details:")
    print(user_info)

except ValidationError as e:
    print("Validation Error:")
    print(e)