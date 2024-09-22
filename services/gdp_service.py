import sqlite3
import pandas as pd
import requests


def fetch_and_store_data_gdp():
    filename = download_gdp_excel()
    data = read_gdp_excel(filename)
    save_gdp_data_to_sqlite(data)
    
# Tải file Excel về từ URL
def download_gdp_excel():
    url = "https://nsdp.gso.gov.vn/GSO-chung/Tu%E1%BA%A5n%20Anh/excel%20chung/GDP_VNM.xlsx"
    response = requests.get(url)
    file_name = "GDP_VNM.xlsx"
    with open(file_name, 'wb') as file:
        file.write(response.content)
    return file_name

# Đọc file Excel từ đường dẫn
def read_gdp_excel(file_name):
    # Đọc toàn bộ dữ liệu từ sheet, không sử dụng header
    df = pd.read_excel(file_name, sheet_name='Dataset_A_2004-2019', header=None, engine='openpyxl')
    
    # Xác định vị trí các cột năm
    year_columns = {}
    for col in range(len(df.columns)):
        cell_value = df.iloc[8, col]
        if not pd.isna(cell_value) and isinstance(cell_value, (float, int)):
            try:
                int_value = int(cell_value)
                if int_value in range(2016, 2023):
                    year_columns[int_value] = col
            except ValueError:
                # Nếu không thể chuyển đổi giá trị, bỏ qua
                pass
    
    # Lấy dữ liệu từ các row tương ứng, bắt đầu từ row 11 đến 91 và bỏ qua row 22, 34, 63
    df_filtered = df.iloc[10:91, [2, 3] + list(year_columns.values())]  # Cột 2: INDICATOR, Cột 3: Descriptor Vietnamese
    df_filtered = df_filtered.drop([21, 33, 62])  # Bỏ row 22, 34, 63

    # Đặt lại tên cột cho dễ hiểu
    df_filtered.columns = ['INDICATOR', 'Descriptor Vietnamese'] + list(year_columns.keys())

    return df_filtered

# Lưu dữ liệu vào SQLite
def save_gdp_data_to_sqlite(df):
    conn = sqlite3.connect('data_sqlite.db')
    cursor = conn.cursor()
    
    # Tạo bảng nếu chưa có
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GDPAvg (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator TEXT,
            descriptor TEXT,
            year_2016 REAL,
            year_2017 REAL,
            year_2018 REAL,
            year_2019 REAL,
            year_2020 REAL,
            year_2021 REAL,
            year_2022 REAL
        )
    ''')
    
    cursor.execute('DELETE FROM GDPAvg')
    
    # Lưu từng dòng dữ liệu vào bảng
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO GDPAvg (indicator, descriptor, year_2016, year_2017, year_2018, year_2019, year_2020, year_2021, year_2022)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['INDICATOR'], 
            row['Descriptor Vietnamese'], 
            row.get(2016, None), row.get(2017, None), row.get(2018, None), 
            row.get(2019, None), row.get(2020, None), row.get(2021, None), 
            row.get(2022, None)
        ))
    
    conn.commit()
    conn.close()
    
# Lấy dữ liệu từ SQLite
def get_gdp_data_from_db():
    conn = sqlite3.connect('data_sqlite.db')
    query = "SELECT descriptor, year_2016 AS '2016', year_2017 AS '2017', year_2018 AS '2018', year_2019 AS '2019', year_2020 AS '2020', year_2021 AS '2021', year_2022 AS '2022' FROM GDPAvg WHERE indicator IN ('NGDPVA_ISIC4_A01_XDC', 'NGDPVA_ISIC4_A02_XDC', 'NGDPVA_ISIC4_A03_XDC', 'VNM_NGDPVA_ISIC4_BTE_XDC', 'NGDPVA_ISIC4_F_XDC', 'VNM_NGDPVA_ISIC4_GTT_XDC')"
    df = pd.read_sql_query(query, conn)  # Đảm bảo trả về DataFrame
    conn.close()
    return df