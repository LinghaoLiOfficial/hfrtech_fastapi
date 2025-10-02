import os
from typing import Type, Optional, Tuple, Any, Dict, List

import aiomysql
from aiomysql import DictCursor

from utils.web.Result import Result


class AsyncSqlDriver:
    _pool = None

    @classmethod
    async def create_pool(cls):
        """创建数据库连接池"""
        if cls._pool is None:
            cls._pool = await aiomysql.create_pool(
                host=os.getenv("MYSQL_CONNECTOR_HOST"),
                user=os.getenv("MYSQL_CONNECTOR_USER"),
                password=os.getenv("MYSQL_CONNECTOR_PASSWORD"),
                db=os.getenv("MYSQL_CONNECTOR_DATABASE"),
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False
            )

    @classmethod
    async def close_pool(cls):
        """关闭连接池"""
        if cls._pool is not None:
            cls._pool.close()
            await cls._pool.wait_closed()
            cls._pool = None

    @classmethod
    async def test_connection(cls):
        """测试数据库连接"""
        await cls.create_pool()
        try:
            async with cls._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    if result[0] == 1:
                        return Result.build_success()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return Result.build_error()
        return Result.build_error()

    @classmethod
    async def execute_read(
        cls,
        sql: str,
        params: Dict[str, Any]
    ) -> Result:
        """异步读操作"""
        await cls.create_pool()
        try:
            async with cls._pool.acquire() as conn:
                async with conn.cursor(DictCursor) as cur:
                    # 使用字典参数直接传递
                    await cur.execute(sql, params)
                    results = await cur.fetchall()
                    return Result.build_success_with_results(results)
        except Exception as e:
            print(f"Read Error: {e}")
            return Result.build_error()

    @classmethod
    async def execute_write(
        cls,
        sql: str,
        params: Dict[str, Any]
    ) -> Result:
        """异步写操作"""
        await cls.create_pool()
        try:
            async with cls._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql, params)
                    await conn.commit()
                    return Result.build_success()
        except Exception as e:
            print(f"Write Error: {e}")
            async with cls._pool.acquire() as conn:
                await conn.rollback()
            return Result.build_error()

    @classmethod
    async def execute_transaction(
        cls,
        operations: List[Tuple[str, Dict[str, Any]]]
    ) -> Result:
        """异步事务操作"""
        await cls.create_pool()
        try:
            async with cls._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await conn.begin()
                    for sql, params in operations:
                        await cur.execute(sql, params)
                    await conn.commit()
                    return Result.build_success()
        except Exception as e:
            print(f"Transaction Error: {e}")
            async with cls._pool.acquire() as conn:
                await conn.rollback()
            return Result.build_error()