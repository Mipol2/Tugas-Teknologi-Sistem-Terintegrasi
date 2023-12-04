from fastapi import APIRouter, HTTPException, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer
import requests
from .auth import Token, get_current_user
from pydantic import BaseModel
from models.users import UserJSON
from routes.auth import get_current_user

# Pydantic model for user registration
class DesignData(BaseModel):
    designname: str
    deskripsi: str
    tanggalpesan: str
    status: str
    namadesainer: str
    nohp: str

home_design_router = APIRouter(tags=["Home Design"])
JWT_SECRET = 'myjwtsecret'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
# Corrected base URL with the http:// or https:// prefix
FRIENDS_API_BASE_URL = "http://127.0.0.1:8000" 


@home_design_router.post("/create")
async def create_home_design(
    token: str = Depends(oauth2_scheme),  # Use OAuth2 token for authentication
    desainname: str = Form(...),
    deskripsi: str = Form(...),
    tanggalpesan: str = Form(...),
    status: str = Form(...),
    namadesainer: str = Form(...),
    nohp: str = Form(...),
    user: UserJSON = Depends(get_current_user) 
):
    # Obtain the integrasi_token based on the user's token
    integrasi_token = user.integrasi_token
    
    # Use integrasi_token for authentication with your friend's service
    headers = {"Authorization": f"Bearer {integrasi_token}"}
    
    form_data = {
        "desainname": desainname,
        "deskripsi": deskripsi,
        "tanggalpesan": tanggalpesan,
        "status": status,
        "namadesainer": namadesainer,
        "nohp": nohp,
    }
    
    response = requests.post(f"{FRIENDS_API_BASE_URL}/alldata", data=form_data, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error creating home design.")
    
    return response.json()


@home_design_router.get("/{id}")
async def get_home_design(id: int, token: str = Depends(oauth2_scheme)):
    # Get the current user based on the token
    user = await get_current_user(token)

    # Obtain the integrasi_token from the current user
    integrasi_token = user.integrasi_token

    # Use integrasi_token for authentication with your friend's service
    headers = {"Authorization": f"Bearer {integrasi_token}"}
    response = requests.get(f"{FRIENDS_API_BASE_URL}/desain", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error retrieving home design.")

    return response.json()