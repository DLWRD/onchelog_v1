import cloudscraper
import pandas as pd
import time
import os
import math
from datetime import datetime

CSV_FILE = 'user_log.csv'
URL = 'https://onche.org/user/logged'
AUTH_COOKIE = os.environ.get('AUTH_COOKIE', '')
SESS_COOKIE = os.environ.get('SESS_COOKIE', '')

scraper = cloudscraper.create_scraper()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "application/json",
    "Referer": "https://onche.org/",
    "Cookie": f"{AUTH_COOKIE}; {SESS_COOKIE}"
    }

def fetch_usernames():
    try:
        response = scraper.get(URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return [user['username'] for user in data if 'username' in user]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def update_csv(usernames):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, index_col=0)
    else:
        df = pd.DataFrame()

    # Add new users as columns
    for user in usernames:
        if user not in df.columns:
            df[user] = 0

    # Prepare row data
    row_data = {user: (1 if user in usernames else 0) for user in df.columns if user != "Total_Online"}
    total_online = sum(row_data.values())
    row_data = {"Total_Online": total_online, **row_data}

    new_row = pd.DataFrame([row_data], index=[now])

    # Ensure Total_Online column exists and is first
    if "Total_Online" not in df.columns:
        df["Total_Online"] = 0

    df = pd.concat([df, new_row])

    # Reorder columns to make sure Total_Online is first
    cols = df.columns.tolist()
    if "Total_Online" in cols:
        cols = ["Total_Online"] + [c for c in cols if c != "Total_Online"]
    df = df[cols]

    df.to_csv(CSV_FILE)
    print(f"[{now}] Updated CSV with {len(usernames)} users.")

def main():
    """Run once for GitHub Actions"""
    usernames = fetch_usernames()
    if usernames:
        update_csv(usernames)
        print(f"Successfully logged {len(usernames)} users.")
    else:
        print("No users fetched.")

if __name__ == '__main__':
    main()
