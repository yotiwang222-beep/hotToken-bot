import requests
from flask import Flask, request
import threading

app = Flask(__name__)

BOT_TOKEN = "8155888633:AAECW2-c4gUTwMF5gWCi-KVxQTgzi1s6DBM"
CHANNEL_ID = "-1003224080782"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

def monitor():
    while True:
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana,base,sui")
            for p in r.json().get("pairs", []):
                vol = p.get("volume", {}).get("h24", 0)
                change = p.get("priceChange", {}).get("h24", 0)
                if vol > 500000 and change > 30:
                    symbol = p["baseToken"]["symbol"]
                    link = f"https://dexscreener.com/{p['chainId']}/{p['pairAddress']}"
                    msg = f"Up *{symbol}* | +{change:.1f}% | ${vol:,.0f}\n<a href='{link}'>Chart</a>"
                    send(msg)
        except: pass
        time.sleep(60)

# 启动监控线程
threading.Thread(target=monitor, daemon=True).start()

@app.route('/')
def home():
    return "Bot 运行中..."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)