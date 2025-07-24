FROM python:3.11-slim
WORKDIR /app

# Копируем и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код (app.py, import_sheets.py и проч.)
COPY . .

# По умолчанию запускаем API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
