def monitor():
    send("Bot 重启成功！正在监控 5 链...")  # 测试推送
    while True:
        try:
            # 防限流：加随机延迟 + 请求头
            time.sleep(35)  # ← 每 35 秒请求一次（< 30 次/分钟）
            headers = {"User-Agent": "HotTokenBot/1.0"}
            r = requests.get(
                "https://api.dexscreener.com/latest/dex/pairs/solana,base,sui,bsc,ethereum",
                headers=headers,
                timeout=10
            )
            
            if r.status_code == 429:  # 被限流
                print("API 限流，等待 60 秒...")
                time.sleep(60)
                continue
                
            data = r.json().get("pairs", [])
            print(f"扫描到 {len(data)} 个交易对")  # ← 日志滚动证明
            
            for p in data:
                vol = p.get("volume", {}).get("h1", 0)
                change = p.get("priceChange", {}).get("h1", 0)
                if vol > 100000 and change > 50:
                    symbol = p["baseToken"]["symbol"]
                    link = f"https://dexscreener.com/{p['chainId']}/{p['pairAddress']}"
                    msg = f"1h *{symbol}* | +{change:.1f}% | ${vol:,.0f}\n<a href='{link}'>Chart</a>"
                    send(msg)
                    print("推送:", symbol)
                    
        except requests.exceptions.RequestException as e:
            print("网络错误:", e)
            time.sleep(60)
        except Exception as e:
            print("未知错误:", e)
            time.sleep(30)
