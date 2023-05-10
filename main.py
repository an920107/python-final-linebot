import os
import json
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from chatgpt import ChatGPT

app = Flask(__name__)
app.config["host"] = "0.0.0.0"
line_bot_config = json.load(open("config/linebot.conf", "r", encoding="utf8"))
line_bot_api = LineBotApi(line_bot_config["access_token"])
handler = WebhookHandler(line_bot_config["channel_secret"])
gpt = ChatGPT(open("config/chatgpt.conf", "r", encoding="utf8"))


@app.route("/")
def root():
    return "Root"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        os.abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def reply(event):

    try:
        line_bot_api.reply_message(
            event.reply_token,
            # TextSendMessage(text=event.message.text)
            TextSendMessage(text=gpt.post(event.message.text))
        )
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="機器人罷工")
        )


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
