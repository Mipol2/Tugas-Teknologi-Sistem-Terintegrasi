from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, Request
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
import json
import jwt
from models.requirements import Requirement, ReqInAdmin, ReqInUser, Metal, Handle, Cutlery_Type
from models.users import Token, UserIn, UserJSON

app = FastAPI()

JWT_SECRET = 'myjwtsecret'

# Load data from the JSON file
with open("requirement.json", "r") as json_file:
    data = json.load(json_file)

# Assign the tables
requirements = data.get("requirements", [])
metals = data.get("metals", [])
handles = data.get("handles", [])
cutlery_types = data.get("cutlery_types", [])

choice_router = APIRouter(tags=["Choices"])
requirement_router = APIRouter(tags=["Requirements"])

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
@app.get('/users/me', response_model=UserJSON)
async def get_user(user: UserJSON = Depends(get_current_user)):
    return user

# Route to register a new user
@app.post('/register', response_model=UserJSON)
async def register_user(user: UserIn):
    user_id = len(users_data) + 1
    password_hash = bcrypt.hash(user.password)
    
    is_admin = False
    if user.username == "jazmy":
        is_admin = True
        
    new_user = {"id": user_id, "username": user.username, "password_hash": password_hash, "is_admin": is_admin}
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

@requirement_router.get("/", response_model=List[Requirement])
async def retrieve_all_requirements(user: dict = Depends(get_current_user)) -> List[Requirement]:
    # Check if the user is an admin
    if user.is_admin:
        return requirements  # Return all requirements for admin
    else:
        # Only return requirements for the authenticated user
        user_requirements = [req for req in requirements if req.get("username") == user.username]
        return user_requirements

@requirement_router.get("/{id}", response_model=Requirement)
async def retrieve_requirement(id: int, user: UserJSON = Depends(get_current_user)) -> Requirement:
    # Check if the user is an admin or if the requirement belongs to the authenticated user
    requirement_data = next((req for req in requirements if req.get("id") == id), None)
    if user.is_admin or (requirement_data and requirement_data.get("username") == user["username"]):
        return Requirement(**requirement_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement with supplied ID does not exist or unauthorized access"
        )


#----------------------------------------------------------------#

#POST
@requirement_router.post("/new", response_model=Requirement)
async def create_requirement(
    requirement_user_data: Optional[ReqInUser] = None,
    requirement_admin_data: Optional[ReqInAdmin] = None,
    user: dict = Depends(get_current_user)
):
    if user.is_admin:
        if not requirement_admin_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="requirement_admin_data is required for admin user"
            )

        validate_input(requirement_admin_data, handles, "handle")
        validate_input(requirement_admin_data, metals, "metal")
        validate_input(requirement_admin_data, cutlery_types, "cutlery_type")

        requirement_id = len(requirements) + 1
        image_url = get_image_url(
            requirement_admin_data.metal,
            requirement_admin_data.handle,
            requirement_admin_data.cutlery_type
        )

        new_requirement = {
            "id": requirement_id,
            "username": requirement_admin_data.username,
            "metal": requirement_admin_data.metal,
            "handle": requirement_admin_data.handle,
            "cutlery_type": requirement_admin_data.cutlery_type,
            "quantity": requirement_admin_data.quantity,
            "image_url": image_url
        }
    else:
        if not requirement_user_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="requirement_user_data is required for regular user"
            )

        validate_input(requirement_user_data, handles, "handle")
        validate_input(requirement_user_data, metals, "metal")
        validate_input(requirement_user_data, cutlery_types, "cutlery_type")

        username = user.username
        requirement_id = len(requirements) + 1
        image_url = get_image_url(
            requirement_user_data.metal,
            requirement_user_data.handle,
            requirement_user_data.cutlery_type
        )

        new_requirement = {
            "id": requirement_id,
            "username": username,
            "metal": requirement_user_data.metal,
            "handle": requirement_user_data.handle,
            "cutlery_type": requirement_user_data.cutlery_type,
            "quantity": requirement_user_data.quantity,
            "image_url": image_url
        }

    requirements.append(new_requirement)
    # Write the updated data to the JSON file
    with open("requirement.json", "w") as json_file:
        data["requirements"] = requirements
        json.dump(data, json_file, indent=4)
    return new_requirement



#----------------------------------------------------------------#

#PUT
@requirement_router.put("/edit/{id}", response_model=Requirement)
async def update_requirement(id: int, requirement_data: Requirement):
    validate_input(requirement_data, handles, "handle")
    validate_input(requirement_data, metals, "metal")
    validate_input(requirement_data, cutlery_types, "cutlery_type")

    for existing_requirement in requirements:
        if existing_requirement.get("id") == id:
            # Update the fields of the existing requirement with the new data
            for key, value in requirement_data.dict().items():
                if key != "id":
                    existing_requirement[key] = value

            # Update the image_url based on the choices
            image_url = get_image_url(requirement_data.metal, requirement_data.handle, requirement_data.cutlery_type)
            existing_requirement["image_url"] = image_url

            # Write the updated data to the JSON file
            with open("requirement.json", "w") as json_file:
                data["requirement"] = requirements
                json.dump(data, json_file, indent=4)

            return Requirement(**existing_requirement)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Requirement with supplied ID does not exist"
    )

#----------------------------------------------------------------#

#DELETE
@requirement_router.delete("/delete/{id}")
async def delete_requirement(id: int):
    for requirement in requirements:
        if requirement.get("id") == id:
            requirements.remove(requirement)

            # Update the JSON data file
            with open("requirement.json", "w") as json_file:
                data["requirement"] = requirements
                json.dump(data, json_file, indent=4)

            return {
                "message": "Requirement deleted successfully"
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Requirement with supplied ID does not exist"
    )
#----------------------------------------------------------------#

#FUNCTIONS
def validate_input(requirement_data: Requirement, name_list, field_name):
    if requirement_data.dict().get(field_name) not in [name["name"] for name in name_list]:
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

app.include_router(requirement_router,	prefix="/requirements")
app.include_router(choice_router,	prefix="/choices")
