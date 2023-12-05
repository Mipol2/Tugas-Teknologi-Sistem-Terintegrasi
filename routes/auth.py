from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
import jwt
import json
from models.users import Token, UserIn, UserJSON
import requests
from fastapi.templating import Jinja2Templates

# Corrected base URL with the http:// or https:// prefix
FRIENDS_API_BASE_URL = "http://127.0.0.1:8000" 

# Load user data from JSON file
with open("data/users.json", "r") as json_file:
    users_data = json.load(json_file)

auth_router = APIRouter(tags=["Authentication"])
JWT_SECRET = 'myjwtsecret'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Function to write user data to JSON file
def write_users_to_json():
    with open("data/users.json", "w") as json_file:
        json.dump(users_data, json_file, indent=4)

# Function to authenticate and get user
def authenticate_user(username: str, password: str):
    for user in users_data:
        if user['username'] == username and bcrypt.verify(password, user['password_hash']):
            return user
    return None

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

templates = Jinja2Templates(directory="./Frontend")

@auth_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route to generate token
@auth_router.post('/token', response_model=Token)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    token_data = {"sub": user['username'], "id": user['id']}
    token = jwt.encode(token_data, JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('id')
        user = next((u for u in users_data if u['id'] == user_id), None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail='Invalid user'
            )
        return UserJSON(**user)  # Convert user dictionary to User Pydantic model
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid token'
        )

# Route to get current user
@auth_router.get('/users/me', response_model=UserJSON)
async def get_user(user: UserJSON = Depends(get_current_user)):
    return user

# Route to register a new user
@auth_router.post('/register', response_model=UserJSON)
async def register_user_and_friends(user: UserIn):
    # Register the user in your own service
    user_id = len(users_data) + 1
    password_hash = bcrypt.hash(user.password)
    
    is_admin = False
    if user.username == "jazmy":
        is_admin = True

    # Register the user in your friend's API using URL parameters
    response = requests.post(f"{FRIENDS_API_BASE_URL}/users", params={"username": user.username, "password": user.password})
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error registering user with your friend's API.")
    
    # Obtain a token from your friend's API
    token_response = requests.post(f"{FRIENDS_API_BASE_URL}/token", data={"username": user.username, "password": user.password})
    
    if token_response.status_code == 200:
        integrasi_token = token_response.json().get("access_token")
    else:
        raise HTTPException(status_code=token_response.status_code, detail="Error obtaining token from your friend's API.")
    
    # Store the integration token in your user data
    new_user = {"id": user_id, "username": user.username, "password_hash": password_hash, "is_admin": is_admin, "integrasi_token": integrasi_token}
    users_data.append(new_user)
    write_users_to_json()
    
    return new_user
