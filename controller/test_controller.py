import os
import json

from fastapi import APIRouter, Depends

from utils.common.GeneralTool import GeneralTool
from utils.web.Req import Req, get_req
from utils.web.Resp import Resp

test_router = APIRouter(prefix="/test")


@test_router.get("/publicOpinionStart")
async def public_opinion_start_api(req: Req = Depends(get_req)):
    
    with open("@/data/xue_xiang/time_curve/anonymize_time_series_main_event.json".replace("@", GeneralTool.root_path),
              "r", encoding="utf-8") as f:
        anonymize_time_series_main_event = json.load(f)

    text_list = []
    for j, file_name in enumerate(os.listdir("@/data/xue_xiang/communities".replace("@", GeneralTool.root_path))):
        with open(
                f"@/data/xue_xiang/communities/{file_name}".replace("@", GeneralTool.root_path),
                "r", encoding="utf-8") as f:
            community_text_data = json.load(f)
            text_list.append(
                {
                    "id": j,
                    "name": file_name.rstrip(".json").lstrip("_").replace("community", "网络社区信息"),
                    "info": {
                        "mermaid_content": {
                            "name": "舆情推演内容",
                            "value": community_text_data["mermaid_content"].replace("<br>", "")
                        },
                        "keywords": {
                            "name": "关键词",
                            "value": community_text_data["keywords"]
                        },
                        "event": {
                            "name": "舆情具体事件",
                            "value": community_text_data["event"]
                        },
                    }
                }
            )

    data = {
        "title": "雪乡舆情系统结果",
        "text": text_list,
        "image": {
            "blog_num_time_curve": {
                "name": "博客数量时间趋势图",
                "url": f"{os.getenv('URL')}/file/data/xue_xiang/common/blog_num_time_curve.png"
            },
            "text_len": {
                "name": "博客文本长度分布图",
                "url": f"{os.getenv('URL')}/file/data/xue_xiang/common/text_len.png"
            },
            "community_plot": [
                {
                    "id": i,
                    "name": file_name.rstrip(".png").replace("community_plot", "社区网络图"),
                    "url": f"{os.getenv('URL')}/file/data/xue_xiang/community_plot/{file_name}"
                } for i, file_name in enumerate(os.listdir("@/data/xue_xiang/community_plot".replace("@", GeneralTool.root_path)))
            ],
            "time_curve": [
                {
                    "id": i,
                    "name": file_name.rstrip(".png")
                    .replace("heat_index_time_plot", "舆情具体事件平均热度指数曲线")
                    .replace("weighted_attitude_time_plot", "舆情具体事件加权平均立场倾向指数曲线")
                    .replace("weighted_emotion_change_time_plot", "舆情具体事件加权情感波动指数曲线")
                    .replace("weighted_emotion_time_plot", "舆情具体事件加权平均情感极性指数曲线"),
                    "legend": anonymize_time_series_main_event,
                    "url": f"{os.getenv('URL')}/file/data/xue_xiang/time_curve/{file_name}"
                } for i, file_name in enumerate(os.listdir("@/data/xue_xiang/time_curve".replace("@", GeneralTool.root_path))) if ".png" in file_name
            ],
        }
    }

    return Resp.build_success(body={
        "data": data
    })
