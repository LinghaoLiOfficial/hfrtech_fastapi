import requests

class VideoDownloader:
    @classmethod
    def download_mp4(cls, url, save_path):
        """下载 MP4 视频文件"""
        try:
            # 添加浏览器请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Referer": "https://www.douyin.com/",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "video",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }

            # 发送 GET 请求（启用流式下载）
            timeout = 30
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            response.raise_for_status()  # 检查 HTTP 错误

            # 获取文件大小（用于进度显示）
            file_size = int(response.headers.get('content-length', 0))

            # 写入文件
            chunk_size = 8192
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # 过滤 keep-alive 数据块
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 显示下载进度
                        if file_size > 0:
                            # 百分比进度
                            progress = downloaded / file_size * 100
                            print(f"\r下载进度: {progress:.1f}%", end="", flush=True)
                print("\n下载完成！")

        except Exception as e:
            print(f"下载失败: {e}")