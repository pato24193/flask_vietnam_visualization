import sqlite3
# for importing config file
import sys
import requests
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

# Tạo database và table nếu chưa có
def init_db():
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS population (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            province_code TEXT UNIQUE,
            province_name TEXT,
            average_population REAL
        )
    ''')
    conn.commit()
    conn.close()

# Gọi API và lưu vào SQLite
def fetch_and_store_data():
    url = "https://apigis.gso.gov.vn/api/web/exportdetail"
    payload = {
        "province_code": "00",
        "years": ["2022"],
        "import_type": 1
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = response.json()
        data_export = json_data['data']['dataExport']  # Lấy list từ dataExport
        
        conn = sqlite3.connect(Config.DB_NAME)
        cursor = conn.cursor()

        # Lưu dữ liệu vào bảng hoặc cập nhật nếu đã tồn tại
        for item in data_export:
            # skip 'TOÀN QUỐC'
            if item[1] == "":
                continue
            province_code = item[0]
            province_name = item[1]
            average_population = item[2] if item[2] != "" else 0 

            # Sử dụng INSERT OR REPLACE để cập nhật nếu province_code đã tồn tại
            cursor.execute('''
                INSERT OR REPLACE INTO population (province_code, province_name, average_population) 
                VALUES (?, ?, ?)
            ''', (province_code, province_name, average_population))
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    init_db()  # Tạo bảng nếu chưa có
    fetch_and_store_data()  # Lấy và lưu dữ liệu từ API
