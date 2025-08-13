from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class ValidateEmailRequest(BaseModel):
    code: str

class LoginRequest(BaseModel):
    username: str
    password: str