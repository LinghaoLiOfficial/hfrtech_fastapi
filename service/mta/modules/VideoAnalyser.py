import re
import requests
import cv2
import os
import numpy as np
from tqdm import tqdm

from mapper.MTAMapper import MTAMapper
from service.mta.modules.VideoDownloader import VideoDownloader
from utils.common.GeneralTool import GeneralTool
from utils.common.StrGenerator import StrGenerator
from utils.llm_api.LLMServiceClient import LLMServiceClient


class VideoAnalyser:

    service_douyin_base_url = f"https://douyin.wtf"
    # service_douyin_base_url = f"http://localhost:7475"

    def __init__(self, user_id, task_id):
        self.user_id = user_id
        self.task_id = task_id

    def run(self, share_str):
        task_folder_path = f"{GeneralTool.root_path}/storage/{self.user_id}/mta/{self.task_id}"
        if not os.path.exists(task_folder_path):
            os.makedirs(task_folder_path, exist_ok=True)
        video_task_folder_path = f"{GeneralTool.root_path}/storage/{self.user_id}/mta/{self.task_id}/video"
        if not os.path.exists(video_task_folder_path):
            os.makedirs(video_task_folder_path, exist_ok=True)
        frame_task_folder_path = f"{GeneralTool.root_path}/storage/{self.user_id}/mta/{self.task_id}/frame"
        if not os.path.exists(frame_task_folder_path):
            os.makedirs(frame_task_folder_path, exist_ok=True)

        share_url = self.extract_share_url_from_str(share_str)
        aweme_id = self.get_aweme_id_from_share_url(share_url)
        video_url = self.get_video_url_from_aweme_id(aweme_id)
        video_id = self.download_video(video_url=video_url)
        frame_id_list = self.extract_frames_from_video_url(
            video_id=video_id,
            frames_per_second=1
        )
        self.understand_frames(frame_id_list=frame_id_list)

    def understand_frames(self, frame_id_list):
        for frame_id in tqdm(frame_id_list, desc="image understanding..."):
            mysql_result = MTAMapper.sync_select_frame_where_frame_id({
                "frame_id": frame_id
            })
            frame_file_path = mysql_result.get_data_on_results()[0]["file_path"]
            frame_info_dict = LLMServiceClient.locate_and_understand_img(frame_file_path)
            MTAMapper.sync_update_frame_on_understanding_info({
                "understanding_info": str(frame_info_dict),
                "frame_id": frame_id
            })

    def extract_frames_from_video_url(self, video_id, frames_per_second=3, file_type="jpg", img_quality=85):
        """
        从视频中每秒提取指定数量的帧
        """

        frames_save_path = f"{GeneralTool.root_path}/storage/{self.user_id}/mta/{self.task_id}/frame"

        mysql_result = MTAMapper.sync_select_video_where_video_id({
            "video_id": video_id
        })
        video_save_path = mysql_result.get_data_on_results()[0]["file_path"]

        # 打开视频文件
        cap = cv2.VideoCapture(video_save_path)
        if not cap.isOpened():
            print("无法打开视频文件")
            return

        # 获取视频属性
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        print(f"视频信息: {fps:.2f} FPS, 总帧数: {total_frames}, 时长: {duration:.2f}秒")
        print(f"每秒提取 {frames_per_second} 帧...")

        # 计算帧间隔（以秒为单位）
        interval = 1.0 / frames_per_second

        saved_count = 0
        current_time = 0.0

        frame_id_list = []
        while current_time < duration:
            # 设置目标时间位置
            cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)

            ret, frame = cap.read()
            if not ret:
                print(f"ret: {ret}")
                break

            # 生成文件名（包含时间戳）
            filename = f"{video_id}_{current_time:.2f}s.{file_type}"
            output_path = os.path.join(frames_save_path, filename)

            # 保存帧并压缩
            cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, img_quality])
            saved_count += 1

            frame_id = StrGenerator.generate_uuid()
            MTAMapper.sync_insert_frame({
                "frame_id": frame_id,
                "frame_number": saved_count,
                "belong_video_id": video_id,
                "belong_user_id": self.user_id,
                "belong_task_id": self.task_id,
                "file_path": output_path,
                "understanding_info": ""
            })
            frame_id_list.append(frame_id)

            # 移动到下一个时间点
            current_time += interval

        # 释放资源
        cap.release()
        print(f"处理完成! 共保存 {saved_count} 张图片")

        return frame_id_list

    def download_video(self, video_url, file_type="mp4"):
        video_save_path = f"{GeneralTool.root_path}/storage/{self.user_id}/mta/{self.task_id}/video/{self.task_id}.{file_type}"
        VideoDownloader.download_mp4(url=video_url, save_path=video_save_path)
        video_id = StrGenerator.generate_uuid()
        # 保存视频信息
        MTAMapper.sync_insert_video({
            "video_id": video_id,
            "belong_user_id": self.user_id,
            "belong_task_id": self.task_id,
            "video_name": f"{self.task_id}.{file_type}",
            "file_path": video_save_path,
        })

        return video_id

    def get_video_url_from_aweme_id(self, aweme_id):
        fetch_one_video_url = f"{self.service_douyin_base_url}/api/douyin/web/fetch_one_video"
        fetch_one_video_params = {
            "aweme_id": aweme_id
        }
        resp = requests.get(fetch_one_video_url, params=fetch_one_video_params)
        video_url = None
        if resp.status_code == 200:
            resp_data = resp.json()
            # 提取1080p的视频
            video_url = [big_rate for big_rate in resp_data['data']['aweme_detail']['video']['bit_rate'] if
                         '1080' in big_rate['gear_name']][0]['play_addr']['url_list'][0]
        return video_url

    def get_aweme_id_from_share_url(self, share_url):
        get_aweme_id_url = f"{self.service_douyin_base_url}/api/douyin/web/get_aweme_id"
        get_aweme_id_params = {
            "url": share_url
        }
        resp = requests.get(get_aweme_id_url, params=get_aweme_id_params)
        aweme_id = None
        if resp.status_code == 200:
            resp_data = resp.json()
            aweme_id = resp_data['data']

        return aweme_id

    def extract_share_url_from_str(self, share_str):
        pattern = r'https?://v\.douyin\.com/\S+/'
        match = re.search(pattern, share_str)
        share_url = None
        if match:
            share_url = match.group()
        return share_url




