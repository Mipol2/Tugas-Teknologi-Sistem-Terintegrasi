from fastapi import APIRouter, HTTPException
from models.requests import Request
from typing import List
import json

request_router = APIRouter(tags=["Requests"])

# Load data from the JSON file
with open("form.json", "r") as json_file:
    data = json.load(json_file)

requests = data.get("request", []) 


@request_router.get("/", response_model=List[Request])
async def retrieve_all_requests() -> List[Request]:
    return requests

@request_router.get("/{id}", response_model=Request)
async def retrieve_request(id: int) -> Request:
    for request in requests:
        if request.get("id") == id:
            return Request(**request)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Request with supplied ID does not exist"
    )

