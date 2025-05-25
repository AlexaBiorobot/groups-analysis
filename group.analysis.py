# stats_slack.py

import os
import gspread
import pandas as pd
import requests

# --- Настройки Google Sheets ---
SPREADSHEET_ID = "1_S-NyaVKuOc0xK12PBAYvdIauDBq9mdqHlnKLfSYNAE"
SHEET_NAME     = "groups"
CREDS_PATH     = os.getenv("GOOGLE_CREDS_JSON_PATH", "/etc/myapp/gspread_creds.json")

# --- Настройки Slack ---
# Задайте в окружении:
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def fetch_and_compute():
    # Авторизация
    gc = gspread.service_account(filename=CREDS_PATH)
    ws = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    df = pd.DataFrame(ws.get_all_records())

    # Приводим к числам
    df["F"]  = pd.to_numeric(df["F"],  errors="coerce")
    df["AA"] = pd.to_numeric(df["AA"], errors="coerce")

    # Условия
    c1 = df["B"].str.contains("COL", na=False) & (df["F"] == 14)
    c2 = df["B"].str.contains("COL", na=False) & (df["F"] == 9)
    c3 = df["B"].str.contains("COL", na=False) & df["B"].str.contains("PRM", na=False)

    return df.loc[c1, "AA"].mean(), df.loc[c2, "AA"].mean(), df.loc[c3, "AA"].mean()

def send_slack(text: str):
    payload = {"text": text}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload)
    resp.raise_for_status()

if __name__ == "__main__":
    avg1, avg2, avg3 = fetch_and_compute()
    message = (
        "*📊 Средние AA (таблица groups):*\n"
        f"> B содержит COL и F=14: `{avg1:.2f}`\n"
        f"> B содержит COL и F=9:  `{avg2:.2f}`\n"
        f"> B содержит COL и PRM: `{avg3:.2f}`"
    )
    send_slack(message)
