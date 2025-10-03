from fastapi import APIRouter, Depends

from service.mta.MTAService import MTAService
from utils.web.Req import Req, get_req

router = APIRouter(prefix="/sr")


@router.post("/frameLabeling")
async def frame_labeling_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await MTAService.frame_labeling(token=token)






