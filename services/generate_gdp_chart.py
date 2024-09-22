import pandas as pd
import plotly.express as px
import plotly.io as pio

# Tạo biểu đồ bằng plotly
def create_gdp_chart(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected df to be a pandas DataFrame")
    
    # In ra tên cột để kiểm tra
    print(df.columns)

    # Chuyển đổi dữ liệu thành dạng dài (long format)
    df_long = df.melt(id_vars=['descriptor'],  # Sử dụng 'descriptor' thay vì 'indicator'
                      var_name='Year', 
                      value_name='GDP')
    
    # Tạo biểu đồ với plotly
    fig = px.line(df_long, x='Year', y='GDP', color='descriptor', markers=True,
                  title='Dữ liệu các năm 2016-2022',
                  labels={'GDP': 'GDP', 'Year': 'Year', 'descriptor': 'Descriptor'})
    
    fig.update_layout(transition_duration=500)
    return pio.to_html(fig, full_html=False)
