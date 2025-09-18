import os.path
import random
from dotenv import load_dotenv, find_dotenv
import json


# 加载全局环境变量
load_dotenv(find_dotenv(), verbose=True)


class GeneralTool:

    seed = 42  # 全局随机种子
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @classmethod
    def load_json(cls, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        return cfg

    @classmethod
    def load_cfg(cls, cfg_name):
        cfg_path = f"{cls.root_path}/config/{cfg_name}.json"
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        return cfg


