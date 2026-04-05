import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

data = json.load(open('backtest_results_2023_2026.json'))

quarters = [d['quarter'] for d in data]
base_pnl = [d['pnl_severity'] for d in data]
active_pnl = [d['pnl_active_risk'] for d in data]
like_pnl = [d['pnl_likelihood_weighted'] for d in data]

# Cumulative equity curves (starting at 1.0 = 100%)
cum_base = [1.0]
cum_active = [1.0]
cum_like = [1.0]
for i in range(len(data)):
    cum_base.append(cum_base[-1] * (1 + base_pnl[i]))
    cum_active.append(cum_active[-1] * (1 + active_pnl[i]))
    cum_like.append(cum_like[-1] * (1 + like_pnl[i]))

x_labels = ['Start'] + quarters

# --- Chart 1: Equity Curves ---
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

ax.plot(x_labels, cum_active, color='#00ff88', linewidth=2.5, marker='o', markersize=6, label='Active Risk (TP/SL)')
ax.plot(x_labels, cum_base, color='#ff4444', linewidth=2, marker='s', markersize=5, label='Base (Severity-Weighted Hold)', alpha=0.8)
ax.plot(x_labels, cum_like, color='#ffaa00', linewidth=1.5, marker='^', markersize=5, label='Likelihood-Weighted', alpha=0.7, linestyle='--')

ax.axhline(y=1.0, color='white', linestyle=':', alpha=0.3, linewidth=1)
ax.fill_between(x_labels, cum_active, 1.0, alpha=0.15, color='#00ff88')

ax.set_title('Agentic Macro Strategy: Equity Curves (2023-Q1 to 2026-Q1)', fontsize=16, color='white', fontweight='bold', pad=15)
ax.set_ylabel('Portfolio Value (Starting = 1.0)', fontsize=12, color='white')
ax.set_xlabel('Quarter', fontsize=12, color='white')
ax.tick_params(axis='x', rotation=45, colors='white', labelsize=9)
ax.tick_params(axis='y', colors='white')
ax.legend(loc='upper left', fontsize=10, facecolor='#16213e', edgecolor='#444', labelcolor='white')
ax.grid(axis='y', alpha=0.2, color='white')

for spine in ax.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('equity_curves.png', dpi=150, facecolor='#1a1a2e')
print("Saved equity_curves.png")

# --- Chart 2: Quarterly PnL Bars ---
fig2, ax2 = plt.subplots(figsize=(14, 6))
fig2.patch.set_facecolor('#1a1a2e')
ax2.set_facecolor('#16213e')

x = np.arange(len(quarters))
width = 0.35

bars_base = ax2.bar(x - width/2, [p*100 for p in base_pnl], width, label='Base (Hold)', color='#ff4444', alpha=0.7)
bars_active = ax2.bar(x + width/2, [p*100 for p in active_pnl], width, label='Active (TP/SL)', color='#00ff88', alpha=0.9)

ax2.axhline(y=0, color='white', linewidth=0.5)
ax2.set_title('Quarterly PnL Comparison: Base Hold vs Active Risk Management', fontsize=14, color='white', fontweight='bold', pad=15)
ax2.set_ylabel('PnL (%)', fontsize=12, color='white')
ax2.set_xticks(x)
ax2.set_xticklabels(quarters, rotation=45, fontsize=9, color='white')
ax2.tick_params(axis='y', colors='white')
ax2.legend(fontsize=10, facecolor='#16213e', edgecolor='#444', labelcolor='white')
ax2.grid(axis='y', alpha=0.2, color='white')

for spine in ax2.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('quarterly_pnl.png', dpi=150, facecolor='#1a1a2e')
print("Saved quarterly_pnl.png")
