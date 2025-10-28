import requests
import time          # ← 必须在最上面！
import os
from flask import Flask
import threading

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 先定义 send
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print("发送失败:", e)

# 再定义 monitor
def monitor():
    send("Bot 强制重启！正在监控 5 链...")
    while True:
        try:
            time.sleep(35)
            headers = {"User-Agent": "HotTokenBot/1.0"}
            r = requests.get(
                "https://api.dexscreener.com/latest/dex/pairs/solana,base,sui,bsc,ethereum",
                headers=headers,
                timeout=10
            )
            if r.status_code == 429:
                print("API 限流，等待 60 秒...")
                time.sleep(60)
                continue
            data = r.json().get("pairs", [])
            print(f"扫描到 {len(data)} 个交易对")
            for p in data:
                vol = p.get("volume", {}).get("h1", 0)
                change = p.get("priceChange", {}).get("h1", 0)
                if vol > 100000 and change > 50:
                    symbol = p["baseToken"]["symbol"]
                    link = f"https://dexscreener.com/{p['chainId']}/{p['pairAddress']}"
                    msg = f"1h *{symbol}* | +{change:.1f}% | ${vol:,.0f}\n<a href='{link}'>Chart</a>"
                    send(msg)
                    print("推送:", symbol)
        except Exception as e:
            print("监控错误:", e)
            time.sleep(30)

threading.Thread(target=monitor, daemon=True).start()

@app.route('/')
def home():
    return "Bot 运行中..."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
