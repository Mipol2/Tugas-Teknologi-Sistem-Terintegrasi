from pydantic import BaseModel
from typing	import List, Optional

class Metal(BaseModel):
    metal_id: int
    name: str
class Handle(BaseModel):
    handle_id: int
    name: str
class Cutlery_Type(BaseModel):
    type_id: int
    name: str
