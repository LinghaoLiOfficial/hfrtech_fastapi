from utils.database.CypherDriver import CypherDriver
from utils.database.AsyncSqlDriver import AsyncSqlDriver


class LRMapper:

    @classmethod
    async def select_validation_where_email(cls, params):
        sql = "SELECT * FROM nst.lr_validation WHERE email = %s"
        return await AsyncSqlDriver.execute_read(sql, params)

    @classmethod
    async def select_user_where_email_and_password(cls, params):
        sql = "SELECT * FROM nst.user WHERE email = %s and password = %s"
        return await AsyncSqlDriver.execute_read(sql, params)

    @classmethod
    async def select_user_where_email(cls, params):
        sql = "SELECT * FROM nst.user WHERE email = %s"
        return await AsyncSqlDriver.execute_read(sql, params)

    @classmethod
    async def delete_validation(cls, params):
        sql = "DELETE FROM nst.lr_validation WHERE email = %s"
        return await AsyncSqlDriver.execute_write(sql, params)

    @classmethod
    async def insert_validation(cls, params):
        sql = "INSERT INTO nst.lr_validation (validation_id, email, code, create_timestamp) VALUES (%s, %s, %s, NOW())"
        return await AsyncSqlDriver.execute_write(sql, params)

    @classmethod
    async def insert_user(cls, params):
        sql = "INSERT INTO nst.user (user_id, email, password, salt, auth, create_timestamp) VALUES (%s, %s, %s, %s, %s, NOW())"
        return await AsyncSqlDriver.execute_write(sql, params)

    @classmethod
    async def merge_user_node(cls, params):
        cypher = "MERGE (n:user {id: $user_id, email: $email})"
        return await CypherDriver.execute_write(cypher, params)
