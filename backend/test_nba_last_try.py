import json
import time
import requests

BASE_PAGE = "https://www.nba.com/stats"
API_URL = "https://stats.nba.com/stats/leaguegamelog"

HEADERS = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/stats/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

PARAMS = {
    "Counter": "0",
    "DateFrom": "01/15/2024",
    "DateTo": "01/15/2024",
    "Direction": "ASC",
    "LeagueID": "00",
    "PlayerOrTeam": "T",
    "Season": "2023-24",
    "SeasonType": "Regular Season",
    "Sorter": "DATE",
}

print("Last try: warm-up + direct stats request")
print("Step 1: open NBA stats page first...")

session = requests.Session()

try:
    warm = session.get(
        BASE_PAGE,
        headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept-Language": HEADERS["Accept-Language"],
        },
        timeout=(10, 60),
    )
    print("Warm-up status:", warm.status_code)
    print("Cookies after warm-up:", session.cookies.get_dict())

    time.sleep(3)

    print("\nStep 2: request LeagueGameLog...")
    response = session.get(
        API_URL,
        headers=HEADERS,
        params=PARAMS,
        timeout=(10, 180),
    )

    print("Final URL:")
    print(response.url)
    print("Status code:", response.status_code)
    print("Content type:", response.headers.get("content-type"))
    print("First 300 chars:")
    print(response.text[:300])

    if response.status_code != 200:
        raise SystemExit

    data = response.json()

    result_sets = data.get("resultSets", [])
    if not result_sets:
        print("No resultSets found.")
        raise SystemExit

    first = result_sets[0]
    headers = first.get("headers", [])
    rows = first.get("rowSet", [])

    print("\nColumns:")
    print(headers)

    print("\nRows count:")
    print(len(rows))

    print("\nFirst 5 rows:")
    for row in rows[:5]:
        print(row)

except Exception as e:
    print("\nERROR:")
    print(type(e))
    print(e)