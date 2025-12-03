from pydantic import BaseModel

class User(BaseModel):
    username: str
    roles: list[str]|None = None
    hash_psw: str|None = None
    session_token: str|None = None\
    
class User_registr(BaseModel):
    username: str
    password: str
    password_repeat: str

class UserPublic(BaseModel):
    username: str
    roles: list[str] | None = None

class Emb(BaseModel):
    text: str
    emb: list[int]

class TextIn(BaseModel):
    text: str