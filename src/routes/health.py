import os
from fastapi import APIRouter
from fastapi.responses import Response
router = APIRouter()

@router.get('/')
async def get():
    """Should return version, other info"""
    return Response()

@router.get('/health')
async def health_check():
    return Response()

@router.get('/version', response_model=str)
async def health_check():
    ver = os.environ.get('APP_VERSION', 'no app version')
    return ver


@router.get('/{member_uid}')
async def test_send_email(member_uid: str):
    """Testing acquiring locks for transactions... i didn't like the way firestore handled locks."""
    # tasks = [test_transactions() for _ in range(10)]
    # await asyncio.gather(*tasks)
    return member_uid