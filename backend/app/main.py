from fastapi import FastAPI

app = FastAPI(
    title="OmniBrain API",
    version="1.0.0"
)

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
    