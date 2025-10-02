from utils.web.Result import Result


class Resp(Result):

    @classmethod
    def _build(cls, status: bool, code: int, message: str, body: dict):
        return cls(status, code, message, body).to_dict()

    @classmethod
    def build_success(cls, code: int = None, message: str = "", body: dict = {}):
        return cls._build(
            status=True,
            code=code,
            message=message,
            body=body
        )

    @classmethod
    def build_error(cls, code: int = None, message: str = "", body: dict = {}):
        return cls._build(
            status=False,
            code=code,
            message=message,
            body=body
        )

    @classmethod
    def build_db_error(cls):
        return cls.build_error(
            code=60001,
            message="数据库操作执行失败"
        )

    @classmethod
    def build_jwt_error(cls, jwt_parser_result: Result):
        return cls.build_error(
            code=jwt_parser_result.code,
            message=jwt_parser_result.message
        )

