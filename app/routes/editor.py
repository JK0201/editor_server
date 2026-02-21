from fastapi import APIRouter

router = APIRouter(
    prefix="/editor",
    tags=["editor"],
)


@router.get("")
async def test():
    return {"message": "Hello, World!"}
