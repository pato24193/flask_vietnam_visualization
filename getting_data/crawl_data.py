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
        iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        self.driver.switch_to.frame(iframe)

        # Lấy tất cả các thẻ <select> trên trang
        select_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
        )

        # Thẻ <select> đầu tiên là province, thẻ thứ hai là year
        province_select = select_elements[0]  # Thẻ <select> đầu tiên

        # Lấy tất cả các tỉnh thành từ thẻ <select> đầu tiên
        provinces = [option.text for option in Select(province_select).options]
        regions = [
            'CẢ NƯỚC',
            'Đồng bằng sông Hồng',
            'Trung du và miền núi phía Bắc',
            'Bắc Trung Bộ và duyên hải miền Trung',
            'Đồng bằng sông Cửu Long',
            'Đông Nam Bộ'
        ]

        first = True

        # Duyệt qua từng tỉnh thành và chọn năm nhập vào
        for province_text in provinces:
            if province_text in regions:
                continue

            if not first:
                iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                self.driver.switch_to.frame(iframe)
                select_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
                )
            else:
                first = False

            province_select = select_elements[0]  # Thẻ <select> đầu tiên
            year_select = select_elements[1]  # Thẻ <select> thứ hai

            Select(province_select).select_by_visible_text(province_text)  # Chọn tỉnh thành
            Select(year_select).select_by_visible_text(str(year_input))  # Chọn năm

            # if self.db_name == 'income':
            #     source_salary = select_elements[2]
            #     Select(source_salary).select_by_visible_text('Thu từ tiền lương, tiền công')  # Chọn nguồn thu

            # Click vào button 'Tiếp tục'
            continue_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Tiếp tục']")))
            continue_button.click()

            # Kiểm tra và xử lý popup (nếu có)
            self.handle_popup()

            # Lấy tất cả các bảng trên trang
            tables = self.driver.find_elements(By.TAG_NAME, "table")

            # Lấy bảng cuối cùng và ô <td> cuối cùng của bảng
            last_table = tables[2]
            last_td = last_table.find_elements(By.TAG_NAME, "td")[-1]
            value_needed = last_td.text

            # Lưu kết quả vào cơ sở dữ liệu
            self.save_to_db(province_text, str(year_input), value_needed)

            self.driver.back()
            print(province_text)

    # Hàm chạy chương trình
    def run(self, year_input):
        try:
            self.scrape_data(year_input)
        finally:
            self.driver.quit()
            self.conn.commit()
            self.conn.close()
            print("Đã lưu dữ liệu thành công vào SQLite.")

# Ví dụ sử dụng
if __name__ == "__main__":
    # url = "https://www.gso.gov.vn/px-web-2/?pxid=V0237&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng"
    # year_input = 'Sơ bộ 2023'
    # table_name = 'labor_force'
    # column_name = 'labor_force'
    url = "https://www.gso.gov.vn/px-web-2/?pxid=V1437&theme=Y%20t%E1%BA%BF%2C%20v%C4%83n%20h%C3%B3a%20v%C3%A0%20%C4%91%E1%BB%9Di%20s%E1%BB%91ng"
    year_input = 'Sơ bộ 2023'
    table_name = 'income'
    column_name = 'money'
    crawler = CrawlData(url, table_name=table_name, column_name=column_name)
    crawler.run(year_input)
