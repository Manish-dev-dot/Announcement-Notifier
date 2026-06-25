import requests
from bs4 import BeautifulSoup
import json
import time

TOKEN = "8791391872:AAE2necTmLzLAYGF5Ke0592x7wQq4lBA7b0"
CHAT_ID = "5616178137"

URL = "https://srmuniversity.ac.in/examination-announcements/"
DB_FILE = "srm_seen.json"


def send_telegram(message):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )


def get_announcements():
    html = requests.get(URL, timeout=30).text

    soup = BeautifulSoup(html, "html.parser")

    tbody = soup.find("tbody")

    if not tbody:
        return []

    announcements = []

    for row in tbody.find_all("tr"):

        cols = row.find_all("td")

        if len(cols) < 2:
            continue

        date = cols[0].get_text(strip=True)

        a = cols[1].find("a")

        if not a:
            continue

        announcements.append({
            "date": date,
            "title": a.get_text(strip=True),
            "link": a.get("href", "")
        })

    return announcements


announcements = get_announcements()

try:

    with open(DB_FILE, "r", encoding="utf-8") as f:
        seen = set(json.load(f))

except FileNotFoundError:

    print("First run detected")

    # Get the most recent date appearing on the site
    today_date = announcements[0]["date"] if announcements else ""

    todays_posts = [
        x for x in announcements
        if x["date"] == today_date
    ]

    if todays_posts:

        msg = "📢 SRM Announcements Posted Today\n\n"

        for item in todays_posts:

            msg += (
                f"📅 {item['date']}\n"
                f"{item['title']}\n"
                f"{item['link']}\n\n"
            )

        send_telegram(msg)

    seen = set(item["title"] for item in announcements)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)

    print("Initialization complete")


while True:

    try:

        announcements = get_announcements()

        for item in reversed(announcements):

            title = item["title"]

            if title not in seen:

                send_telegram(
                    "🚨 NEW SRM ANNOUNCEMENT\n\n"
                    f"📅 {item['date']}\n\n"
                    f"{item['title']}\n\n"
                    f"{item['link']}"
                )

                print("New announcement:", title)

                seen.add(title)

                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(seen), f)

        time.sleep(60)

    except Exception as e:

        print("Error:", e)

        time.sleep(60)