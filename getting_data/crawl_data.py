from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
# for importing config file
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

class CrawlData:
    def __init__(self, url, db_name=Config.DB_NAME, driver_path='chromedriver.exe', table_name='labor_force', column_name='labor_force'):
        self.url = url
        self.db_name = db_name
        self.driver_path = driver_path
        self.table_name = table_name
        self.column_name = column_name
        self.driver = self.init_driver()
        self.conn, self.cursor = self.init_db()

    # Hàm khởi tạo Selenium với chế độ headless
    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # driver = webdriver.Chrome(service=service)
        return driver

    # Hàm tạo table SQLite để lưu dữ liệu
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                province TEXT, 
                year TEXT, 
                {self.column_name} FLOAT,
                PRIMARY KEY (province, year)
            )
        ''')
        conn.commit()
        return conn, cursor

    # Hàm lưu dữ liệu vào SQLite
    def save_to_db(self, province, year, labor_force):
        # Kiểm tra xem dữ liệu đã tồn tại chưa
        self.cursor.execute(f"SELECT {self.column_name} FROM {self.table_name} WHERE province = ? AND year = ?", (province, year))
        record = self.cursor.fetchone()

        if record:
            # Cập nhật labor_force nếu bản ghi đã tồn tại
            self.cursor.execute(f"UPDATE {self.table_name} SET {self.column_name} = ? WHERE province = ? AND year = ?",
                                (labor_force, province, year))
            print(f"Đã cập nhật dữ liệu cho {province}, năm {year}.")
        else:
            # Thêm mới nếu bản ghi chưa tồn tại
            self.cursor.execute(f"INSERT INTO {self.table_name} (province, year, {self.column_name}) VALUES (?, ?, ?)",
                                (province, year, labor_force))
            print(f"Đã thêm dữ liệu cho {province}, năm {year}.")

    # Hàm xử lý popup (nếu có) sau khi nhấn "Tiếp tục"
    def handle_popup(self):
        try:
            close_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='ui-button-text' and text()='Close']"))
            )
            close_button.click()
            print("Popup đã được đóng.")
        except Exception:
            print("Không có popup nào xuất hiện.")

    # Hàm lấy dữ liệu từ trang web
    def scrape_data(self, year_input):
        self.driver.get(self.url)

        # Chuyển vào iframe chứa các thẻ <select>
        iframe = WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        self.driver.switch_to.frame(iframe)

        # Lấy tất cả các thẻ <select> trên trang
        select_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )

        # Thẻ <select> đầu tiên là province, thẻ thứ hai là year
        province_select = select_elements[0]  # Thẻ <select> đầu tiên

        # Lấy tất cả các tỉnh thành từ thẻ <select> đầu tiên
        province_texts_selected = [
            'Hà Nội',
            'Vĩnh Phúc',
            'Bắc Ninh',
            'Quảng Ninh',
            'Hải Dương',
            'Hải Phòng',
            'Hưng Yên',
            'Thái Bình',
            'Hà Nam',
            'Nam Định',
            'Ninh Bình',
            'Hà Giang',
            'Cao Bằng',
            'Bắc Kạn',
            'Tuyên Quang',
            'Lào Cai',
            'Yên Bái',
            'Thái Nguyên',
            'Lạng Sơn',
            'Bắc Giang',
            'Phú Thọ',
            'Điện Biên',
            'Lai Châu',
            'Sơn La',
            'Hòa Bình',
            'Hoà Bình',
            'Thanh Hóa',
            'Thanh Hoá',
            'Nghệ An',
            'Hà Tĩnh',
            'Quảng Bình',
            'Quảng Trị',
            'Thừa Thiên - Huế',
            'Thừa Thiên-Huế',
            'Thừa Thiên Huế',
            'Đà Nẵng',
            'Quảng Nam',
            'Quảng Ngãi',
            'Bình Định',
            'Phú Yên',
            'Khánh Hòa',
            'Khánh Hoà',
            'Ninh Thuận',
            'Bình Thuận',
            'Tây Nguyên',
            'Kon Tum',
            'Gia Lai',
            'Đắk Lắk',
            'Đắk Nông',
            'Lâm Đồng',
            'Bình Phước',
            'Tây Ninh',
            'Bình Dương',
            'Đồng Nai',
            'Bà Rịa - Vũng Tàu',
            'TP. Hồ Chí Minh',
            'TP.Hồ Chí Minh',
            'Long An',
            'Tiền Giang',
            'Bến Tre',
            'Trà Vinh',
            'Vĩnh Long',
            'Đồng Tháp',
            'An Giang',
            'Kiên Giang',
            'Cần Thơ',
            'Hậu Giang',
            'Sóc Trăng',
            'Bạc Liêu',
            'Cà Mau'
        ]

        # Duyệt qua từng tỉnh thành và chọn năm nhập vào
        for province_text in province_texts_selected:
            try:
                Select(province_select).select_by_visible_text(province_text)  # Chọn tỉnh thành
            except:
                print(f"Cannot select '{province_text}'")

        year_select = select_elements[1]  # Thẻ <select> thứ hai
        Select(year_select).select_by_visible_text(str(year_input))  # Chọn năm

        if self.table_name == 'crimes':
            crime_select = select_elements[2]
            Select(crime_select).select_by_visible_text('Số vụ án đã bị khởi tố')

        if self.table_name == 'medicals':
            medical_select = select_elements[2]
            Select(medical_select).select_by_visible_text('Tổng số')

        # Click vào button 'Tiếp tục'
        continue_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Tiếp tục']")))
        continue_button.click()

        # Kiểm tra và xử lý popup (nếu có)
        self.handle_popup()
        
        # Lấy tất cả các bảng trên trang
        tables = self.driver.find_elements(By.TAG_NAME, "table")

        # Lấy bảng cuối cùng và list <td> của bảng
        last_table = tables[2]
        list_td = last_table.find_elements(By.TAG_NAME, "td")

        for td in list_td:
            try:
                th = td.find_element(By.XPATH, "./preceding-sibling::th")

                # Lưu kết quả vào cơ sở dữ liệu
                self.save_to_db(th.text, str(year_input), td.text)
            except:
                print(f'this <td> {td.text} is not lie next to <th>')

    # Hàm chạy chương trình
    def run(self, years):
        try:
            for year_input in years:
                self.scrape_data(year_input)
        finally:
            self.driver.quit()
            self.conn.commit()
            self.conn.close()
            print("Đã lưu dữ liệu thành công vào SQLite.")

# Ví dụ sử dụng
if __name__ == "__main__":
    # luc luong lao dong
    url = "https://www.gso.gov.vn/px-web-2/?pxid=V0237&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng"
    # 2021, 2022, Sơ bộ 2023
    years = ['2021']
    table_name = 'labor_force'
    column_name = 'labor_force'

    # thu nhap binh quan
    # url = "https://www.gso.gov.vn/px-web-2/?pxid=V1437&theme=Y%20t%E1%BA%BF%2C%20v%C4%83n%20h%C3%B3a%20v%C3%A0%20%C4%91%E1%BB%9Di%20s%E1%BB%91ng"
    # # 2021, 2022, Sơ bộ 2023
    # years = ['2021']
    # table_name = 'income'
    # column_name = 'money'

    # ti le toi pham
    # url = "https://www.gso.gov.vn/px-web-2/?pxid=V1466&theme=Y%20t%E1%BA%BF%2C%20v%C4%83n%20h%C3%B3a%20v%C3%A0%20%C4%91%E1%BB%9Di%20s%E1%BB%91ng"
    # # 2022, 2023
    # years = ['2023']
    # table_name = 'crimes'
    # column_name = 'cases'

    # y te: so co so kham chua benh
    # url = "https://www.gso.gov.vn/px-web-2/?pxid=V1405&theme=Y%20t%E1%BA%BF%2C%20v%C4%83n%20h%C3%B3a%20v%C3%A0%20%C4%91%E1%BB%9Di%20s%E1%BB%91ng"
    # # 2015, 2016, 2017
    # years = ['2017']
    # table_name = 'medicals'
    # column_name = 'totals'

    crawler = CrawlData(url, table_name=table_name, column_name=column_name)
    crawler.run(years)
