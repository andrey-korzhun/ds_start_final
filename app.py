import streamlit as st
import pandas as pd


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

st.write(new_data.head())
st.write(new_data.head())
