from __future__ import annotations

from datetime import date

from app.etl.extract import extract_daily_raw_data
from app.etl.transform import transform_daily_data
from app.etl.load import load_daily_data


def refresh_nba_data_for_date(target_date: date) -> dict:
    raw_data = extract_daily_raw_data(target_date)
    transformed = transform_daily_data(raw_data)
    result = load_daily_data(transformed, target_date)

    result["target_date"] = str(target_date)
    return result