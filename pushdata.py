import os
import pandas as pd
from sqlalchemy import create_engine

# Danh sách các file Excel và tên bảng tương ứng
files_and_tables = {
    'data/sltk_doanhthu_dulich_diaphuong1.xlsx': 'dtdl_VN_tydong',
    'data/sltk_doanhthu_dulich_vungdiaphuong.xlsx': 'dtvdl_VN_tydong',  # Thêm file và tên bảng mới tại đây
    # Bạn có thể thêm nhiều file và tên bảng hơn
}

# Thiết lập kết nối tới SQLite
DATABASE_URI = 'sqlite:///data_sqlite.db'
engine = create_engine(DATABASE_URI)

# Nhập dữ liệu từ từng file vào từng bảng
for file_path, table_name in files_and_tables.items():
    # Kiểm tra xem file có tồn tại không
    if os.path.exists(file_path):
        try:
            # Đọc dữ liệu từ file Excel
            df = pd.read_excel(file_path)
            # Kiểm tra dữ liệu
            print(f"Dữ liệu từ {file_path}:")
            print(df.head())

            # Đưa dữ liệu vào bảng tương ứng
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)

            print(f"Dữ liệu đã được nhập vào bảng '{table_name}' thành công!")

        except Exception as e:
            print(f"Đã xảy ra lỗi khi nhập dữ liệu từ '{file_path}': {e}")
    else:
        print(f"Tệp '{file_path}' không tồn tại. Vui lòng kiểm tra lại đường dẫn và tên tệp.")
