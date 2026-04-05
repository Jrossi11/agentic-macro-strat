import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd
import yfinance as yf

# ─── Page Config ───
st.set_page_config(
    page_title="Agentic Macro Strategy",
    page_icon="🏹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0d1117; }
    
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-label {
        color: #8b949e;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .green { color: #3fb950; }
    .red { color: #f85149; }
    .gold { color: #d29922; }
    .blue { color: #58a6ff; }
    
    .agent-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .agent-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .catalyst-chip {
        display: inline-block;
        background: #1c2333;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 4px 10px;
        margin: 3px;
        font-size: 0.8rem;
    }
    .severity-high { border-left: 3px solid #f85149; }
    .severity-med { border-left: 3px solid #d29922; }
    .severity-low { border-left: 3px solid #3fb950; }
    
    .trade-row {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 8px;
    }
    
    h1, h2, h3 { color: #e6edf3 !important; }
    p, li { color: #c9d1d9; }
    
    .pipeline-container {
        display: flex;
        align-items: stretch;
        gap: 0;
        margin: 20px 0;
        overflow-x: auto;
    }
    .pipeline-node {
        flex: 1;
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px 14px;
        position: relative;
        min-width: 180px;
        transition: all 0.3s ease;
    }
    .pipeline-node:hover {
        border-color: #58a6ff;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(88, 166, 255, 0.15);
    }
    .pipeline-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        color: #30363d;
        min-width: 36px;
        padding-top: 10px;
    }
    .node-icon {
        font-size: 1.8rem;
        margin-bottom: 6px;
    }
    .node-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e6edf3;
        margin-bottom: 4px;
    }
    .node-desc {
        font-size: 0.75rem;
        color: #8b949e;
        line-height: 1.4;
    }
    .node-output {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #30363d;
        font-size: 0.72rem;
        color: #58a6ff;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───
@st.cache_data
def load_results():
    with open("backtest_results_2023_2026.json", "r") as f:
        return json.load(f)

data = load_results()
quarters = [d["quarter"] for d in data]

# ─── Sidebar ───
with st.sidebar:
    st.markdown("# 🏹 Agentic Macro")
    st.markdown("##### Supply & Demand Shock Detector")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Performance Overview", "🔍 Agent Drill-Down", "📋 Trade Journal"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("#### System Architecture")
    st.markdown("""
    ```
    Scout (Tavily)
      ↓ Raw News
    Macro Scout (EIA/USGS)
      ↓ Balance Score
    Analyst (Gemini)
      ↓ Catalysts (Filtered)
    Quant (Gemini + ATR)
      ↓ Signals + TP/SL
    ```
    """)
    st.markdown("---")
    st.caption("13 Quarters | 5 Commodities | 33 Catalysts")


# ═══════════════════════════════════
# PAGE 1: PERFORMANCE OVERVIEW
# ═══════════════════════════════════
if page == "📊 Performance Overview":
    st.markdown("# 📊 Performance Overview")
    st.markdown("##### Agentic Macro Strategy — Clean Backtest (2023-Q1 to 2026-Q1)")
    
    # ── Headline Metrics ──
    cum_base = sum(d["pnl_severity"] for d in data)
    cum_active = sum(d["pnl_active_risk"] for d in data)
    cum_like = sum(d["pnl_likelihood_weighted"] for d in data)
    win_base = sum(1 for d in data if d["pnl_severity"] > 0)
    win_active = sum(1 for d in data if d["pnl_active_risk"] > 0)
    total_signals = sum(len(d["signals"]) for d in data)
    
    # --- Fetch Benchmark Data ---
    @st.cache_data
    def get_benchmarks(quarters):
        bench_data = {"SPY": [], "GSG": []}
        for q in quarters:
            year = int(q.split("-")[0])
            qn = int(q.split("Q")[1])
            q_start = f"{year}-{(qn-1)*3+1:02d}-01"
            # Approx 3 months later
            if qn == 4:
                q_end = f"{year+1}-01-01"
            else:
                q_end = f"{year}-{qn*3+1:02d}-01"
                
            # SPY
            spy = yf.download("SPY", start=q_start, end=q_end, progress=False)
            if not spy.empty:
                col = 'Close' if 'Close' in spy.columns else spy.columns[0]
                # Handle MultiIndex
                if isinstance(spy.columns, pd.MultiIndex):
                    p = spy[col]["SPY"]
                else:
                    p = spy[col]
                perf = (float(p.iloc[-1]) - float(p.iloc[0])) / float(p.iloc[0])
                bench_data["SPY"].append(perf)
            else:
                bench_data["SPY"].append(0.0)
                
            # GSG (Commodity Index)
            gsg = yf.download("GSG", start=q_start, end=q_end, progress=False)
            if not gsg.empty:
                col = 'Close' if 'Close' in gsg.columns else gsg.columns[0]
                if isinstance(gsg.columns, pd.MultiIndex):
                    p = gsg[col]["GSG"]
                else:
                    p = gsg[col]
                perf = (float(p.iloc[-1]) - float(p.iloc[0])) / float(p.iloc[0])
                bench_data["GSG"].append(perf)
            else:
                bench_data["GSG"].append(0.0)
        return bench_data

    benchmarks = get_benchmarks(quarters)
    cum_spy = sum(benchmarks["SPY"])
    cum_gsg = sum(benchmarks["GSG"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "green" if cum_base > 0 else "red"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Base (Hold) Return</div>
            <div class="metric-value {color}">{cum_base:+.1%}</div>
            <div class="metric-label">{win_base}/13 Win Rate</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        color = "green" if cum_active > 0 else "red"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Trailing Stop Return</div>
            <div class="metric-value {color}">{cum_active:+.1%}</div>
            <div class="metric-label">{win_active}/13 Win Rate</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        color = "green" if cum_spy > 0 else "red"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">S&P 500 (SPY)</div>
            <div class="metric-value {color}">{cum_spy:+.1%}</div>
            <div class="metric-label">Equity Benchmark</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        color = "green" if cum_gsg > 0 else "red"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Commodity (GSG)</div>
            <div class="metric-value {color}">{cum_gsg:+.1%}</div>
            <div class="metric-label">Index Benchmark</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Equity Curve ──
    cum_b = [1.0]
    cum_a = [1.0]
    cum_l = [1.0]
    cum_s = [1.0]
    cum_g = [1.0]
    
    for i, d in enumerate(data):
        cum_b.append(cum_b[-1] * (1 + d["pnl_severity"]))
        cum_a.append(cum_a[-1] * (1 + d["pnl_active_risk"]))
        cum_l.append(cum_l[-1] * (1 + d["pnl_likelihood_weighted"]))
        cum_s.append(cum_s[-1] * (1 + benchmarks["SPY"][i]))
        cum_g.append(cum_g[-1] * (1 + benchmarks["GSG"][i]))
    
    x_labels = ["Start"] + quarters
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_labels, y=cum_a, mode='lines+markers',
        name='Active (Trailing SL)', line=dict(color='#3fb950', width=3),
        marker=dict(size=7), fill='tozeroy',
        fillcolor='rgba(63,185,80,0.08)'
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=cum_b, mode='lines+markers',
        name='Base (Hold)', line=dict(color='#f85149', width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=cum_s, mode='lines',
        name='S&P 500 (SPY)', line=dict(color='#58a6ff', width=1.5, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=cum_g, mode='lines',
        name='Commodity (GSG)', line=dict(color='#d29922', width=1.5, dash='dot')
    ))
    fig.add_hline(y=1.0, line_dash="dot", line_color="#30363d", annotation_text="Break-Even")
    fig.update_layout(
        title="Cumulative Equity Curve",
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(family="Inter", color="#c9d1d9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ── Quarterly Bar Chart ──
    base_pnl = [d["pnl_severity"] * 100 for d in data]
    active_pnl = [d["pnl_active_risk"] * 100 for d in data]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=quarters, y=base_pnl, name='Base (Hold)',
        marker_color=['#3fb950' if v >= 0 else '#f85149' for v in base_pnl],
        opacity=0.5
    ))
    fig2.add_trace(go.Bar(
        x=quarters, y=active_pnl, name='Active (Trailing SL)',
        marker_color=['#3fb950' if v >= 0 else '#f85149' for v in active_pnl],
        opacity=0.9
    ))
    fig2.update_layout(
        title="Quarterly PnL Comparison (%)",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(family="Inter", color="#c9d1d9"),
        height=380,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    fig2.add_hline(y=0, line_color="#30363d")
    st.plotly_chart(fig2, use_container_width=True)
    
    # ── Agent Workflow Pipeline ──
    st.markdown("---")
    st.markdown("### Agent Pipeline Architecture")
    st.markdown("""<div class="pipeline-container">
        <div class="pipeline-node">
            <div class="node-icon">🔎</div>
            <div class="node-title">Scout Agent</div>
            <div class="node-desc">Searches Tavily for commodity supply/demand shocks within the target quarter's date range.</div>
            <div class="node-output">OUTPUT: Raw article text (10 per commodity)</div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">🌍</div>
            <div class="node-title">Macro Scout</div>
            <div class="node-desc">Queries EIA, USGS, IEA for structural supply/demand balance. Scores market as Deficit (+1) or Surplus (-1).</div>
            <div class="node-output">OUTPUT: Market balance score per commodity</div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">📊</div>
            <div class="node-title">Analyst Agent</div>
            <div class="node-desc">Extracts structured catalysts via Gemini. Applies <strong style="color:#f85149;">temporal filter</strong> — rejects articles published after the quarter.</div>
            <div class="node-output">OUTPUT: Validated Catalyst objects with severity, dates, impact</div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">🧠</div>
            <div class="node-title">Quant Agent</div>
            <div class="node-desc">Analyzes price action (MAs, ATR, 20-day range) against catalysts. Detects if move is priced in. Sets trailing SL at 2x ATR.</div>
            <div class="node-output">OUTPUT: LONG/SHORT signals with trailing stop + asymmetry score</div>
        </div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-node">
            <div class="node-icon">💰</div>
            <div class="node-title">Execution</div>
            <div class="node-desc">Entry at <strong>max(Q start, catalyst date)</strong>. Trailing stop ratchets up with winners. Hold to quarter end if no stop hit.</div>
            <div class="node-output">OUTPUT: Realized PnL per position</div>
        </div>
    </div>""", unsafe_allow_html=True)
    
    # ── Data flow stats ──
    st.markdown("")
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    fc1.markdown("""<div class="metric-card"><div class="metric-label">Searches</div><div class="metric-value blue">130</div><div class="metric-label">Tavily Queries Cached</div></div>""", unsafe_allow_html=True)
    
    total_cats = sum(len(c) for d in data for s in d.get('signals', []) for c in [s.get('catalysts', [])])
    fc2.markdown(f'<div class="metric-card"><div class="metric-label">Catalysts</div><div class="metric-value gold">{total_cats}</div><div class="metric-label">After Temporal Filter</div></div>', unsafe_allow_html=True)
    
    fc3.markdown(f'<div class="metric-card"><div class="metric-label">Signals</div><div class="metric-value green">{total_signals}</div><div class="metric-label">Trade Decisions</div></div>', unsafe_allow_html=True)
    
    long_count = sum(1 for d in data for s in d.get('signals', []) if s['direction'] == 'LONG')
    short_count = sum(1 for d in data for s in d.get('signals', []) if s['direction'] == 'SHORT')
    fc4.markdown(f'<div class="metric-card"><div class="metric-label">Long / Short</div><div class="metric-value blue">{long_count} / {short_count}</div><div class="metric-label">Directional Split</div></div>', unsafe_allow_html=True)
    
    avg_sev = sum(c.get('severity', 0) for d in data for s in d.get('signals', []) for c in s.get('catalysts', [])) / max(total_cats, 1)
    fc5.markdown(f'<div class="metric-card"><div class="metric-label">Avg Severity</div><div class="metric-value gold">{avg_sev:.1f}/10</div><div class="metric-label">Catalyst Quality</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════
# PAGE 2: AGENT DRILL-DOWN
# ═══════════════════════════════════
elif page == "🔍 Agent Drill-Down":
    st.markdown("# 🔍 Agent Reasoning Drill-Down")
    
    selected_q = st.selectbox("Select Quarter", quarters, index=0)
    q_data = next(d for d in data if d["quarter"] == selected_q)
    
    signals = q_data.get("signals", [])
    
    # ── Summary Row ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Signals Generated", len(signals))
    c2.metric("Base PnL", f"{q_data['pnl_severity']:.2%}")
    c3.metric("Active PnL", f"{q_data['pnl_active_risk']:.2%}")
    c4.metric("Likelihood PnL", f"{q_data['pnl_likelihood_weighted']:.2%}")
    
    if not signals:
        st.warning("No signals were generated for this quarter. All catalysts may have been filtered by temporal validation.")
    
    for i, sig in enumerate(signals):
        st.markdown("---")
        
        # ── Signal Header ──
        direction_emoji = "🟢" if sig["direction"] == "LONG" else "🔴"
        priced_in = "⚠️ Priced In" if sig.get("is_priced_in") else "✅ Not Priced In"
        
        st.markdown(f"### {direction_emoji} {sig['commodity']} — {sig['direction']}")
        
        # ── Three-Column Layout ──
        col_tech, col_trade, col_reason = st.columns(3)
        
        with col_tech:
            st.markdown(f"""<div class="agent-card">
                <div class="agent-header">📡 Technical Context</div>
                <p style="font-size: 0.85rem;">{sig.get('technical_context', 'N/A')}</p>
            </div>""", unsafe_allow_html=True)
        
        with col_trade:
            tp = sig.get("take_profit", 0)
            sl = sig.get("stop_loss", 0)
            asym = sig.get("asymmetry_ratio", 0)
            
            st.markdown(f"""<div class="agent-card">
                <div class="agent-header">🎯 Trade Parameters</div>
                <table style="width:100%; font-size: 0.85rem; color: #c9d1d9;">
                    <tr><td>Take Profit</td><td style="text-align:right; color:#3fb950; font-weight:600;">${tp:.2f}</td></tr>
                    <tr><td>Stop Loss</td><td style="text-align:right; color:#f85149; font-weight:600;">${sl:.2f}</td></tr>
                    <tr><td>Asymmetry Ratio</td><td style="text-align:right; color:#58a6ff; font-weight:600;">{asym:.2f}x</td></tr>
                    <tr><td>Upside</td><td style="text-align:right;">{sig.get('upside_potential', 0):.2%}</td></tr>
                    <tr><td>Downside</td><td style="text-align:right;">{sig.get('downside_risk', 0):.2%}</td></tr>
                    <tr><td>Weight (Sev)</td><td style="text-align:right;">{sig.get('weight_severity', 0):.1%}</td></tr>
                    <tr><td>Status</td><td style="text-align:right;">{priced_in}</td></tr>
                </table>
            </div>""", unsafe_allow_html=True)
        
        with col_reason:
            st.markdown(f"""<div class="agent-card">
                <div class="agent-header">🧠 Quant Rationale</div>
                <p style="font-size: 0.85rem;">{sig.get('rationale', 'N/A')}</p>
            </div>""", unsafe_allow_html=True)
        
        # ── Catalysts (Analyst Output) ──
        st.markdown("**📋 Analyst Catalysts:**")
        for cat in sig.get("catalysts", []):
            sev = cat.get("severity", 0)
            sev_class = "severity-high" if sev >= 7 else "severity-med" if sev >= 4 else "severity-low"
            pub_date = cat.get("source_publish_date", "N/A")
            
            st.markdown(f"""<div class="agent-card {sev_class}">
                <strong>{cat.get('impact_type', '')} — Severity {sev}/10</strong>
                &nbsp;|&nbsp; Likelihood: {cat.get('likelihood_ratio', 1.0):.0%}
                &nbsp;|&nbsp; Region: {cat.get('region', 'N/A')}
                &nbsp;|&nbsp; Published: <span style="color:#58a6ff">{pub_date}</span>
                <br/>
                <span style="color:#c9d1d9;">{cat.get('description', '')}</span>
                <br/>
                <span style="font-size:0.75rem; color:#8b949e;">
                    Impact: {cat.get('supply_impact_value', 'N/A')} {cat.get('supply_impact_unit', '')}
                    &nbsp;|&nbsp; Window: {cat.get('start_date', '?')} → {cat.get('end_date', '?')}
                    &nbsp;|&nbsp; <a href="{cat.get('source_url', '#')}" style="color:#58a6ff;">Source</a>
                </span>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════
# PAGE 3: TRADE JOURNAL
# ═══════════════════════════════════
elif page == "📋 Trade Journal":
    st.markdown("# 📋 Trade Journal")
    st.markdown("##### Every position taken across 13 quarters")
    
    # Build a flat table of all trades
    rows = []
    for d in data:
        q = d["quarter"]
        for sig in d.get("signals", []):
            # Compute actual entry date
            cat_dates = [c.get("date_detected", "") for c in sig.get("catalysts", []) if c.get("date_detected")]
            latest_det = max(cat_dates) if cat_dates else "?"
            
            year = int(q.split("-")[0])
            qn = int(q.split("Q")[1])
            q_start = f"{year}-{(qn-1)*3+1:02d}-01"
            actual_entry = max(q_start, latest_det) if latest_det != "?" else q_start
            
            rows.append({
                "Quarter": q,
                "Commodity": sig["commodity"],
                "Direction": sig["direction"],
                "Entry Date": actual_entry,
                "TP": sig.get("take_profit", 0),
                "SL": sig.get("stop_loss", 0),
                "Asymmetry": sig.get("asymmetry_ratio", 0),
                "Priced In?": "Yes" if sig.get("is_priced_in") else "No",
                "Weight": sig.get("weight_severity", 0),
                "Catalysts": len(sig.get("catalysts", [])),
                "Top Catalyst": sig.get("catalysts", [{}])[0].get("description", "N/A")[:60] + "..." if sig.get("catalysts") else "N/A"
            })
    
    if rows:
        df = pd.DataFrame(rows)
        
        # ── Filters ──
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            commodities_filter = st.multiselect("Filter by Commodity", df["Commodity"].unique(), default=list(df["Commodity"].unique()))
        with col_f2:
            direction_filter = st.multiselect("Filter by Direction", df["Direction"].unique(), default=list(df["Direction"].unique()))
        
        filtered = df[(df["Commodity"].isin(commodities_filter)) & (df["Direction"].isin(direction_filter))]
        
        # ── Summary Stats ──
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Trades", len(filtered))
        c2.metric("Long / Short", f"{len(filtered[filtered['Direction']=='LONG'])} / {len(filtered[filtered['Direction']=='SHORT'])}")
        c3.metric("Avg Asymmetry", f"{filtered['Asymmetry'].mean():.2f}x")
        
        # ── Commodity Distribution ──
        fig_dist = px.histogram(
            filtered, x="Commodity", color="Direction",
            color_discrete_map={"LONG": "#3fb950", "SHORT": "#f85149"},
            title="Trade Distribution by Commodity"
        )
        fig_dist.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            font=dict(family="Inter", color="#c9d1d9"),
            height=300,
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # ── Trade Table ──
        st.markdown("### Full Trade Log")
        st.dataframe(
            filtered.style.map(
                lambda v: "color: #3fb950" if v == "LONG" else "color: #f85149" if v == "SHORT" else "",
                subset=["Direction"]
            ),
            use_container_width=True,
            height=500
        )
        
        # ── Expandable Detail ──
        st.markdown("### Trade Details")
        for _, row in filtered.iterrows():
            with st.expander(f"{row['Quarter']} | {row['Direction']} {row['Commodity']} | Entry: {row['Entry Date']}"):
                q_data = next(d for d in data if d["quarter"] == row["Quarter"])
                sig = next((s for s in q_data["signals"] if s["commodity"] == row["Commodity"]), None)
                if sig:
                    st.markdown(f"**Rationale:** {sig.get('rationale', 'N/A')}")
                    st.markdown(f"**Technical:** {sig.get('technical_context', 'N/A')}")
                    st.markdown(f"**TP:** ${sig.get('take_profit', 0):.2f} | **SL:** ${sig.get('stop_loss', 0):.2f} | **Asymmetry:** {sig.get('asymmetry_ratio', 0):.2f}x")
                    
                    for cat in sig.get("catalysts", []):
                        st.info(f"**{cat.get('impact_type', '')}** (Sev: {cat.get('severity', 0)}/10) — {cat.get('description', '')}")
    else:
        st.warning("No trades found in the backtest results.")
