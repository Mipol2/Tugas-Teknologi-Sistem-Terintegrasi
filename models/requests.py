from pydantic import BaseModel

class Request(BaseModel):
    id: int | None= None
    username: str
    metal: str
    handle: str
    cutlery_type: str
    quantity: int
    image_url: str | None= None

