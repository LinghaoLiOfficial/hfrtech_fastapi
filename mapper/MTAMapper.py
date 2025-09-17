from utils.database.SqlDriver import SqlDriver


class MTAMapper:

    @classmethod
    def select_frame_where_user_id(cls, params):
        sql = "SELECT * FROM nst.mta_frame_detail WHERE belong_user_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def update_frame_on_understanding_info(cls, params):
        sql = "UPDATE nst.mta_frame_detail SET understanding_info = %s WHERE frame_id = %s"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def select_frame_where_frame_id(cls, params):
        sql = "SELECT * FROM nst.mta_frame_detail WHERE frame_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def select_video_where_video_id(cls, params):
        sql = "SELECT * FROM nst.mta_video_detail WHERE video_id = %s"
        return SqlDriver.execute_read(sql, params)

    @classmethod
    def insert_frame(cls, params):
        sql = "INSERT INTO nst.mta_frame_detail (frame_id, frame_number, belong_video_id, belong_user_id, belong_task_id, file_path, understanding_info, create_timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_video(cls, params):
        sql = "INSERT INTO nst.mta_video_detail (video_id, belong_user_id, belong_task_id, video_name, file_path, create_timestamp) VALUES (%s, %s, %s, %s, %s, NOW())"
        return SqlDriver.execute_write(sql, params)

    @classmethod
    def insert_task(cls, params):
        sql = "INSERT INTO nst.mta_task_detail (task_id, belong_user_id, task_name, create_timestamp) VALUES (%s, %s, %s, NOW())"
        return SqlDriver.execute_write(sql, params)

