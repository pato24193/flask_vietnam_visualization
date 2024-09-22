import json
import plotly.utils
from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from wordcloud import WordCloud
import os
from config import Config
from services.gdp_service import fetch_and_store_data_gdp, get_gdp_data_from_db
from services.generate_gdp_chart import create_gdp_chart
from services.generate_populations_fig import generate_bar_fig, generate_map_fig
from services.population_service import read_population_data_from_excel, save_population_data_to_sqlite

app = Flask(__name__)

# ################# Minh: comment out un-used code
# Lấy dữ liệu population từ SQLite
# def get_population_data():
#     conn = sqlite3.connect(Config.DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('''SELECT province_name, average_population 
#                    FROM population 
#                    ORDER BY average_population DESC 
#                    LIMIT 10''')
#     data = cursor.fetchall()
#     conn.close()
#     return data

# Tạo word cloud từ dữ liệu
# def create_word_cloud(data):
#     word_freq = {item[0]: item[1] for item in data}
    
#     wordcloud = WordCloud(width=800, height=400, 
#                           background_color="white").generate_from_frequencies(word_freq)
    
#     # Đảm bảo thư mục tồn tại
#     if not os.path.exists('static/images'):
#         os.makedirs('static/images')
    
#     # Lưu word cloud thành file hình ảnh
#     wordcloud.to_file('static/images/wordcloud.png')

# Route để hiển thị popluation theo bar chart
# @app.route('/')
# def homepage():
#     data = get_population_data()  # Lấy dữ liệu từ SQLite
    
#     # Chuẩn bị dữ liệu cho biểu đồ
#     province_names = [item[0] for item in data]
#     average_populations = [item[1] for item in data]

#     return render_template('population_chart.html', province_names=province_names, average_populations=average_populations)

# Route để hiển thị popluation theo word cloud
# @app.route('/population_chart_wc')
# def population_chart_wc():
#     data = get_population_data()  # Lấy dữ liệu từ SQLite
    
#     # Tạo word cloud từ dữ liệu
#     create_word_cloud(data)
    
#     # Hiển thị word cloud trên trang
#     return render_template('population_chart_wc.html')
# ################# Minh: comment out un-used code

def get_crime_data(year):
    # Connect to the database
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()

    # Fetch data for the selected year
    cursor.execute('''SELECT province, cases FROM crimes WHERE year = ?''', (year,))
    data = cursor.fetchall()

    # Creating DataFrame
    df = pd.DataFrame(data, columns=['province', 'cases'])
    df['cases'] = pd.to_numeric(df['cases'], errors='coerce')

    # Convert 'cases' to the appropriate format
    df['cases'] = df['cases'].apply(lambda x: str(int(x)) if x.is_integer() else str(x).replace('.', '')).astype(int)

    # Sort values by 'cases' and take the top 10
    df_sorted = df.sort_values(by='cases', ascending=False).head(10)

    # Customize bar chart with colors and labels
    fig = go.Figure([go.Bar(
        x=df_sorted['province'],
        y=df_sorted['cases'],
        marker=dict(
            color=df_sorted['cases'],  # Coloring bars based on the values
            colorscale='YlOrRd',  # Choose a color scale
            showscale=True  # Show color scale on the side
        )
    )])

    # Update layout for better appearance
    fig.update_layout(
        title=f'Top 10 Provinces by Crime Cases in {year}',
        xaxis_title='Province',
        yaxis_title='Number of Cases',
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        yaxis=dict(
            showline=True,
            showgrid=True,
            gridcolor='lightgray',
            linecolor='black',
            linewidth=1
        ),
        xaxis=dict(
            showline=True,
            linecolor='black',
            linewidth=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(245,245,245,245)',  # Transparent page background
    )

    # Convert Plotly figure to JSON for rendering
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Close database connection
    conn.close()

    # Return the graph JSON
    return graph_json


# Route to display the crime chart
@app.route('/crime_chart')
def crime_chart():
    # Fetch available years from the database
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT DISTINCT year FROM crimes ORDER BY year''')
    years = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Render the template with the available years and an initial graph for the most recent year
    initial_year = years[-1]  # Assume the most recent year is the last one in the list
    graph_json = get_crime_data(initial_year)  # Initial graph for the most recent year
    return render_template('crime_chart.html', years=years, graph_json=graph_json, selected_year=initial_year)


@app.route('/update_crime_chart', methods=['POST'])
def update_crime_chart():
    # Get the selected year from the dropdown
    selected_year = request.form.get('year')
    # Get the updated graph data for the selected year
    graph_json = get_crime_data(selected_year)
    return graph_json

def get_medical_data(year):
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()

    # Query to fetch data based on the selected year
    cursor.execute('''SELECT province_name, year, totals FROM medicals WHERE year = ?''', (year,))
    data = cursor.fetchall()

    conn.close()

    # Creating DataFrame
    df = pd.DataFrame(data, columns=['province', 'year', 'totals'])

    # Sort by totals and take top 10
    df_sorted = df.sort_values(by='totals', ascending=False).head(10)

    # Create a horizontal bar chart
    fig = go.Figure([go.Bar(
        x=df_sorted['totals'],  # Values on the x-axis (totals)
        y=df_sorted['province'],  # Provinces on the y-axis
        orientation='h',  # Horizontal bar chart
        marker=dict(
            color=df_sorted['totals'],  # Coloring bars based on totals
            colorscale='Blues',  # Color scale for the bars
            showscale=True  # Display the color scale
        )
    )])

    # Update layout for better appearance
    fig.update_layout(
        title=f'Top 10 Provinces by Number of Health Facilities in {year}',
        xaxis_title='Number of Health Facilities',
        yaxis_title='Province',
        yaxis=dict(
            autorange="reversed",  # Ensure the largest bar is at the top
            showline=True,
            linecolor='black',  # Set line color for y-axis
            linewidth=1
        ),
        xaxis=dict(
            showgrid=True,  # Show grid lines on the x-axis
            showline=True,
            gridcolor='lightgray',  # Set the color of the grid lines
            gridwidth=1,  # Set the thickness of the grid lines
            linecolor='black',  # Set line color for y-axis
            linewidth=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent page background
    )

    # Convert plotly figure to JSON for rendering
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Return the graph JSON
    return graph_json

# Route to display the initial chart
@app.route('/medical_chart')
def medical_chart():
    # Fetch available years from the database
    conn = sqlite3.connect(Config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT DISTINCT year FROM medicals ORDER BY year''')
    years = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Initial year will be the latest one available
    initial_year = years[-1]
    graph_json = get_medical_data(initial_year)
    return render_template('medical_chart.html', years=years, graph_json=graph_json, selected_year=initial_year)

