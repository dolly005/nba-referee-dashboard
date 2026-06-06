from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.etl.pipeline import refresh_nba_data_for_date


TAIWAN_TZ = ZoneInfo("Asia/Taipei")


scheduler = BackgroundScheduler(timezone=TAIWAN_TZ)


def refresh_yesterday_games():
    """
    每天凌晨 5 點執行。
    抓台灣時間「昨天」的 NBA 比賽資料。
    """
    now_tw = datetime.now(TAIWAN_TZ)
    target_date = (now_tw - timedelta(days=1)).date()

    print(f"[scheduler] Refresh NBA data for {target_date}")
    result = refresh_nba_data_for_date(target_date)
    print(f"[scheduler] Done: {result}")


def start_scheduler():
    """
    啟動排程器。
    注意：部署到 Render 時，請只開一個 worker，避免排程重複跑。
    """
    if scheduler.running:
        return

    scheduler.add_job(
        refresh_yesterday_games,
        trigger=CronTrigger(
            hour=5,
            minute=0,
            timezone=TAIWAN_TZ,
        ),
        id="daily_nba_refresh",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
    print("[scheduler] APScheduler started. Daily refresh time: 05:00 Asia/Taipei")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[scheduler] APScheduler stopped.")