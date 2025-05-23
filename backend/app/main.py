from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import grid

app = FastAPI()

# Enable CORS for frontend (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include grid routes
app.include_router(grid.router)

@app.get("/")
def read_root():
    return {"message": "ML Driven Power Grid Management Backend"}