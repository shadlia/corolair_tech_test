from fastapi import FastAPI
from routes import upload, retrieve, answer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Corolair Technical Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["Retrieve"])
app.include_router(answer.router, prefix="/answer", tags=["Answer"])


@app.get("/")
def root():
    return {
        "success": True,
        "data": {"Message": "hello its me Chadlia :) "},
    }
