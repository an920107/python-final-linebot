from io import TextIOWrapper
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import copy

class ChatGPT:

    '''
    底下是讀入設定檔應有的 json 格式
    {
        "key": "", // ChatGPT API 密鑰.
        "prefix": "", // 前綴
        "suffix": "", // 後綴
        "config": { // 參閱 https://platform.openai.com/docs/guides/chat/introduction
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": ""
                }
            ]
        }
    }
    '''
    def __init__(self, config_file: TextIOWrapper) -> None:
        self._config_file = config_file
        

    def post(self, text: str) -> str:

        URL = "https://api.openai.com/v1/chat/completions"

        config_dict = json.load(self._config_file)
        self._config_file.seek(0)

        self._auth = HTTPBasicAuth("Bearer", config_dict["key"])

        config_dict["config"]["messages"].append({
            "role": "user",
            "content": config_dict["prefix"] + text + config_dict["suffix"]
        })
        response = requests.post(URL, json=config_dict["config"], auth=self._auth)
        
        # print(self._config_dict["config"])
        # print(f"\n{json.loads(response.text)}\n")

        # response_text = re.search(r"\"content\":\".*?\"", response.text).group()
        # response_text = response_text[11:-1]
        # response_text = re.sub(r"(\\n)+", "\n", response_text)
        # response_text = re.sub(r"(\\\\n)+", "\n", response_text)

        # if response_text[0] in ["，", "。", "！", "？"]:
        #     response_text = response_text[1:]

        try:
            response_text = json.loads(response.text)["choices"][0]["message"]["content"]
        except:
            raise Exception("response.text")

        return response_text