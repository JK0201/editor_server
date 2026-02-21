from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"""
        ===============================
        Starting Editor Server
        ===============================
        Host: {settings.host}
        Port: {settings.port}
        """
    )
    yield


app = FastAPI(lifespan=lifespan)
