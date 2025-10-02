import os
import mimetypes
from pathlib import Path
from fastapi import HTTPException

from utils.common.GeneralTool import GeneralTool


class FileService:
    # 基础目录 - 设置为项目根目录或指定的安全目录
    BASE_DIR = Path(GeneralTool.root_path)

    @classmethod
    def validate_and_get_path(cls, relative_path: str) -> str:
        """
        验证文件路径是否安全并返回完整路径

        参数:
            relative_path: 相对路径

        返回:
            完整的文件系统路径

        异常:
            HTTPException: 如果路径不安全或文件不存在
        """
        # 构建完整路径
        full_path = (cls.BASE_DIR / relative_path).resolve()

        # 安全检查 1: 确保路径在基础目录内
        if not full_path.is_relative_to(cls.BASE_DIR):
            raise HTTPException(
                status_code=403,
                detail="Access to this file is forbidden"
            )

        # 安全检查 2: 确保文件存在
        if not full_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

        return str(full_path)

    @classmethod
    def get_filename(cls, file_path: str) -> str:
        """从路径中提取文件名"""
        return os.path.basename(file_path)

    @classmethod
    def get_media_type(cls, file_path: str) -> str:
        """根据扩展名获取 MIME 类型"""
        filename = cls.get_filename(file_path)
        media_type, _ = mimetypes.guess_type(filename)
        return media_type or "application/octet-stream"