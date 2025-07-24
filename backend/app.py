from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, text
import os

app = FastAPI()
db_url = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(db_url, pool_pre_ping=True)

class ReportRow(BaseModel):
    tutor_j: str
    lesson_date: str
    lesson_type: Optional[str]
    score_x: Optional[float]
    h_flag: Optional[int]

@app.get("/api/data/", response_model=List[ReportRow])
def get_data(
    start: str = Query(..., description="YYYY-MM-DD"),
    end:   str = Query(..., description="YYYY-MM-DD"),
    lesson: Optional[str] = Query(None)
):
    sql = """
    SELECT tutor_j, lesson_date, lesson_type, score_x, h_flag
      FROM lesson_data
     WHERE lesson_date BETWEEN :start AND :end
       AND (:lesson IS NULL OR lesson_type = :lesson)
     ORDER BY lesson_date;
    """
    with engine.begin() as conn:
        rows = conn.execute(text(sql), {"start": start, "end": end, "lesson": lesson}).fetchall()
    return [dict(r) for r in rows]
