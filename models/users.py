from pydantic import BaseModel

# Pydantic model for user registration
class UserIn(BaseModel):
    username: str
    password: str

# Pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Pydantic model for user data in JSON file
class UserJSON(BaseModel):
    id: int
    username: str
    password_hash: str
    is_admin: bool
