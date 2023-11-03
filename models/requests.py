from pydantic import BaseModel
from typing	import List	

class Request(BaseModel):
    id: int
    username: str
    metal: str
    handle: str
    cutleryType: str
    quantity: int

