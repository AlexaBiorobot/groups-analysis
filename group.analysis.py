import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

# --- Настройки доступа к Google Sheets ---
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"  # Ваш JSON-файл сервисного аккаунта
SPREADSHEET_ID = "1_S-NyaVKuOc0xK12PBAYvdIauDBq9mdqHlnKLfSYNAE"
SHEET_NAME = "groups"

# --- Функция получения и обработки данных ---
def fetch_and_compute():
    # Авторизация и загрузка листа
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()

    # Преобразуем в DataFrame
    df = pd.DataFrame(data)

    # Убедимся, что нужные колонки в правильном типе
    df['F'] = pd.to_numeric(df['F'], errors='coerce')
    df['AA'] = pd.to_numeric(df['AA'], errors='coerce')

    # Фильтрации и вычисления
    cond1 = df['B'].str.contains("COL", na=False) & (df['F'] == 14)
    cond2 = df['B'].str.contains("COL", na=False) & (df['F'] == 9)
    cond3 = df['B'].str.contains("COL", na=False) & df['B'].str.contains("PRM", na=False)

    avg1 = df.loc[cond1, 'AA'].mean()
    avg2 = df.loc[cond2, 'AA'].mean()
    avg3 = df.loc[cond3, 'AA'].mean()

    # Вывод результатов
    print("Среднее AA для B содержит COL и F=14: {:.2f}".format(avg1))
    print("Среднее AA для B содержит COL и F=9:  {:.2f}".format(avg2))
    print("Среднее AA для B содержит COL и PRM: {:.2f}".format(avg3))

# --- Планировщик ---
if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=pytz.timezone("Europe/Lisbon"))
    # каждый понедельник в 11:00
    scheduler.add_job(fetch_and_compute, trigger='cron',
                      day_of_week='mon', hour=11, minute=0)
    print("Scheduler started. Next run: every Monday at 11:00 Europe/Lisbon")
    scheduler.start()
