import json

data = json.load(open('backtest_results_2023_2026.json'))

total = 0
ok = 0
intra = 0
future = 0

for d in data:
    q = d['quarter']
    year = int(q.split('-')[0])
    qn = int(q.split('Q')[1])
    if qn == 1: entry = f"{year}-01-01"; exit_d = f"{year}-03-31"
    elif qn == 2: entry = f"{year}-04-01"; exit_d = f"{year}-06-30"
    elif qn == 3: entry = f"{year}-07-01"; exit_d = f"{year}-09-30"
    else: entry = f"{year}-10-01"; exit_d = f"{year}-12-31"
    
    for s in d.get('signals', []):
        for c in s.get('catalysts', []):
            total += 1
            det = c.get('date_detected', '')
            if not det or det <= entry:
                ok += 1
                status = "OK"
            elif det <= exit_d:
                intra += 1
                status = "INTRA-Q"
            else:
                future += 1
                status = "FUTURE"
            print(f"{q} | {s['commodity']:12} | det={det:10} | entry={entry} | {status} | {c['description'][:60]}")

print(f"\nTOTAL={total} OK={ok} INTRA={intra} FUTURE={future} BIAS_RATE={(intra+future)/max(total,1)*100:.1f}%")
