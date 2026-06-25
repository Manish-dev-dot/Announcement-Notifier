import requests

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "5616178137"

msg = "✅ SRM Announcement Bot is working!"

url = f"https://api.telegram.org/bot8791391872:AAE2necTmLzLAYGF5Ke0592x7wQq4lBA7b0/sendMessage"

requests.get(
    url,
    params={
        "chat_id": CHAT_ID,
        "text": msg
    }
)

print("Message sent")