from fastapi import APIRouter

from service.file.FileService import FileService
from fastapi.responses import FileResponse

file_router = APIRouter(prefix="/file")


# 获取任意本地文件
@file_router.get("/{file_path:path}")
async def get_file_api(file_path: str):
    """
    获取指定路径的文件

    参数:
        file_path: 文件相对路径 (如: uploads/images/photo.jpg)

    返回:
        FileResponse: 文件内容流式响应
    """
    # 调用文件服务获取安全路径
    full_path = FileService.validate_and_get_path(file_path)

    # 直接返回 FileResponse 对象
    return FileResponse(
        path=full_path,
        filename=FileService.get_filename(file_path),
        media_type=FileService.get_media_type(file_path)
    )
