# backend/import_sheets.py
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine
from gspread_dataframe import get_as_dataframe

def main():
    # --- 1) Авторизация в Google Sheets ---
    creds_path = os.getenv("GOOGLE_SHEETS_KEYFILE")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # --- 2) Читаем весь лист lessons LATAM ---
    ss = client.open_by_key(os.getenv("GOOGLE_SHEETS_SOURCE_SS_ID"))
    ws = ss.worksheet(os.getenv("GOOGLE_SHEETS_SOURCE_SHEET"))

    # Получаем DataFrame, первая строка — заголовки
    df = get_as_dataframe(ws,
                          evaluate_formulas=True,  # считаем формулы
                          header=0                  # первая строка — названия колонок
                         )
    # Убираем полностью пустые строки и колонки
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)

    # Опционально: нормализуем названия колонок (strip, lower, _ вместо пробелов)
    df.columns = [
        col.strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    # --- 3) Записываем в Postgres ---
    db_url = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )
    engine = create_engine(db_url, pool_pre_ping=True)

    # При первом запуске создастся таблица lesson_data со всеми колонками из листа
    df.to_sql("lesson_data", engine, if_exists="replace", index=False)
    print(f"→ Imported {len(df)} rows and {len(df.columns)} columns into lesson_data")

if __name__ == "__main__":
    main()
