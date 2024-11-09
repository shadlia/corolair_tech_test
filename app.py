from fastapi import FastAPI
from routes import upload, retrieve, answer

app = FastAPI(title="Corolair Technical Test")


app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["Retrieve"])
app.include_router(answer.router, prefix="/answer", tags=["Answer"])


@app.get("/")
def root():
    return {"message": "Hi its me Chadlia :) !"}
