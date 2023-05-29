# 功能型智能聊天機器人

## 專題簡介

### 簡介

此專題主要是實作了 Linebot 連接 ChatGPT 以及高鐵訂票的功能。
能夠根據使用者輸入的文字來進行簡單的對話，也能讓使用者藉由輸入一點資料就能夠完成高鐵訂票。

## 如何使用這個專案

### 環境建置

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

### 申請所需的 API 並加入專案

- Line Bot
  
  1. 至 [LINE Developers](https://developers.line.biz/console) 建立專案 Provider
  
  2. 於 Provider 內新增新的 Channel，類別為 Messaging API
     
     ![](https://hackmd.io/_uploads/BkeKxBfUn.png)
     
     ![](https://hackmd.io/_uploads/SkDPxSGI2.png)
  
  3. 將專案的 `config/linebot_template.conf` 改名成 `config/linebot.conf`
  
  4. 在 Channel 的 Basic settings 找到 Channel secret 並複製到專案中 `config/linebot.conf` 的 `channel_secret` 後方
  
  5. 在 Messaging API 中找到 Channel access token 按下 Issue 取得新的 token 並複製到 `config/linebot` 的 `access_token` 後方

- ChatGPT
  
  1. 將專案的 `config/chatgpt_template.conf` 改名成 `config/chatgpt.conf`
  
  2. 至 [OpenAI API](https://platform.openai.com/account/api-keys) 取得 API key 並複製到 `config/chatgpt.conf` 的 `key` 後方
     ![](https://hackmd.io/_uploads/BJPl-HfL3.png)

- Imgur
  
  1. 將專案的 `config/imgur_template.conf` 改名成 `config/imgur.conf`
  
  2. 至 [Imgur Register an Application](https://api.imgur.com/oauth2/addclient) 建立應用程式，並於 Authorization type 選擇第二項
     
     ![](https://s2.loli.net/2023/05/28/xoJYWr3i94QTPRc.png)
  
  3. 可於 [Imgur Applications](https://imgur.com/account/settings/apps) 找到申請過的應用程式的 `Client ID` 與 `Client Secret` 分別複製到 `config/imgur.conf` 的 `client_id` 與 `client_secret` 後方

- Ngrok（選用）
  
  1. 至 [ngrok ](https://dashboard.ngrok.com/get-started/setup) 註冊帳號並登入，找到 Connect your account 下方的指令複製執行

### 啟動專案

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

## 詳細程式碼說明

- main.py: 負責執行整個 linebot 並整合 chatgpt.py 與 hsr.py 的程式碼，並根據使用者輸入來做出其回應，例如:設定個人資料、chatgpt 回應以及訂購高鐵票。

- chatgpt.py: 與 ChatGPT API 串接，讀取 config 檔，並透過 http post 與 ChatGPT API 聯繫，讓使用者輸入的文字能夠 ChatGPT 回應。

- hsr.py: 從資料庫獲得使用者的資料，並根據使用想要訂票的資訊進行爬蟲(獲取資料)，取得班次列表後回傳至 main.py 並再獲取訂購班次的要求後，完成訂票並與 Imgur API Key 完成截圖上傳至 Imgur 後回傳給使用者。

- chrome.py: 因為原本 selenium 的 wait and find_element 寫法過於冗長，因此使用繼承的方式，新增新的方法，讓使用起來的可讀性與可寫性更高。

## 程式架構圖

### 整體程式架構

![](https://hackmd.io/_uploads/ryZNJHMLn.png)

### main.py 與其他檔案的架構圖

![](https://hackmd.io/_uploads/S1NvyHGIh.png)

### chatgpt.py 的架構圖

![](https://hackmd.io/_uploads/H1-6kSzL2.png)

### hsr.py 的架構圖

![](https://hackmd.io/_uploads/HyDygSMLn.png)

## 程式功能實作

### 畫面介紹

如與朋友對話般，可以直接在鍵盤輸入來使用

> 也可點及下方的「預設選單」來選擇功能

### ChatGPT 對話回應

![](https://i.imgur.com/TkWJ5Oi.png)

![](https://i.imgur.com/3LjVtHS.png)

在不使用預設功能的狀況下，輸入任意文字，Linebot 會使用 ChatGPT 回應你輸入的文字

### 設定個人檔案

![](https://hackmd.io/_uploads/SylBOxrGIh.png)

點選下方的選單右方「設定個人資料」可以設定自己的資料

> (若要開啟訂票功能，須先完成此設定)

1. 接下來會要求輸入姓名、手機號碼、電子郵件以及身分證字號

2. 設定完成後會將資料傳置 sql 資料庫並輸出資料給使用者

### 訂購高鐵票

![](https://hackmd.io/_uploads/BkDxbHzIh.png)

點選下方的選單左方「訂購高鐵」可以訂購高鐵票

1. 首先會先要求輸入日期以及時間

2. 接下來會請使用者輸入出發、抵達站(輸入數字編號)

3. 輸入想要訂購的種類其對應的票數數量

4. 輸入完成後會進行爬蟲(利用  selenium)並回傳可訂購的車種及其時間

5. 選完想訂購的票後，會完成剩下步驟並回傳訂購完成的圖

## 團隊分工

| 姓名  | 負責項目                                |
|:---:| ----------------------------------- |
| 游宗穎 | 使用者資料庫串接、高鐵訂票爬蟲程式碼、整式碼整併、簡報與說明文件    |
| 吳柏翰 | 簡報與說明文件、Line Developer 申請           |
| 許明瑞 | Line API 串接、Line Widgets 設計、簡報與說明文件 |
| 黃彥程 | 訊息回應流程、簡報與說明文件                      |
| 林劭宇 | 簡報與說明文件、ChatGPT API 串接              |
