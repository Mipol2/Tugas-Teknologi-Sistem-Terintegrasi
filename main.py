from fastapi import	FastAPI
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from typing import List
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from pydantic import BaseModel
import json
import jwt

app = FastAPI()

JWT_SECRET = 'myjwtsecret'

# Pydantic model for user registration
class UserIn(BaseModel):
    username: str
    password: str

# Pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Pydantic model for user data in JSON file
class UserJSON(BaseModel):
    id: int
    username: str
    password_hash: str
    is_admin: bool = False


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

class RequestIn(BaseModel):
    username: str
    metal: str
    handle: str
    cutlery_type: str
    quantity: int
class Request(BaseModel):
    id: int
    username: str
    metal: str
    handle: str
    cutlery_type: str
    quantity: int
    image_url: str 
    
    # class Config:
    #     schema_extra={
    #         "example":{
    #             "username": "myusername",
    #             "metal": "Silver",
    #             "handle": "Wood",
    #             "cutlery_type": "Spoon",
    #             "quantity": 10
    #         }
    #     }

# Load data from the JSON file
with open("form.json", "r") as json_file:
    data = json.load(json_file)

# Assign the tables
requests = data.get("request", [])
metals = data.get("metals", [])
handles = data.get("handles", [])
cutlery_types = data.get("cutlery_types", [])

choice_router = APIRouter(tags=["Choices"])
request_router = APIRouter(tags=["Requests"])

# Load user data from JSON file
with open("users.json", "r") as json_file:
    users_data = json.load(json_file)

# Function to write user data to JSON file
def write_users_to_json():
    with open("users.json", "w") as json_file:
        json.dump(users_data, json_file, indent=4)

# Function to authenticate and get user
def authenticate_user(username: str, password: str):
    for user in users_data:
        if user['username'] == username and bcrypt.verify(password, user['password_hash']):
            return user
    return None

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# Route to generate token
@app.post('/token', response_model=Token)
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
        user = next((u for u in users_data if u['id'] == payload['id']), None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail='Invalid username or password'
            )
        return user  # Return the user dictionary directly
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )


# Route to get current user
@app.get('/users/me', response_model=UserJSON)
async def get_user(user: UserJSON = Depends(get_current_user)):
    return user

# Route to register a new user
@app.post('/register', response_model=UserJSON)
async def register_user(user: UserIn):
    if user.username == "jazmy":
        is_admin = True
    user_id = len(users_data) + 1
    password_hash = bcrypt.hash(user.password)
    new_user = {"id": user_id, "username": user.username, "password_hash": password_hash, user.is_admin:is_admin}
    users_data.append(new_user)
    write_users_to_json()
    return new_user


#GET
@choice_router.get("/metals", response_model=List[Metal])
async def retrieve_all_metals() -> List[Metal]:
    return metals

@choice_router.get("/handles", response_model=List[Handle])
async def retrieve_all_handles() -> List[Handle]:
    return handles

@choice_router.get("/types", response_model=List[Cutlery_Type])
async def retrieve_all_cutlery_types() -> List[Cutlery_Type]:
    return cutlery_types


#GET
@request_router.get("/", response_model=List[Request])
async def retrieve_all_requests(user: dict = Depends(get_current_user)) -> List[Request]:
    # Check if the user is an admin
    is_admin = user.get("is_admin", False)
    if is_admin:
        return requests  # Return all requests for admin
    else:
        # Only return requests for the authenticated user
        user_requests = [req for req in requests if req.get("username") == user["username"]]
        return user_requests

@request_router.get("/{id}", response_model=Request)
async def retrieve_request(id: int, user: UserJSON = Depends(get_current_user)) -> Request:
    # Check if the user is an admin or if the request belongs to the authenticated user
    request_data = next((req for req in requests if req.get("id") == id), None)
    if user.is_admin or (request_data and request_data.get("username") == user["username"]):
        return Request(**request_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request with supplied ID does not exist or unauthorized access"
        )


#----------------------------------------------------------------#

#POST
@request_router.post("/new", response_model=Request)
async def create_request(request_data: RequestIn):
    validate_input(request_data, handles, "handle")
    validate_input(request_data, metals, "metal")
    validate_input(request_data, cutlery_types, "cutlery_type")

    # # Check if the requests list is empty
    # if requests:
    #     # The list is not empty, so you can proceed to find the max ID
    #     max_id = max(requests, key=lambda request: request["id"])["id"]
    #     new_id = max_id + 1
    # else:
    #     # The list is empty, so you can start with a new ID of 1
    #     new_id = 1
    # request_data.id = new_id

    # # Get the image URL based on the choices and add it to the request
    # image_url = get_image_url(request_data.metal, request_data.handle, request_data.cutlery_type)
    # request_data.image_url = image_url

    # # Append the new request to the list
    # requests.append(request_data.dict())

    # # Write the updated data to the JSON file
    # with open("form.json", "w") as json_file:
    #     data["request"] = requests
    #     json.dump(data, json_file, indent=4)

    request_id = len(requests) + 1
    image_url = get_image_url(request_data.metal, request_data.handle, request_data.cutlery_type)
    new_request = {"id": request_id, "username": request_data.username, "metal": request_data.metal, "handle": request_data.handle, "cutlery_type": request_data.cutlery_type, "quantity": request_data.quantity, "image_url": image_url}
    requests.append(new_request)
    write_users_to_json()
    return new_request


