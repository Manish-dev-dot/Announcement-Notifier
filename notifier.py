import json
import os
import requests
from bs4 import BeautifulSoup

URL = "https://srmuniversity.ac.in/examination-announcements/"
DB_FILE = "seen.json"

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def send_telegram(message):
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=20,
    )
    response.raise_for_status()


def get_announcements():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    tbody = soup.find("tbody")

    if tbody is None:
        raise RuntimeError("Couldn't locate announcement table.")

    announcements = []

    for row in tbody.find_all("tr"):

        cols = row.find_all("td")

        if len(cols) < 2:
            continue

        date = cols[0].get_text(strip=True)

        link = cols[1].find("a")

        if not link:
            continue

        announcements.append(
            {
                "date": date,
                "title": link.get_text(strip=True),
                "link": link.get("href", ""),
            }
        )

    return announcements


def load_seen():
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(seen):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2)


def main():

    announcements = get_announcements()

    seen = load_seen()

    # Use (date, title, link) as the unique identifier
    seen_keys = {
        (item["date"], item["title"], item["link"])
        for item in seen
    }

    if not seen:

        print("First run.")

        latest_date = announcements[0]["date"] if announcements else ""

        todays = [
            x
            for x in announcements
            if x["date"] == latest_date
        ]

        if todays:

            msg = "📢 SRM Announcements Posted Today\n\n"

            for item in todays:

                msg += (
                    f"📅 {item['date']}\n"
                    f"{item['title']}\n"
                    f"{item['link']}\n\n"
                )

            send_telegram(msg)

        save_seen(announcements)

        print("Saved current announcements.")

        return

    new_items = []

    for item in announcements:

        key = (item["date"], item["title"], item["link"])

        if key not in seen_keys:
            new_items.append(item)

    if not new_items:

        print("No new announcements.")

        return

    print(f"Found {len(new_items)} new announcement(s).")

    for item in reversed(new_items):

        send_telegram(
            "🚨 NEW SRM ANNOUNCEMENT\n\n"
            f"📅 {item['date']}\n\n"
            f"{item['title']}\n\n"
            f"{item['link']}"
        )

    save_seen(announcements)

    print("seen.json updated.")


if __name__ == "__main__":
    main()