from fastapi import FastAPI
from routes.requirements import requirement_router, choice_router
from routes.auth import auth_router

app = FastAPI()

app.include_router(requirement_router, prefix="/requirements")
app.include_router(choice_router, prefix="/choices")
app.include_router(auth_router)  # Include the authentication router