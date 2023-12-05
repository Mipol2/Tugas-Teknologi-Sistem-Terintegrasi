from fastapi import FastAPI
from routes.requirements import requirement_router, choice_router
from routes.auth import auth_router
from routes.homeDesign import home_design_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Tambahkan middleware CORS ini ke instance aplikasi FastAPI Anda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Izinkan semua origin untuk tujuan pengembangan
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua metode
    allow_headers=["*"],  # Izinkan semua header
)

app.include_router(requirement_router, prefix="/requirements")
app.include_router(choice_router, prefix="/choices")
app.include_router(home_design_router, prefix="/home-design")
app.include_router(auth_router)  # Include the authentication router