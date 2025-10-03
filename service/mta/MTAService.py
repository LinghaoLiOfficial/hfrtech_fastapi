import cv2
from PIL import ImageFont, ImageDraw, Image
import ast
import os
import numpy as np

from mapper.MTAMapper import MTAMapper
from service.mta.modules.VideoAnalyser import VideoAnalyser
from task.TaskManager import TaskManager
from utils.common.JWTParser import JWTParser
from utils.common.StrGenerator import StrGenerator
from utils.web.Resp import Resp


class MTAService:

    # TODO
    @classmethod
    async def frame_labeling(cls, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        mysql_result = await MTAMapper.select_frame_where_user_id({
            "user_id": user_id
        })
        frame_detail_list = sorted(mysql_result.get_data_on_results(), key=lambda v: v["frame_number"])

        color_palette = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 黄色
            (255, 0, 255),  # 紫色
            (0, 255, 255),  # 青色
            (255, 128, 0),  # 橙色
            (128, 0, 255),  # 紫罗兰
            (0, 255, 128),  # 青色
            (255, 0, 128),  # 粉红色
            (128, 255, 0),  # 青柠色
            (0, 128, 255)   # 天蓝色
        ]

        for frame_detail in frame_detail_list:
            # 读取图片
            image = cv2.imread(frame_detail['file_path'])
            if image is None:
                print(f"无法读取图片: {frame_detail['file_path']}")
                continue

            data_info_dict = ast.literal_eval(frame_detail['understanding_info'])

            # 为了处理中文和复杂的文本样式，我们将使用PIL进行文本绘制
            # 创建PIL图像副本用于绘制
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)

            # 尝试加载中文字体 (如果可用)
            try:
                font = ImageFont.truetype("simhei.ttf", 24)  # 黑体
            except:
                # 回退到默认字体
                font = ImageFont.load_default()

            entities = data_info_dict["entities"] + data_info_dict["texts"]
            # 为每个实体分配颜色
            for idx, entity in enumerate(entities):
                # 从调色板中循环选取颜色
                color_idx = idx % len(color_palette)
                bgr_color = color_palette[color_idx]
                rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])

                # 确保坐标是整数
                try:
                    top_left = (int(entity['bbox_2d'][0]), int(entity['bbox_2d'][1]))
                    bottom_right = (int(entity['bbox_2d'][2]), int(entity['bbox_2d'][3]))
                except Exception as e:
                    print(e)
                    continue

                # 使用PIL绘制矩形框
                draw.rectangle([top_left, bottom_right], outline=rgb_color, width=2)

                # 计算标签位置 - 在矩形框正上方
                box_width = bottom_right[0] - top_left[0]
                text = entity["label"] if "label" in entity.keys() else entity['text_content']

                # 获取文本尺寸
                try:
                    # 新版本Pillow使用textbbox
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except AttributeError:
                    # 旧版本Pillow使用textsize
                    text_width, text_height = draw.textsize(text, font=font)

                # 计算居中位置
                text_x = top_left[0] + (box_width - text_width) // 2
                text_y = top_left[1] - text_height - 10  # 在矩形框上方10像素

                # 确保文本在图片范围内
                if text_y < 0:
                    text_y = bottom_right[1] + 10  # 如果上方空间不足，放在下方

                # 使用PIL绘制文本
                draw.text((text_x, text_y), text, font=font, fill=rgb_color)

            # 将PIL图像转回OpenCV格式
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            # 确保输出目录存在
            output_dir = "storage/001/mta/test/"
            os.makedirs(output_dir, exist_ok=True)

            # 保存结果
            output_path = os.path.join(output_dir, f"{frame_detail['frame_id']}.jpg")
            cv2.imwrite(output_path, image)
            print(f"已保存: {output_path}")

    @classmethod
    def direct_analysis_video(cls, share_url):
        # # 解析token
        # jwt_parser_result = JWTParser.decode_user_id(token=token)
        # if not jwt_parser_result.status:
        #     return Resp.build_jwt_error(jwt_parser_result)
        # user_id = jwt_parser_result.get_data_on_results()

        user_id = StrGenerator.generate_uuid()

        task_id = StrGenerator.generate_uuid()
        video_analyser = VideoAnalyser(
            user_id=user_id,
            task_id=task_id
        )
        video_text_concept = video_analyser.direct_analysis_video(share_url)

        # task_manager = TaskManager()
        # qsize = await task_manager.add_task(
        #     video_analyser.direct_analysis_video,
        #     share_url=share_url
        # )

        return Resp.build_success(body={
            "video_text_concept": video_text_concept
        })

    @classmethod
    async def start_analysis_video(cls, share_url, token):
        # 解析token
        jwt_parser_result = JWTParser.decode_user_id(token=token)
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)
        user_id = jwt_parser_result.get_data_on_results()

        task_id = StrGenerator.generate_uuid()
        await MTAMapper.insert_task({
            "task_id": task_id,
            "belong_user_id": user_id,
            "task_name": "",  # TODO
        })

        video_analyser = VideoAnalyser(
            user_id=user_id,
            task_id=task_id
        )
        video_analyser.run(share_str=share_url)




