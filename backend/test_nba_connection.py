import requests

url = "https://stats.nba.com/stats/leaguegamelog"

headers = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "x-nba-stats-origin": "stats",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
}

params = {
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

print("Testing direct request to stats.nba.com...")

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    print("Status code:", response.status_code)
    print("Content type:", response.headers.get("content-type"))
    print("First 500 chars:")
    print(response.text[:500])

except Exception as e:
    print("ERROR:")
    print(type(e))
    print(e)