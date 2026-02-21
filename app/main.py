from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine, init_db
from app.routes import categories_router, documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    result = await init_db()
    print(
        f"""
        ===============================
        >>> {result}
        >>> Starting Editor Server
        Host: {settings.host}
        Port: {settings.port}
        ===============================
        """
    )
    yield
    await engine.dispose()  # Close DB connection
    print(
        f"""
        ===============================
        >>> Closing Editor Server
        Host: {settings.host}
        Port: {settings.port}
        ===============================
        """
    )


app = FastAPI(lifespan=lifespan)

app.include_router(categories_router)
app.include_router(documents_router)
