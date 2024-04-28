import streamlit as st
import pandas as pd

import re
import plotly

import plotly.graph_objects as go
import plotly.express as px

from plotly.subplots import make_subplots


st.set_page_config('Проект: анализ зарплат в России', layout='wide', initial_sidebar_state='auto')
st.subheader('Данные об инфляции')

url = 'https://xn----ctbjnaatncev9av3a8f8b.xn--p1ai/%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8B-%D0%B8%D0%BD%D1%84%D0%BB%D1%8F%D1%86%D0%B8%D0%B8'
df_infl = pd.read_html(url, index_col='Год', )[0]
st.write(df_infl.head())


st.markdown("#### Данные о номинальной начисленной заработной плате")
url = 'https://rosstat.gov.ru/storage/mediabank/tab3-zpl_2023.xlsx'

new_data = pd.read_excel(url, sheet_name='с 2017 г.', header=4)
old_data = pd.read_excel(url, sheet_name='2000-2016 гг.', header=2)

new_data = new_data.set_axis(['Отрасль'] + [str(x) for x in range(2017, 2024)], axis='columns')
old_data = old_data.set_axis(['Отрасль'] + [str(x) for x in range(2000, 2017)], axis='columns')

new_data = new_data.dropna(how='any')
old_data = old_data.dropna(how='any')

st.write(old_data.head())
st.write(new_data.head())

infl = df_infl.loc[df_infl.index >= 2000 , 'Всего'][1:].sort_index()
infl.name = 'Инфляция'

def sanitaze_str(str):
    str = str.strip().capitalize()
    str = re.sub(r'\s{2,}', ' ', str)
    if str in col_name_mapping:
        str = col_name_mapping[str]
    return str


def discount(year_from, year_to, sum):
    result = sum
    for x in range(year_from, year_to, -1):
        result /= 1.0 + infl.loc[x] / 100.0
    return result


def compound(year_from, year_to, sum):
    result = sum
    for x in range(year_from, year_to):
        result *= 1.0 + infl.loc[x] / 100.0
    return result


def get_line(data, name):
    line = data[data['Отрасль'] == name].drop(['Отрасль'], axis=1)
    line = line.squeeze()
    line.index = line.index.map(int)
    return line


col_name_mapping = {
    'Рыболовство, рыбоводство': 'Рыболовство и рыбоводство',
    'Производство кожи, изделий из кожи и производство обуви': 'Производство кожи и изделий из кожи',
    'Производство резиновых и пластмассовых изделий': 'Производство резиновых и пластмассовых изделий',
    'Торговля оптовая и розничная; ремонт автотранспортных средств и мотоциклов': 'Оптовая и розничная торговля; ремонт автотранспортных средств, мотоциклов, бытовых изделий и предметов личного пользования',
    'Деятельность финансовая и страховая': 'Финансовая деятельность',
    'Государственное управление и обеспечение военной безопасности; социальное обеспечение': 'Государственное управление и обеспечение военной безопасности; социальное страхование',
    'Деятельность в области здравоохранения и социальных услуг': 'Здравоохранение и предоставление социальных услуг',
    'Всего': 'Средняя',
    'Всего по экономике': 'Средняя',
}

new_data['Отрасль'] = new_data['Отрасль'].apply(sanitaze_str)
old_data['Отрасль'] = old_data['Отрасль'].apply(sanitaze_str)
data = old_data.merge(new_data, on='Отрасль')


data_2000 = data.copy()

for year in infl.index:
    data_2000[str(year)] = discount(year, 2000, data_2000[str(year)])

color, colors = 0, plotly.colors.qualitative.Plotly
fig = go.Figure()
# выбранные отрасли + среднее по всем отраслям
lines = ['Образование', 'Финансовая деятельность', 'Строительство', 'Средняя']

for name in lines:
    dt = get_line(data, name)
    dt_real = get_line(data_2000, name)
    fig.add_trace(go.Scatter(x=dt_real.index, y=dt_real.array, name=name + ' с учетом инфл.', line=dict(color=colors[color])))
    fig.add_trace(go.Scatter(x=dt.index, y=dt.array, name=name, line=dict(dash='dot', color=colors[color])))
    color += 1

fig.update_layout(xaxis_title='год', yaxis_title='з/п, руб.', yaxis_type='log',
                  margin=dict(l=20,r=20,b=10,t=40))


st.plotly_chart(fig, use_container_width=True)
