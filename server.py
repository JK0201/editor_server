import uvicorn

from app.core import settings

if __name__ == "__main__":
    uvicorn.run(
        app=settings.app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
