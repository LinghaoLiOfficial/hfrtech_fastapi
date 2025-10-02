import time

from utils.llm_api.BaseLLMAPIClient import BaseLLMAPIClient
from utils.llm_api.prompts.LocateAndUnderstandImgPrompt import LocateAndUnderstandImgPrompt


class LLMServiceClient:
    @classmethod
    def locate_and_understand_img(cls, absolute_image_path):
        image_path = f"file://{absolute_image_path}"
        messages = [
            {
                "role": "system",
                "content": [{"text": LocateAndUnderstandImgPrompt.system_prompt}]
            },
            {
                "role": "user",
                "content": [
                    {'image': image_path},
                    {'text': LocateAndUnderstandImgPrompt.user_prompt}
                ]
            }
        ]
        output_dict = {}
        retry = 5
        for _ in range(retry):
            try:
                output_text = BaseLLMAPIClient.call_qwen_vl_max(messages=messages)
                output_dict = BaseLLMAPIClient.parse_str_to_json(output_text)
                if output_dict != {}:
                    return output_dict
            except Exception as e:
                print(e)
            time.sleep(2)

        return output_dict
