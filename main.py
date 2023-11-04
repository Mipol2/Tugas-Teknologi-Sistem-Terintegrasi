from fastapi import	FastAPI
from routes.requests import	request_router
from routes.choices import choice_router
import	uvicorn

app	=	FastAPI()
app.include_router(request_router,	prefix="/requests")
app.include_router(choice_router,	prefix="/choices")

if	__name__	==	"__main__":	
    uvicorn.run("main:app",	host="0.0.0.0",	port=8000,	reload=True)