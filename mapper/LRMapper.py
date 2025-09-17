from utils.database.CypherDriver import CypherDriver
from utils.database.SqlDriver import SqlDriver


class LRMapper:

    @classmethod
    def select_validation_where_email(cls, params):
        sql = "SELECT * FROM nst.lr_validation WHERE email = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_user_where_email_and_password(cls, params):
        sql = "SELECT * FROM nst.user WHERE email = %s and password = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_user_where_email(cls, params):
        sql = "SELECT * FROM nst.user WHERE email = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def delete_validation(cls, params):
        sql = "DELETE FROM nst.lr_validation WHERE email = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_validation(cls, params):
        sql = "INSERT INTO nst.lr_validation (validation_id, email, code, create_timestamp) VALUES (%s, %s, %s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_user(cls, params):
        sql = "INSERT INTO nst.user (user_id, email, password, salt, auth, create_timestamp) VALUES (%s, %s, %s, %s, %s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def merge_user_node(cls, params):
        cypher = "MERGE (n:user {id: $user_id, email: $email})"
        return CypherDriver.execute_write(cypher, params)
