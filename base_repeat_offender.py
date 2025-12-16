import requests, time

def repeat_offender():
    print("Base — Repeat Offender Tracker (dev wallets with 5+ launches & high rug rate)")
    offenders = {}  # wallet → (launches, rugs)

    while True:
        try:
            r = requests.get("https://api.dexscreener.com/latest/dex/pairs/base")
            for pair in r.json().get("pairs", []):
                age = time.time() - pair.get("pairCreatedAt", 0) / 1000
                if age > 3600: continue  # only recent

                tx_hash = pair.get("pairCreatedTxHash")
                if not tx_hash: continue

                tx = requests.get(f"https://api.basescan.org/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}").json()
                dev = tx["result"]["from"].lower()

                if dev not in offenders:
                    offenders[dev] = [0, 0]

                offenders[dev][0] += 1  # new launch

                # Rough rug check: low liq or high sell tax
                if pair["liquidity"]["usd"] < 5000 or pair.get("sellTax", 0) > 20:
                    offenders[dev][1] += 1

                launches, rugs = offenders[dev]
                if launches >= 5 and rugs / launches > 0.6:
                    token = pair["baseToken"]["symbol"]
                    print(f"REPEAT OFFENDER ALERT\n"
                          f"Wallet {dev[:10]}... launched {launches} tokens\n"
                          f"Rug rate: {rugs/launches:.0%}\n"
                          f"Latest: {token}\n"
                          f"https://dexscreener.com/base/{pair['pairAddress']}\n"
                          f"https://basescan.org/address/{dev}\n"
                          f"→ Serial rugger active — avoid or short\n"
                          f"{'REPEAT RUG'*15}")
                    del offenders[dev]  # reset after alert

        except:
            pass
        time.sleep(9.2)

if __name__ == "__main__":
    repeat_offender()
