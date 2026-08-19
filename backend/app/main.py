from fastapi import FastAPI

from backend.app.api.chat import router as chat_router

app = FastAPI(
    title="OmniBrain API",
    version="1.0.0"
)

app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "OmniBrain Backend is Running!"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }    
