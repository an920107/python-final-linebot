import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import ddddocr
import sqlite3

from modules.chrome import Chrome


class HSR:
    def __init__(self, id: str, chrome: Chrome = None):
        self.id = id
        self.chrome = chrome


    # 從資料庫取得使用者資料
    def load(self) -> bool:
        sql = sqlite3.connect("sql/users.sqlite")
        cursor = sql.cursor()
        cursor.execute(f""" SELECT * FROM users WHERE id = "{self.id}" """)
        fatched = cursor.fetchall()
        if len(fatched) == 0:
            return False
        self.userdata = self.__list_to_dict(fatched[0])
        return True

    # 取得班次
    def get_cars(self, from_index: int, to_index: int,
                 student: str, adult: str, child: str,
                 date: str, time: str) -> str:

        # 初始化
        URL = "https://irs.thsrc.com.tw/IMINT/"
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        self.chrome = Chrome(options=options)
        self.chrome.set_window_size(1600, 1000)
        self.chrome.get(URL)

        # 同意 cookie
        self.chrome.find_element_and_wait(
            By.XPATH, "//*[@id='cookieAccpetBtn']", 3000).click()

        # 輸入訂票資訊
        tried = 0
        while tried < 3:
            try:
                HEART = u"0"
                ELDER = u"0"
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[3]/div[1]/div/div[1]/div/select")).select_by_index(from_index + 1)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[3]/div[1]/div/div[2]/div/select")).select_by_index(to_index + 1)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[4]/div[1]/div[1]/div/select")).select_by_visible_text(adult)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[4]/div[1]/div[2]/div/select")).select_by_visible_text(child)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[4]/div[1]/div[3]/div/select")).select_by_visible_text(HEART)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[4]/div[1]/div[4]/div/select")).select_by_visible_text(ELDER)
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[4]/div[1]/div[5]/div/select")).select_by_visible_text(student)
                self.chrome.execute_script(
                    f"document.getElementById('toTimeInputField').setAttribute('value', '{date}')")
                Select(self.chrome.find_element(By.XPATH,
                                           "//*[@id='BookingS1Form']/div[3]/div[2]/div/div[2]/div[1]/select")).select_by_visible_text(time)

                # 驗證碼
                self.chrome.find_element(
                    By.ID, "BookingS1Form_homeCaptcha_passCode").screenshot("captcha.png")
                with open("captcha.png", "rb") as f:
                    image_bytes = f.read()
                security_code = ddddocr.DdddOcr().classification(image_bytes)
                security_code_blank = self.chrome.find_element(
                    By.ID, "securityCode")
                security_code_blank.clear()
                security_code_blank.send_keys(security_code)
                self.chrome.find_element(By.ID, "SubmitButton").click()
                self.chrome.find_element(
                    By.XPATH, "//*[@id='BookingS2Form']/section[2]/div/div/input")
                break
            except:
                tried += 1
                continue

        # 取得班次
        class Car:
            def __init__(self, departure: str, arrival: str, code: str, discount: str) -> None:
                self.departure = departure
                self.arrival = arrival
                self.code = int(code)
                self.discount = "None" if (discount == "") else discount

        car_list = list(map(lambda e: Car(e[0], e[1], e[2], e[3]), zip(
            map(lambda e: e.text, self.chrome.find_elements(By.ID, "QueryDeparture")),
            map(lambda e: e.text, self.chrome.find_elements(By.ID, "QueryArrival")),
            map(lambda e: e.text, self.chrome.find_elements(By.ID, "QueryCode")),
            map(lambda e: e.text.replace("\n", ","), self.chrome.find_elements(By.CSS_SELECTOR, "div[class='discount uk-flex']")))))

        car_list_str = ""
        for i in range(len(car_list)):
            car = car_list[i]
            car_list_str += f"{i + 1:2d} {car.code:4d} {car.departure} {car.arrival} {car.discount}\n"

        return car_list_str

    def run(self, car_index: int):
        # 選擇班次
        self.chrome.find_elements(By.CSS_SELECTOR, "input[type='radio']")[
            car_index - 1].click()
        self.chrome.find_element(
            By.XPATH, "//*[@id='BookingS2Form']/section[2]/div/div/input").click()

        # 輸入身份資訊
        self.load()
        id_blank = self.chrome.find_element(By.ID, "idNumber")
        id_blank.clear()
        id_blank.send_keys(self.userdata["person_id"])
        phone_blank = self.chrome.find_element(By.ID, "mobilePhone")
        phone_blank.clear()
        phone_blank.send_keys(self.userdata["phone"])
        email_blank = self.chrome.find_element(By.ID, "email")
        email_blank.clear()
        email_blank.send_keys(self.userdata["email"])
        self.chrome.find_element(
            By.XPATH, "//*[@id='BookingS3FormSP']/section[2]/div[3]/div[1]/label/input").click()
        self.chrome.find_element(By.ID, "isSubmit").click()

        # 關閉學生優惠提醒視窗
        try:
            self.chrome.find_element_and_wait(
                By.ID, "step4StudentModalBtn", 800).click()
        except:
            pass

        # 截圖
        self.chrome.find_element(
            By.XPATH, "//*[@id='BookingS4Form']/section[1]").screenshot("result.png")
        
        self.chrome.close()

    def __list_to_dict(self, l: list) -> dict:
        return {
            "id": l[0],
            "name": l[1],
            "person_id": l[2],
            "email": l[3],
            "phone": l[4]
        }
