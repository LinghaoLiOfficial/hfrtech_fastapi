import os
from typing import Type, Optional, Tuple, Any

import mysql.connector

from utils.web.Result import Result


class SqlDriver:

    @classmethod
    def _get_connect(cls):
        return mysql.connector.connect(
            host=os.getenv("MYSQL_CONNECTOR_HOST"),
            user=os.getenv("MYSQL_CONNECTOR_USER"),
            password=os.getenv("MYSQL_CONNECTOR_PASSWORD"),
            database=os.getenv("MYSQL_CONNECTOR_DATABASE"),
            charset="utf8mb4"  # 确保支持特殊字符
        )

    # 测试连接
    @classmethod
    def test_connection(cls):
        connection = cls._get_connect()

        if not connection.is_connected():
            connection.close()
            return Result.build_error()

        connection.close()
        return Result.build_success()

    # 读操作：支持参数化查询
    @classmethod
    def execute_read(
        cls,
        sql: str,
        params  # 接受字典参数
    ):
        # 移除参数转换逻辑，直接使用字典
        connection = cls._get_connect()
        cursor = connection.cursor()

        try:
            # 直接传递字典参数
            cursor.execute(sql, params)  # 关键修改
            results = cursor.fetchall()

            # 获取列名
            columns = [desc[0] for desc in cursor.description]

            # 将结果转换为字典列表
            result_mappings = [dict(zip(columns, row)) for row in results]

        except Exception as e:
            print("Read Error:", e)
            print("Failed SQL:", cursor.statement)  # 打印实际执行的SQL
            cursor.close()
            connection.close()
            return Result.build_error()

        cursor.close()
        connection.close()

        return Result.build_success_with_results(result_mappings)

    # 写操作：支持参数化查询
    @classmethod
    def execute_write(
        cls,
        sql: str,
        params  # 接受字典参数
    ):
        # 移除参数转换逻辑
        connection = cls._get_connect()
        cursor = connection.cursor()

        try:
            # 直接传递字典参数
            cursor.execute(sql, params)  # 关键修改
            connection.commit()

        except Exception as e:
            print("Write Error:", e)
            print("Failed SQL:", cursor.statement)  # 打印实际执行的SQL
            cursor.close()
            connection.close()
            return Result.build_error()

        cursor.close()
        connection.close()
        return Result.build_success()

    # 事务操作：支持参数化查询
    @classmethod
    def execute_transaction_write(
        cls,
        sql: str,
        params: Optional[Any] = None,  # 修改类型为Any以接受字典
        input: Optional[Tuple[Any, ...]] = None
    ):
        if input is None:
            connection = cls._get_connect()
            cursor = connection.cursor()

            try:
                connection.start_transaction()
                # 直接传递字典参数
                cursor.execute(sql, params)  # 关键修改
            except Exception as e:
                print("Transaction Error:", e)
                print("Failed SQL:", cursor.statement)
                cursor.close()
                connection.close()
                return Result.build_error()
        else:
            cursor, connection = input
            try:
                # 直接传递字典参数
                cursor.execute(sql, params)  # 关键修改
            except Exception as e:
                print("Transaction Error:", e)
                print("Failed SQL:", cursor.statement)
                cursor.close()
                connection.close()
                return Result.build_error()

        return Result.build_success_with_results((cursor, connection))

    # 回滚和关闭方法保持不变
    @classmethod
    def rollback(cls, input):
        cursor, connection = input

        try:
            connection.rollback()

        except Exception as e:
            print(e)
            cursor.close()
            connection.close()
            return Result.build_error()

        cursor.close()
        connection.close()
        return Result.build_success()

    @classmethod
    def close(cls, input):
        cursor, connection = input

        try:
            connection.commit()

        except Exception as e:
            print(e)
            cursor.close()
            connection.close()
            return Result.build_error()

        cursor.close()
        connection.close()
        return Result.build_success()