import streamlit as st
import gspread
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = "1_S-NyaVKuOc0xK12PBAYvdIauDBq9mdqHlnKLfSYNAE"
SHEET_NAME = "groups"

def fetch_and_compute():
    # Авторизация через сервисный аккаунт из Streamlit secrets
    creds_dict = st.secrets["gcp_service_account"]
    client = gspread.service_account_from_dict(creds_dict)

    # Загрузка данных
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    df = pd.DataFrame(sheet.get_all_records())

    # Приводим колонки к числовому типу там, где нужно
    df['F'] = pd.to_numeric(df['F'], errors='coerce')
    df['AA'] = pd.to_numeric(df['AA'], errors='coerce')

    # Условия фильтрации
    cond1 = df['B'].str.contains("COL", na=False) & (df['F'] == 14)
    cond2 = df['B'].str.contains("COL", na=False) & (df['F'] == 9)
    cond3 = df['B'].str.contains("COL", na=False) & df['B'].str.contains("PRM", na=False)

    # Вычисление средних
    avg1 = df.loc[cond1, 'AA'].mean()
    avg2 = df.loc[cond2, 'AA'].mean()
    avg3 = df.loc[cond3, 'AA'].mean()

    # Выводим в консоль (или можно сохранять куда угодно)
    print(f"Среднее AA для B содержит COL и F=14: {avg1:.2f}")
    print(f"Среднее AA для B содержит COL и F=9:  {avg2:.2f}")
    print(f"Среднее AA для B содержит COL и PRM: {avg3:.2f}")

if __name__ == "__main__":
    # Планировщик на каждый понедельник в 11:00 Europe/Lisbon
    scheduler = BlockingScheduler(timezone=pytz.timezone("Europe/Lisbon"))
    scheduler.add_job(
        fetch_and_compute,
        trigger="cron",
        day_of_week="mon",
        hour=11,
        minute=0
    )
    print("Scheduler started: каждый понедельник в 11:00 (Lisbon).")
    scheduler.start()
