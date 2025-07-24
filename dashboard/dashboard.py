import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Lesson Dashboard")
st.title("Отчёт по урокам")

# 1) Параметры фильтра
col1, col2, col3 = st.columns(3)
with col1:
    start = st.date_input("Начало периода", pd.to_datetime("2025-01-01"))
with col2:
    end   = st.date_input("Конец периода",   pd.to_datetime("2025-12-31"))
with col3:
    lesson = st.text_input("Тип урока (O)", "")

# 2) Базовый URL API
# По умолчанию внутри Docker Compose имя хоста "backend"
backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

# 3) Собираем GET-параметры, но только непустые
params = {
    "start": start.strftime("%Y-%m-%d"),
    "end":   end.strftime("%Y-%m-%d"),
}
if lesson:
    params["lesson"] = lesson

# 4) Формируем строку запроса
query = "&".join(f"{k}={v}" for k, v in params.items())
url = f"{backend_url}/api/data/?{query}"
st.write("Запрос к API:", url)

# 5) Читаем JSON
df = pd.read_json(url)

# 6) Выводим данные и графики
st.subheader("Исходные данные")
st.dataframe(df)

st.subheader("Уникальные репетиторы")
st.write(df["tutor_j"].nunique())

st.subheader("Средний X")
st.write(df["score_x"].mean())

st.subheader("Динамика X по дате")
chart_df = df.groupby("lesson_date")["score_x"].mean().reset_index()
st.line_chart(
    chart_df.set_index("lesson_date")["score_x"]
)
