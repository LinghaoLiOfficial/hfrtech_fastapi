from fastapi import Request, UploadFile, Form, File
from typing import List, Optional, Union


class Req:
    def __init__(self, request: Request):
        self.request = request
        self._json_data = None

    async def _ensure_json(self):
        """确保JSON数据已加载"""
        if self._json_data is None:
            self._json_data = await self.request.json()
        return self._json_data

    async def receive_get_param(self, param: str, default=None) -> Optional[str]:
        """获取GET查询参数"""
        return self.request.query_params.get(param, default)

    async def receive_post_param(self, param: str, default=None) -> Union[str, dict, list, None]:
        """获取POST参数（表单或JSON）"""
        # 优先尝试从JSON获取
        try:
            json_data = await self._ensure_json()
            return json_data.get(param, default)
        except:
            pass

        # 尝试从表单获取
        form_data = await self.request.form()
        return form_data.get(param, default)

    async def receive_header_token(self) -> Optional[str]:
        """获取Authorization头"""
        return self.request.headers.get('Authorization')

    async def receive_file_param(self, param: str) -> Optional[UploadFile]:
        """获取单个文件"""
        form_data = await self.request.form()
        return form_data.get(param)

    async def receive_files_param(self) -> List[UploadFile]:
        """获取多个文件"""
        form_data = await self.request.form()
        return form_data.getlist('files[]')

    async def receive_form_param(self, param: str, default=None) -> Optional[str]:
        """获取表单参数"""
        form_data = await self.request.form()
        return form_data.get(param, default)


# 创建Req实例的依赖项
async def get_req(request: Request) -> Req:
    return Req(request)
