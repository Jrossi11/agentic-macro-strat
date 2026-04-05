import json

data = json.load(open('backtest_results_2023_2026.json'))
for d in data:
    q = d['quarter']
    base = d['pnl_severity']
    active = d['pnl_active_risk']
    like = d['pnl_likelihood_weighted']
    n = len(d['signals'])
    print(f"{q}: Base={base:.4f}, Active={active:.4f}, Likelihood={like:.4f}, Signals={n}")

# Cumulative
cum_base = 0
cum_active = 0
cum_like = 0
print("\n--- Cumulative ---")
for d in data:
    cum_base += d['pnl_severity']
    cum_active += d['pnl_active_risk']
    cum_like += d['pnl_likelihood_weighted']
    print(f"{d['quarter']}: CumBase={cum_base:.4f}, CumActive={cum_active:.4f}, CumLike={cum_like:.4f}")
