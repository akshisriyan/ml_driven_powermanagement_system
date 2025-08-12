from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import grid, auth, billing

app = FastAPI()

# Enable CORS for frontend (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(grid.router)
app.include_router(billing.router)

@app.get("/")
def read_root():
    return {"message": "ML Driven Power Grid Management Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)