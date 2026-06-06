import time
import pandas as pd
import requests

NBA_STATS_PAGE_URL = "https://www.nba.com/stats"
BOX_SCORE_SUMMARY_V2_URL = "https://stats.nba.com/stats/boxscoresummaryv2"

NBA_HEADERS = {
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

game_id = "0022300559"

print("Testing direct officials request...")
print("Game ID:", game_id)

session = requests.Session()

try:
    warm_response = session.get(
        NBA_STATS_PAGE_URL,
        headers={
            "User-Agent": NBA_HEADERS["User-Agent"],
            "Accept-Language": NBA_HEADERS["Accept-Language"],
        },
        timeout=(10, 60),
    )

    print("Warm-up status:", warm_response.status_code)
    print("Cookies:", session.cookies.get_dict())

    time.sleep(3)

    response = session.get(
        BOX_SCORE_SUMMARY_V2_URL,
        headers=NBA_HEADERS,
        params={"GameID": game_id},
        timeout=(10, 180),
    )

    print("Status code:", response.status_code)
    print("Content type:", response.headers.get("content-type"))
    print("First 300 chars:")
    print(response.text[:300])

    response.raise_for_status()

    data = response.json()
    result_sets = data.get("resultSets", [])

    print("\nNumber of result sets:", len(result_sets))

    for i, result in enumerate(result_sets):
        name = result.get("name")
        headers = result.get("headers", [])
        rows = result.get("rowSet", [])

        print(f"\nResult set {i}: {name}")
        print("Columns:", headers)
        print("Rows:", len(rows))

        if name == "Officials":
            officials_df = pd.DataFrame(rows, columns=headers)
            print("\nOfficials dataframe:")
            print(officials_df)
            print("\nOfficials columns:")
            print(officials_df.columns.tolist())

except Exception as e:
    print("\nERROR:")
    print(type(e))
    print(e)