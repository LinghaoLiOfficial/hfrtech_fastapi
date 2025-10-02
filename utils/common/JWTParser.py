import jwt
import os
import datetime

from utils.web.Result import Result


class JWTParser:
    @classmethod
    def encode(cls, user_id: str, username: str):
        payload = {
            "user_id": user_id,
            "username": username,
        }
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=int(os.getenv("JWT_EXPIRATION_TIME")))
        payload["exp"] = expiration_time

        token = jwt.encode(
            payload=payload,
            key=os.getenv("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHMS")
        )

        return Result.build_success_with_results(token)

    @classmethod
    def decode_user_id(cls, token: str):
        try:
            decoded_payload = jwt.decode(
                jwt=token,
                key=os.getenv("JWT_SECRET_KEY"),
                algorithms=os.getenv("JWT_ALGORITHMS")
            )

            return Result.build_success_with_results(decoded_payload["user_id"])

        except jwt.ExpiredSignatureError:
            return Result.build_error(
                code=50001,
                message="Token已过期"
            )

        except jwt.InvalidTokenError:
            return Result.build_error(
                code=50002,
                message="无效的Token"
            )

        except Exception as e:
            print(e)
            return Result.build_error(
                code=50003,
                message="Token解析失败"
            )

