from fastapi import FastAPI
from api.routes import carbon

app = FastAPI(
    title="greenops",         
    description="greenops",   
    version="0.1.0",       
)

@app.get("/")
def root():
    return {"service": "GreenOps Carbon Engine",
        "version": "0.1.0",
        "docs": "/docs",}   

app.include_router(carbon.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}