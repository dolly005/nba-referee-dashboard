from __future__ import annotations

import os
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Query, HTTPException

from app.etl.pipeline import refresh_nba_data_for_date


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/refresh-data")
def refresh_data(
    date_: date = Query(..., alias="date", description="格式：YYYY-MM-DD，例如 2024-01-15")
):
    """
    手動補爬指定日期：
    POST /api/admin/refresh-data?date=2024-01-15
    """
    try:
        result = refresh_nba_data_for_date(date_)
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Refresh failed: {exc}",
        )


@router.post("/import-csv")
async def import_csv_files(
    games_file: Optional[UploadFile] = File(None),
    officials_file: Optional[UploadFile] = File(None),
    merged_file: Optional[UploadFile] = File(None),
):
    """
    保留 CSV 相容機制。
    這個 endpoint 先把上傳的 CSV 存到 backend/uploaded_csv。
    之後如果你要接原本 import_csv.py，可以在這裡呼叫你的匯入函式。

    Swagger 測試方式：
    1. 打開 http://localhost:8000/docs
    2. 找 POST /api/admin/import-csv
    3. Upload CSV
    """
    upload_dir = Path("uploaded_csv")
    upload_dir.mkdir(exist_ok=True)

    saved_files = []

    for file in [games_file, officials_file, merged_file]:
        if file is None:
            continue

        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a CSV file.",
            )

        save_path = upload_dir / file.filename

        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(str(save_path))

    return {
        "status": "success",
        "message": "CSV files uploaded. You can now run your import_csv.py logic if needed.",
        "saved_files": saved_files,
    }