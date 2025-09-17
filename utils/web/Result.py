class Result:
    status: bool
    code: int
    message: str
    body: dict

    def __init__(self, status, code, message, body):
        self.status = status
        self.code = code
        self.message = message
        self.body = body

    def to_dict(self):
        return self.__dict__

    def get_data(self, key):
        return self.body.get(key)

    def get_data_on_results(self):
        return self.get_data("results")

    def verify_data(self, key: str):
        value = self.get_data(key)
        if value == []:
            return False

        return True

    def verify_data_on_results(self):
        return self.verify_data("results")

    @classmethod
    def _build(cls, status: bool, code: int, message: str, body: dict):
        return cls(status, code, message, body)

    @classmethod
    def build_success(cls, code: int = None, message: str = "", body: dict = {}):
        return cls._build(
            status=True,
            code=code,
            message=message,
            body=body
        )

    @classmethod
    def build_success_with_results(cls, value):
        return cls.build_success(
            body={
                "results": value
            }
        )

    @classmethod
    def build_error(cls, code: int = None, message: str = "", body: dict = {}):
        return cls._build(
            status=False,
            code=code,
            message=message,
            body=body
        )

