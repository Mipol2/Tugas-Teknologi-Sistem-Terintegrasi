from fastapi import APIRouter, HTTPException, status
from models.choices import Metal, Handle, Cutlery_Type
from typing import List
import json

choice_router = APIRouter(tags=["Choices"])

# Load data from the JSON file
with open("form.json", "r") as json_file:
    data = json.load(json_file)

metals = data.get("metals", [])
handles = data.get("handles", [])
cutlery_types = data.get("cutlery_types", [])

#GET
@choice_router.get("/metals", response_model=List[Metal])
async def retrieve_all_metals() -> List[Metal]:
    return metals

@choice_router.get("/hanldes", response_model=List[Handle])
async def retrieve_all_handles() -> List[Handle]:
    return handles

@choice_router.get("/types", response_model=List[Cutlery_Type])
async def retrieve_all_cutlery_types() -> List[Cutlery_Type]:
    return cutlery_types