#----------------------------------------------------------------#

#PUT
@request_router.put("/edit/{id}", response_model=Request)
async def update_request(id: int, request_data: Request):
    validate_input(request_data, handles, "handle")
    validate_input(request_data, metals, "metal")
    validate_input(request_data, cutlery_types, "cutlery_type")

    for existing_request in requests:
        if existing_request.get("id") == id:
            # Update the fields of the existing request with the new data
            for key, value in request_data.dict().items():
                if key != "id":
                    existing_request[key] = value

            # Update the image_url based on the choices
            image_url = get_image_url(request_data.metal, request_data.handle, request_data.cutlery_type)
            existing_request["image_url"] = image_url

            # Write the updated data to the JSON file
            with open("form.json", "w") as json_file:
                data["request"] = requests
                json.dump(data, json_file, indent=4)

            return Request(**existing_request)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Request with supplied ID does not exist"
    )

#----------------------------------------------------------------#

#DELETE
@request_router.delete("/delete/{id}")
async def delete_request(id: int):
    for request in requests:
        if request.get("id") == id:
            requests.remove(request)

            # Update the JSON data file
            with open("form.json", "w") as json_file:
                data["request"] = requests
                json.dump(data, json_file, indent=4)

            return {
                "message": "Request deleted successfully"
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Request with supplied ID does not exist"
    )
#----------------------------------------------------------------#

#FUNCTIONS
def validate_input(request_data: Request, name_list, field_name):
    if request_data.dict().get(field_name) not in [name["name"] for name in name_list]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} not found in the list"
        )
    
def get_image_url(metal: str, handle: str, cutlery_type: str) -> str:
    # Define a dictionary that maps choices to image URLs
    image_urls = {
        ("Silver", "Plastic", "Spoon"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251885895221248/image.png?ex=65585cff&is=6545e7ff&hm=35ce0d41b0a05edd757f4933f7464cef81d86a5dbc7c5aa63d079d894eef86e6&",
        ("Silver", "Plastic", "Fork"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251192945877022/2Q.png?ex=65585c5a&is=6545e75a&hm=10c864dd7a63859ba07959b8ea5412f17ef77af10c8d39dbd85253ddc4977ae1&",
        ("Silver", "Plastic", "Knife"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170248662912340029/51v6Oc0aJ4L.png?ex=655859ff&is=6545e4ff&hm=94d95f49a27416e26fe4b1ae956bb8031180dc249df6a6a86eab0fd46f8e8a18&",
        ("Silver", "Wood", "Spoon"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251951238291598/stainless-steel-spoon-wood-handle-500x500.png?ex=65585d0f&is=6545e80f&hm=bf8d766da91daf6604761d99759a911585e254928a559b48236559999991002b&",
        ("Silver", "Wood", "Fork"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170250147846959114/DALLE_2023-11-04_13.35.31_-_wood_handle_silver_fork_with_white_background.png?ex=65585b61&is=6545e661&hm=f354bfa6fed8d52668e25bd139c6caaa75721ac651040c09bd436639b2db3210&",
        ("Silver", "Wood", "Knife"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170248812804178030/4b90bae6-95a3-4633-901c-dd2ea06d4079_1200x1200.png?ex=65585a23&is=6545e523&hm=3bdc221f66aa612d84fa3aa7342fc7fe4a05d4feebff2e71089e46217b1bea6c&",
        ("Stainless Steel", "Plastic", "Spoon"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251787270377495/slpba211.png?ex=65585ce8&is=6545e7e8&hm=99166ab01788d46eae608128ff745d6f20b1bda84fd7fa8c1da3bbb69a22e6c7&",
        ("Stainless Steel", "Plastic", "Fork"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251199279288360/images.png?ex=65585c5c&is=6545e75c&hm=74c0d129252bafd4bbd5a34cf4e422ff59049eb591bd51c4066a7316ea21167f&",
        ("Stainless Steel", "Plastic", "Knife"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170248899919872070/415IEhFdYtL.png?ex=65585a37&is=6545e537&hm=b8d57c9c5dad0ec72e213b2b9cd6e9bdd9c3eebc82da7607a822831597c53f6b&",
        ("Stainless Steel", "Wood", "Spoon"): "https://media.discordapp.net/attachments/1170248640145670164/1170251681586491453/417djo180-L.png?ex=65585ccf&is=6545e7cf&hm=03d35e08dabb4d79194c45b656bf8a144c0708d268128742d0cd95367430339d&=&width=656&height=656",
        ("Stainless Steel", "Wood", "Fork"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170251578230452245/1957080.png?ex=65585cb6&is=6545e7b6&hm=eeee1586eb04ddc3d001e96d890640ef54c6254a4ebb3b80ab253833f7066e2d&",
        ("Stainless Steel", "Wood", "Knife"): "https://cdn.discordapp.com/attachments/1170248640145670164/1170249065523597312/1823130.png?ex=65585a5f&is=6545e55f&hm=bb5b5aabe6d2dd0a6188860ac01adb8bebc5e24b79379c9dc9e2cbd8b3a79755&",
        # Add more entries for other choices
    }

    # Check if the combination of choices exists in the dictionary
    image_url = image_urls.get((metal, handle, cutlery_type))

    return image_url

app.include_router(request_router,	prefix="/requests")
app.include_router(choice_router,	prefix="/choices")
