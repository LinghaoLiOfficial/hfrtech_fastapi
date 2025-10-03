import os

from mapper.FAMapper import FAMapper
from mapper.LRMapper import LRMapper
from utils.common.EmailSender import EmailSender
from utils.common.GeneralTool import GeneralTool
from utils.common.JWTParser import JWTParser
from utils.common.StrGenerator import StrGenerator
from utils.common.TimeParser import TimeParser
from utils.web.Resp import Resp


class LRService:

    @classmethod
    async def verify_token(cls, token):
        jwt_parser_result = JWTParser.decode_user_id(
            token=token
        )
        if not jwt_parser_result.status:
            return Resp.build_jwt_error(jwt_parser_result)

        return Resp.build_success()

    @classmethod
    async def get_salt(cls, email):
        mysql_result = await LRMapper.select_user_where_email({
            "email": email
        })
        salt = mysql_result.get_data_on_results()[0]["salt"]

        return Resp.build_success(body={
            "salt": salt
        })

    @classmethod
    async def user_register(cls, email, hashed_password, validation_code, salt):
        mysql_result = await LRMapper.select_validation_where_email({
            "email": email
        })
        # 判断邮箱验证码是否存在
        if not mysql_result.verify_data_on_results():
            return Resp.build_error(
                code=50001,
                message="请先点击发送邮箱"
            )

        # 判断邮箱验证码是否正确
        if validation_code != mysql_result.get_data_on_results()[0]['code']:
            return Resp.build_error(
                code=50002,
                message="邮箱验证码有误"
            )

        user_id = StrGenerator.generate_uuid()

        # 新增用户
        mysql_result1 = await LRMapper.insert_user({
            "user_id": user_id,
            "email": email,
            "password": hashed_password,
            "salt": salt,
            "auth": "user"
        })

        # 创建用户节点
        neo4j_result = await LRMapper.merge_user_node({
            "user_id": user_id,
            "email": email
        })

        # 删除验证码信息
        await LRMapper.delete_validation({
            "email": email
        })

        return Resp.build_success(message="注册成功")

    @classmethod
    async def send_email(cls, email):
        # 查询邮箱是否已被注册
        mysql_result = await LRMapper.select_user_where_email({
            "email": email
        })
        if mysql_result.verify_data_on_results():
            return Resp.build_error(
                code=50001,
                message="该邮箱已被注册"
            )

        # 查询邮箱发送是否过于频繁
        mysql_result1 = await LRMapper.select_validation_where_email({
            "email": email
        })
        if mysql_result1.verify_data_on_results():
            time_parser_result = TimeParser.calculate_passing_time(mysql_result1.get_data_on_results()[0]["create_timestamp"])
            if not time_parser_result.status:
                return Resp.build_error(
                    code=50002,
                    message=f"邮箱发送过于频繁，请于{os.getenv('VALIDATION_REPEAT_SENDING_TIME_INTERVAL')}分钟之后重新发送"
                )

        # 删除原有验证数据
        await LRMapper.delete_validation({
            "email": email
        })

        # 添加新的验证数据
        validation_code = StrGenerator.generate_validation_code()
        await LRMapper.insert_validation({
            "validation_id": StrGenerator.generate_uuid(),
            "email": email,
            "code": validation_code
        })

        # 发送邮箱
        email_sender_result = EmailSender.send_validation_code(email, validation_code)
        if not email_sender_result.status:
            return Resp.build_error(
                code=50003,
                message="邮箱发送失败，请重试"
            )

        return Resp.build_success(message="邮箱已发送")

    @classmethod
    async def user_login(cls, email, password):
        # 根据用户名，查询用户
        mysql_result = await LRMapper.select_user_where_email({
            "email": email
        })
        if not mysql_result.status:
            return Resp.build_db_error()

        # 判断用户名是否存在
        if not mysql_result.verify_data_on_results():
            return Resp.build_error(
                code=50001,
                message="用户名不存在"
            )

        # 根据用户名+密码，查询用户
        mysql_result1 = await LRMapper.select_user_where_email_and_password({
            "email": email,
            "password": password
        })
        if not mysql_result1.status:
            return Resp.build_db_error()

        # 判断密码是否正确
        if len(mysql_result1.get_data_on_results()) == 0:
            return Resp.build_error(
                code=50002,
                message="密码错误"
            )

        # 根据用户id+用户名，生成token
        user_id = mysql_result1.get_data_on_results()[0]['user_id']
        jwt_parser_result = JWTParser.encode(
            user_id=user_id,
            username=mysql_result1.get_data_on_results()[0]['email']
        )
        if not jwt_parser_result.status:
            return Resp.build_error()

        token = jwt_parser_result.get_data_on_results()

        # 初始化用户存储文件夹
        zone_list = [
            "fa",
            "mta"
        ]
        # 判断用户存储文件夹是否存在，不存在则创建
        user_storage_path = f"{GeneralTool.root_path}/storage/{user_id}"
        if not os.path.exists(user_storage_path):
            os.makedirs(user_storage_path, exist_ok=True)
        for zone in zone_list:
            zone_user_storage_path = f"{GeneralTool.root_path}/storage/{user_id}/{zone}"
            if not os.path.exists(zone_user_storage_path):
                os.makedirs(zone_user_storage_path, exist_ok=True)

        # 初始化fa_stock_selection_config配置
        mysql_result2 = await FAMapper.select_stock_selection_config({
            "belong_user_id": user_id
        })
        if not mysql_result2.verify_data_on_results():
            await FAMapper.insert_stock_selection_config({
                "config_id": StrGenerator.generate_uuid(),
                "belong_user_id": user_id
            })

        return Resp.build_success(body={
                "token": token
            })