# Route to handle the year selection and update the chart
@app.route('/update_medical_chart', methods=['POST'])
def update_medical_chart():
    selected_year = request.form.get('year')
    graph_json = get_medical_data(selected_year)
    return graph_json

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

# Dashboard
@app.route('/')
def dashboard():
    return render_template('dashboard.html', title="Dashboard")

# Page Population
@app.route('/population')
def population_page():
    # Read data from the Excel file
    df_population = read_population_data_from_excel('./excel_data/danso.xlsx')

    # Save data into the SQLite database
    save_population_data_to_sqlite(df_population)
    
    # Kết nối tới SQLite để lấy dữ liệu dân số mới
    conn = sqlite3.connect('data_sqlite.db')
    default_year = 2023
    df_population = pd.read_sql_query('SELECT province_name, population_2021, population_2022, population_2023 FROM populations', conn)
    
    # Gen figure
    graph_map_json = generate_map_fig(df_population, default_year)
    graph_bar_json = generate_bar_fig(df_population, default_year)
    
    # Chuyển dữ liệu bảng thành JSON để hiển thị
    population_data = df_population.to_dict(orient='records')
    
    return render_template('population.html', graph_map_json=graph_map_json, graph_bar_json=graph_bar_json, population_data=population_data)

@app.route('/get_population_map/<int:year>')
def get_population_map(year):
    # Kết nối tới SQLite để lấy dữ liệu dân số theo năm
    conn = sqlite3.connect('data_sqlite.db')
    df_population = pd.read_sql_query(f'''
        SELECT province_name, population_2021, population_2022, population_2023
        FROM populations
    ''', conn)

    # Tạo bản đồ
    graph_map_json = generate_map_fig(df_population, year)
    
    return graph_map_json

@app.route('/get_population_bar/<int:year>')
def get_population_bar(year):
    conn = sqlite3.connect('data_sqlite.db')
    df_population = pd.read_sql_query('SELECT province_name, population_2021, population_2022, population_2023 FROM populations', conn)
    
    # Tạo biểu đồ cột cho năm đã chọn
    graph_bar_json = generate_bar_fig(df_population, year)
    
    return graph_bar_json

# Page GDP
@app.route('/gdp')
def gdp_page():
    fetch_and_store_data_gdp()
    df = get_gdp_data_from_db()
    chart = create_gdp_chart(df)
    
    gdp_data = df.to_dict(orient='records')
    
    return render_template('gdp.html', chart=chart, gdp_data=gdp_data)

if __name__ == '__main__':
    # app.run(debug=True)
    import os
    port = int(os.environ.get('PORT', 8080))  # Dùng 8080 là port mặc định khi không có biến môi trường
    app.run(host='0.0.0.0', port=port)
