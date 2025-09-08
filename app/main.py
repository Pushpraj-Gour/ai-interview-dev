import asyncio
import uvicorn
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Query, Request,
                     status)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import project_api
from app.db.database import engine, Base

import logging
logging.basicConfig(format='%(asctime)s: [%(funcName)s]: %(message)s', level=logging.INFO, force=True)

from app.config import keys
from contextlib import asynccontextmanager

routers = [project_api.router]
app_name = 'Mock Interview Simulator - All APIs'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix=keys.api_prefix)
for router in routers:
    api_router.include_router(router)
app.include_router(api_router)

@app.get('/')
def health_check():
    return "OK"

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8081)