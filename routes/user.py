
from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Depends


from config.jwt_bearer import JWTBearer
from config.jwt_handler import sign_jwt, decode_jwt
from schemas.user import UserData
from service.user_service import get_current_user

router = APIRouter()


@router.get("", response_model=UserData)
async def detail_user(token: str = Depends(JWTBearer())):
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token: user_id not found")

    user_data = await get_current_user(user_id)
    print(user_data)
    return user_data

