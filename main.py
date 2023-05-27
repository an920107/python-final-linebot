import os
import json
import sqlite3
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from modules.chatgpt import ChatGPT
from pyimgur import Imgur

from modules.hsr import HSR

app = Flask(__name__)
app.config["host"] = "0.0.0.0"
line_bot_config = json.load(open("config/linebot.conf", "r", encoding="utf8"))
line_bot_api = LineBotApi(line_bot_config["access_token"])
handler = WebhookHandler(line_bot_config["channel_secret"])
imgur_config = json.load(open("config/imgur.conf", "r", encoding="utf8"))
imgur = Imgur(imgur_config["client_id"], imgur_config["client_secret"])
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


STATIONS = [
    " 1. 南港", " 2. 台北", " 3. 板橋", " 4. 桃園",
    " 5. 新竹", " 6. 苗栗", " 7. 台中", " 8. 彰化",
    " 9. 雲林", "10. 嘉義", "11. 台南", "12. 左營"
]

users_dict = dict()


@handler.add(MessageEvent, message=TextMessage)
def reply(event: MessageEvent):

    sql = sqlite3.connect("sql/users.sqlite")
    cursor = sql.cursor()

    global users_dict
    id = event.source.user_id
    if (users_dict.get(id) == None):
        users_dict[id] = {"is_setting": False,
                          "is_running": False, "hsr": HSR(id)}

    try:
        text = event.message.text

        if (text == "我想要訂購高鐵票" or users_dict[id]["is_running"]):
            hsr = users_dict[id]["hsr"]
            if ((not users_dict[id]["is_running"]) and (not hsr.load())):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你還沒設定個人資訊！")
                )
            else:
                if (not users_dict[id]["is_running"]):
                    users_dict[id]["is_running"] = True
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入日期（格式 yyyy/MM/dd）")
                    )
                elif (users_dict[id].get("date") == None):
                    users_dict[id]["date"] = text
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入時間（格式 HH:00，以小時為單位）")
                    )
                elif (users_dict[id].get("time") == None):
                    users_dict[id]["time"] = text
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入出發站編號\n" +
                                        "\n".join(STATIONS))
                    )
                elif (users_dict[id].get("from") == None):
                    users_dict[id]["from"] = int(text)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入抵達站編號\n" +
                                        "\n".join(STATIONS))
                    )
                elif (users_dict[id].get("to") == None):
                    users_dict[id]["to"] = int(text)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入學生票數量")
                    )
                elif (users_dict[id].get("student") == None):
                    users_dict[id]["student"] = text
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入成人票數量")
                    )
                elif (users_dict[id].get("adult") == None):
                    users_dict[id]["adult"] = text
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入兒童票數量")
                    )
                elif (users_dict[id].get("child") == None):
                    users_dict[id]["child"] = text
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入預搭乘班次編號\n" + hsr.get_cars(
                            from_index=users_dict[id]["from"],
                            to_index=users_dict[id]["to"],
                            date=users_dict[id]["date"],
                            time=users_dict[id]["time"],
                            student=users_dict[id]["student"],
                            adult=users_dict[id]["adult"],
                            child=users_dict[id]["child"]
                        ))
                    )
                elif (users_dict[id].get("car") == None):
                    users_dict[id]["car"] = int(text)
                    hsr.run(car_index=users_dict[id]["car"])
                    img = imgur.upload_image("result.png")
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=img.link_huge_thumbnail,
                            preview_image_url=img.link_big_square)
                    )
                    users_dict[id] = {"is_setting": False, "is_running": False}

        elif (text == "我要設定個人資訊" or users_dict[id]["is_setting"]):
            if (not users_dict[id]["is_setting"]):
                users_dict[id]["is_setting"] = True
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入姓名")
                )
            elif (users_dict[id].get("name") == None):
                users_dict[id]["name"] = text
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入手機號碼")
                )
            elif (users_dict[id].get("phone") == None):
                users_dict[id]["phone"] = text
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入電子郵件")
                )
            elif (users_dict[id].get("email") == None):
                users_dict[id]["email"] = text
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入身份證字號")
                )
            else:
                users_dict[id]["person_id"] = text
                cursor.execute(f""" DELETE FROM users WHERE id = "{id}" """)
                cursor.execute(f"""
                    INSERT INTO users (id, name, person_id, email, phone) VALUES (
                        "{id}",
                        "{users_dict[id]['name']}",
                        "{users_dict[id]['person_id']}",
                        "{users_dict[id]['email']}",
                        "{users_dict[id]['phone']}")
                """)
                sql.commit()
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=f"設定完成！以下是你的個人資訊\n姓名：{users_dict[id]['name']}\n手機：{users_dict[id]['phone']}\n電子郵件：{users_dict[id]['email']}\n身份證字號：{users_dict[id]['person_id']}")
                )
                users_dict[id] = {"is_setting": False, "is_running": False}

        else:
            reply_text = gpt.post(event.message.text)

            app.logger.info(reply_text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

    except Exception as e:
        print(e.with_traceback())
        users_dict[id] = {"is_setting": False, "is_running": False}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="機器人罷工 ><")
        )

    sql.close()


if __name__ == "__main__":
    app.run("0.0.0.0", 12345, debug=True)
