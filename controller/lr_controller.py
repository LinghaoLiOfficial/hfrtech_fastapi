from fastapi import APIRouter, Depends

from service.lr.LRService import LRService
from utils.web.Req import Req, get_req

router = APIRouter(prefix="/lr")


@router.get("/verifyToken")
async def verify_token_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await LRService.verify_token(token=token)


@router.get("/getSalt")
async def get_salt_api(req: Req = Depends(get_req)):
    email = await req.receive_get_param("email")

    return await LRService.get_salt(email=email)


@router.post("/sendEmail")
async def send_email_api(req: Req = Depends(get_req)):
    email = await req.receive_post_param("email")

    return await LRService.send_email(email=email)


@router.post("/userLogin")
async def user_login_api(req: Req = Depends(get_req)):
    email = await req.receive_post_param("email")
    password = await req.receive_post_param("password")

    return await LRService.user_login(email=email, password=password)


@router.post("/userRegister")
async def user_register_api(req: Req = Depends(get_req)):
    email = await req.receive_post_param("email")
    hashed_password = await req.receive_post_param("hashedPassword")
    validation_code = await req.receive_post_param("validationCode")
    salt = await req.receive_post_param("salt")

    return await LRService.user_register(email=email, hashed_password=hashed_password, validation_code=validation_code, salt=salt)