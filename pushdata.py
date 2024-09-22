import os
import pandas as pd
from sqlalchemy import create_engine

# Đường dẫn chính xác tới file Excel
file_path = 'sltk_doanhthu_dulich_vungdiaphuong.xlsx'

# Kiểm tra xem file có tồn tại không
if os.path.exists(file_path):
    try:
        # Đọc dữ liệu từ file Excel
        df = pd.read_excel(file_path)
        # Kiểm tra dữ liệu
        print(df.head())

        # Thiết lập kết nối tới SQLite
        DATABASE_URI = 'sqlite:///data_sqlite.db'
        engine = create_engine(DATABASE_URI)

        # Đưa dữ liệu vào bảng 'KQT_phantheothitruong'
        df.to_sql('dtvdl_VN_tydong', con=engine, if_exists='replace', index=False)

        print("Dữ liệu đã được nhập vào cơ sở dữ liệu thành công!")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
else:
    print(f"Tệp '{file_path}' không tồn tại. Vui lòng kiểm tra lại đường dẫn và tên tệp.")
