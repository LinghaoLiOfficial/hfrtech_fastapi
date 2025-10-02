import os
from openai import OpenAI
import json
from zai import ZhipuAiClient
from dashscope import MultiModalConversation
import re
import time


class BaseLLMAPIClient:
    """
    0822.ver
    """

    qwen_llm = OpenAI(api_key=os.getenv("QWEN_API_KEY"), base_url=os.getenv("QWEN_API_URL"))
    deepseek_llm = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_API_URL"))
    glm_llm = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))

    @classmethod
    def call_qwen_vl_max(cls, messages):
        resp = MultiModalConversation.call(
            api_key=os.getenv('QWEN_API_KEY'),
            model='qwen-vl-max-latest',
            messages=messages)
        output_text = resp["output"]["choices"][0]["message"].content[0]["text"]
        return output_text

    @classmethod
    def call_deepseek_reasoner(cls, messages):
        completion = cls.deepseek_llm.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=False,
        )

        output_text = completion.choices[0].message.content
        return output_text

    @classmethod
    def call_glm4(cls, messages):
        completion = cls.glm_llm.chat.completions.create(
            model="glm-4.5",
            messages=messages

        )

        output_text = completion.choices[0].message.content
        return output_text

    @classmethod
    def call_qwen3_plus(cls, messages):
        completion = cls.qwen_llm.chat.completions.create(
            model="qwen-plus",
            messages=messages

        )

        output_text = completion.choices[0].message.content
        return output_text

    @classmethod
    def call_qwen3_embedding(cls, text):
        completion = cls.qwen_llm.embeddings.create(
            model="text-embedding-v4",
            input=text,
            dimensions=1024,
            encoding_format="float"
        )

        try:
            result = json.loads(completion.model_dump_json())
        except Exception as e:
            print(e)
            return None

        return [x['embedding'] for x in result['data']]

    @classmethod
    def parse_str_to_json(cls, input_str):
        input_str = input_str.replace("true", "True").replace("false", "False")

        match = re.search(r'```json(.*?)```', input_str, re.DOTALL)
        output_str = ""
        if match:
            output_str = match.group(1).strip()
        try:
            output_dict = eval(output_str)
            return output_dict
        except Exception as e:
            print(e)
            output_dict = {}
        return output_dict



