import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
import uvicorn

# 导入路由模块
from controller.file_controller import file_router
from controller.test_controller import test_router

# 加载全局环境变量
load_dotenv(find_dotenv(), verbose=True)

# 实例化FastAPI框架
app = FastAPI()

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 批量注册路由
routers_list = [
    file_router,
    test_router

]
for router in routers_list:
    app.include_router(router)


# 根路由
@app.get("/")
async def default():
    return {"status": 200}


# # 应用生命周期管理
# @app.on_event("shutdown")
# def shutdown_event():
#     """应用关闭时关闭执行器"""
#     task_executor.shutdown(wait=True)


# 启动配置
if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG_MODE", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", 1))
    )