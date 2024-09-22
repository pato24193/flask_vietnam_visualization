import sqlite3
import plotly.express as px
from flask import json
import pandas as pd

def generate_map_fig(df_population, year):
        
    # Quy đổi đơn vị (nghìn người)
    df_population['population_2021'] *= 1000
    df_population['population_2022'] *= 1000
    df_population['population_2023'] *= 1000
    
    with open('./static/geojsons/diaphantinh.geojson', 'r', encoding='utf-8') as f:
        vietnam_geojson = json.load(f)
    population_column = f'population_{year}'
    fig_map = px.choropleth(df_population,
                            geojson=vietnam_geojson,
                            featureidkey='properties.ten_tinh',
                            locations='province_name',
                            color=population_column,  # Dân số theo năm đã chọn
                            color_continuous_scale=["#FFECB3", "#FFD54F", "#FFB74D", "#FF8A65", "#FF5252"],
                            title=f"Bản đồ dân số Việt Nam theo tỉnh (Năm {year})",
                            labels={'province_name': 'Tỉnh', 'population': f'Dân số năm {year}'}
                            )

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    return fig_map.to_json()

def generate_bar_fig(df_population, year):
    # Quy đổi đơn vị (nghìn người)
    df_population['population_2021'] *= 1000
    df_population['population_2022'] *= 1000
    df_population['population_2023'] *= 1000
    
    # Reshape the dataframe to have 'year' and 'population' columns for multi-year data
    df_population_melted = pd.melt(df_population, 
                                   id_vars=['province_name'], 
                                   value_vars=['population_2021', 'population_2022', 'population_2023'],
                                   var_name='year', value_name='population')

    # Lọc dữ liệu theo năm đã chọn
    df_filtered = df_population_melted[df_population_melted['year'] == f'population_{year}']

    # Tạo biểu đồ cột cho dân số theo từng tỉnh
    fig_bar = px.bar(df_filtered,
                     x='province_name',
                     y='population',
                     title=f'Dân số theo tỉnh (Năm {year})',
                     labels={'province_name': 'Tỉnh', 'population': 'Dân số'},
                     color_discrete_sequence=['#FF5252']  # Màu cho biểu đồ cột
                     )

    # Format the hover template to display population with commas
    fig_bar.update_traces(
        hovertemplate="<b>%{x}</b><br>Dân số: %{y:,}<extra></extra>"
    )
    
    # Adjust layout for better readability
    fig_bar.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, xaxis_tickangle=-45)
    graph_bar_json = fig_bar.to_json()
    return graph_bar_json

