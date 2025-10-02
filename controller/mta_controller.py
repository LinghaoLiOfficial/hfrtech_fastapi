from fastapi import APIRouter, Depends

from service.mta.MTAService import MTAService
from utils.web.Req import Req, get_req

router = APIRouter(prefix="/mta")


# TODO
@router.post("/frameLabeling")
async def frame_labeling_api(req: Req = Depends(get_req)):
    token = await req.receive_header_token()

    return await MTAService.frame_labeling(token=token)


@router.post("/startAnalysisVideo")
async def start_analysis_video_api(req: Req = Depends(get_req)):
    share_url = await req.receive_post_param("shareUrl")
    token = await req.receive_header_token()

    return await MTAService.start_analysis_video(share_url=share_url, token=token)






