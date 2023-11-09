from pydantic import BaseModel

# Models
class Metal(BaseModel):
    metal_id: int
    name: str
class Handle(BaseModel):
    handle_id: int
    name: str
class Cutlery_Type(BaseModel):
    type_id: int
    name: str

class ReqIn(BaseModel):
    username: str
    metal: str
    handle: str
    cutlery_type: str
    quantity: int
class Requirement(BaseModel):
    id: int
    username: str
    metal: str
    handle: str
    cutlery_type: str
    quantity: int
    image_url: str 