# 功能型智能聊天機器人

## 環境建置

1. 下載專案，使用 git clone 或直接下載 zip 並解壓縮
   
   ```shell
   git clone https://github.com/an920107/python-final-linebot.git
   ```

2. 安裝相依套件
   
   ```shell
   pip install -r requirements.txt
   ```

3. 安裝 ngrok
   
   > 為了讓伺服器能與 Line 伺服器通訊，必須使本機能被連線，可結由 PPPoE 或 port forwarding 達成，若設備不不允許，可以使用 ngrok 使外部可連線
   
   - Debian/ Ubuntu
     
     ```shell
     sudo apt install ngrok
     ```
   
   - Windows/ macOS/ Others
     
     [官方網站下載頁面](https://ngrok.com/download)

## 申請所需的 API 並加入專案

- Line Bot
  
  1. 至 [LINE Developers](https://developers.line.biz/console) 建立專案 Provider
  
  2. 於 Provider 內新增新的 Channel，類別為 Messaging API
  
  3. 將專案的 `config/linebot_template.conf` 改名成 `config/linebot.conf`
  
  4. 在 Channel 的 Basic settings 找到 Channel secret 並複製到專案中 `config/linebot.conf` 的 `channel_secret` 後方
  
  5. 在 Messaging API 中找到 Channel access token 按下 Issue 取得新的 token 並複製到 `config/linebot` 的 `access_token` 後方

- ChatGPT
  
  1. 將專案的 `config/chatgpt_template.conf` 改名成 `config/chatgpt.conf`
  
  2. 至 [OpenAI API](https://platform.openai.com/account/api-keys) 取得 API key 並複製到 `config/chatgpt.conf` 的 `key` 後方

- Imgur
  
  1. 將專案的 `config/imgur_template.conf` 改名成 `config/imgur.conf`
  
  2. 至 [Imgur Register an Application](https://api.imgur.com/oauth2/addclient) 建立應用程式，並於 Authorization type 選擇第二項
     
     ![](https://s2.loli.net/2023/05/28/xoJYWr3i94QTPRc.png)
  
  3. 可於 [Imgur Applications](https://imgur.com/account/settings/apps) 找到申請過的應用程式的 `Client ID` 與 `Client Secret` 分別複製到 `config/imgur.conf` 的 `client_id` 與 `client_secret` 後方

- Ngrok（選用）
  
  1. 至 [ngrok ](https://dashboard.ngrok.com/get-started/setup) 註冊帳號並登入，找到 Connect your account 下方的指令複製執行

## 啟動專案

1. 以 Python 執行
   
   ```shell
   python ./main.py
   ```

2. （選用）執行 ngrok
   
   > 12345 為 main.py 中 `app.run("0.0.0.0", 12345, debug=True)` 中的連接埠號
   
   ```shell
   ngrok http 12345
   ```

3. 至 [LINE Developers](https://developers.line.biz/console) 的 Messaging API 設定 Web Hook 的 IP 位置域名，後方要記得加上 `/callback`
