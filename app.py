from flask import Flask, render_template
import sqlite3
from wordcloud import WordCloud
import os
from config import Config

app = Flask(__name__)

# Lấy dữ liệu population từ SQLite
def get_population_data():
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT province_name, average_population 
                   FROM population 
                   ORDER BY average_population DESC 
                   LIMIT 10''')
    data = cursor.fetchall()
    conn.close()
    return data

# Tạo word cloud từ dữ liệu
def create_word_cloud(data):
    word_freq = {item[0]: item[1] for item in data}
    
    wordcloud = WordCloud(width=800, height=400, 
                          background_color="white").generate_from_frequencies(word_freq)
    
    # Đảm bảo thư mục tồn tại
    if not os.path.exists('static/images'):
        os.makedirs('static/images')
    
    # Lưu word cloud thành file hình ảnh
    wordcloud.to_file('static/images/wordcloud.png')

# Route để hiển thị popluation theo bar chart
@app.route('/')
def homepage():
    data = get_population_data()  # Lấy dữ liệu từ SQLite
    
    # Chuẩn bị dữ liệu cho biểu đồ
    province_names = [item[0] for item in data]
    average_populations = [item[1] for item in data]

    return render_template('population_chart.html', province_names=province_names, average_populations=average_populations)

# Route để hiển thị popluation theo word cloud
@app.route('/population_chart_wc')
def population_chart_wc():
    data = get_population_data()  # Lấy dữ liệu từ SQLite
    
    # Tạo word cloud từ dữ liệu
    create_word_cloud(data)
    
    # Hiển thị word cloud trên trang
    return render_template('population_chart_wc.html')

# Lấy dữ liệu labor force từ SQLite
def get_labor_data():
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT province, labor_force 
                   FROM labor_force 
                   ORDER BY labor_force DESC 
                   LIMIT 10''')
    data = cursor.fetchall()
    conn.close()
    return data

# Route để hiển thị labor force theo line chart
@app.route('/labor_force_chart')
def labor_force_chart():
    data = get_labor_data()  # Lấy dữ liệu từ SQLite

    return render_template('labor_force_chart.html', data=data)

# Lấy dữ liệu income từ SQLite
def get_income_data():
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT province, money 
                   FROM income 
                   ORDER BY money DESC 
                   LIMIT 10''')
    data = cursor.fetchall()
    conn.close()
    return data

# Route để hiển thị income theo Doughnut Chart
@app.route('/income_chart')
def income_doughnut_chart():
    data = get_income_data()  # Lấy dữ liệu từ SQLite
    provinces = [row[0] for row in data]
    money = [row[1] for row in data]

    sendingData = {"provinces": provinces, "money": money}

    return render_template('income_chart.html', data=sendingData)

if __name__ == '__main__':
    # app.run(debug=True)
    import os
    port = int(os.environ.get('PORT', 8080))  # Dùng 8080 là port mặc định khi không có biến môi trường
    app.run(host='0.0.0.0', port=port)
