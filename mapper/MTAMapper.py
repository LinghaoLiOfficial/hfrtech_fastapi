from utils.database.AsyncSqlDriver import AsyncSqlDriver
from utils.database.SqlDriver import SqlDriver


class MTAMapper:

    @classmethod
    async def select_frame_where_user_id(cls, params):
        sql = "SELECT * FROM nst.mta_frame_detail WHERE belong_user_id = %(belong_user_id)s"
        return await AsyncSqlDriver.execute_read(sql, params)

    @classmethod
    def sync_update_frame_on_understanding_info(cls, params):
        sql = "UPDATE nst.mta_frame_detail SET understanding_info = %(understanding_info)s WHERE frame_id = %(frame_id)s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def sync_select_frame_where_frame_id(cls, params):
        sql = "SELECT * FROM nst.mta_frame_detail WHERE frame_id = %(frame_id)s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def sync_select_video_where_video_id(cls, params):
        sql = "SELECT * FROM nst.mta_video_detail WHERE video_id = %(video_id)s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def sync_insert_frame(cls, params):
        sql = "INSERT INTO nst.mta_frame_detail (frame_id, frame_number, belong_video_id, belong_user_id, belong_task_id, file_path, understanding_info, create_timestamp) VALUES (%(frame_id)s, %(frame_number)s, %(belong_video_id)s, %(belong_user_id)s, %(belong_task_id)s, %(file_path)s, %(understanding_info)s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def sync_insert_video(cls, params):
        sql = "INSERT INTO nst.mta_video_detail (video_id, belong_user_id, belong_task_id, video_name, file_path, create_timestamp) VALUES (%(video_id)s, %(belong_user_id)s, %(belong_task_id)s, %(video_name)s, %(file_path)s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    async def insert_task(cls, params):
        sql = "INSERT INTO nst.mta_task_detail (task_id, belong_user_id, task_name, create_timestamp) VALUES (%(task_id)s, %(belong_user_id)s, %(task_name)s, NOW())"
        return await AsyncSqlDriver.execute_write(sql, params)

