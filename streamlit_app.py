# FMCG PULSE - Supply Chain Control Tower
# Full Streamlit in Snowflake application reconstructed from the code supplied in chat.
# Fix applied: Plotly show() does not pass title=None and gauge() does not pass delta=None,
# preventing the literal 'undefined' label above gauge charts.

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="FMCG Pulse", page_icon="📦", layout="wide")
session = get_active_session()

G, S = "FMCG_DB.GOLD", "FMCG_DB.SILVER"
BLUE, NAVY, GREEN, AMBER, RED, PURPLE = "#29B5E8", "#1478A8", "#30A46C", "#F5A524", "#E5484D", "#8E7CF0"
BANDS = ["HIGH", "MEDIUM", "LOW"]
BAND_COLORS = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN}
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SEQ = [BLUE, PURPLE, AMBER, GREEN, RED, "#5BC0EB", "#C084FC"]
HAS_PILLS = hasattr(st, "pills")
HAS_SEG = hasattr(st, "segmented_control")
HAS_TOGGLE = hasattr(st, "toggle")

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
.hero {padding: 22px 26px; border-radius: 18px; margin-bottom: 16px;
  background: linear-gradient(115deg, #0B1F33 0%, #0B3C5D 45%, #29B5E8 100%);
  box-shadow: 0 8px 30px rgba(41,181,232,.25);}
.hero h1 {color: #fff; margin: 0; font-size: 2rem;}
.hero p {color: #DDF3FC; margin: 8px 0 0 0;}
.chip {display: inline-block; background: rgba(255,255,255,.16); color: #fff;
  border-radius: 20px; padding: 3px 11px; margin: 2px 6px 2px 0; font-size: .8rem;}
.kpi {border-radius: 16px; padding: 14px 16px; height: 108px;
  background: linear-gradient(145deg, rgba(41,181,232,.16), rgba(20,120,168,.05));
  border: 1px solid rgba(41,181,232,.35);}
.kpi .lbl {font-size: .78rem; color: #9FB3C8; text-transform: uppercase; letter-spacing: .6px;}
.kpi .val {font-size: 1.7rem; font-weight: 800; color: #fff; margin-top: 4px;}
.kpi .sub {font-size: .8rem; margin-top: 2px;}
.up {color: #30A46C;} .down {color: #E5484D;} .flat {color: #9FB3C8;}
.insight {border-left: 4px solid #29B5E8; padding: 10px 14px; margin: 6px 0;
  background: rgba(41,181,232,.08); border-radius: 10px;}
.section {font-weight: 700; font-size: 1.05rem; margin: 14px 0 4px 0;}
button[data-baseweb="tab"] {font-size: 1rem;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #0B1F33 0%, #0B3C5D 60%, #0E4A70 100%); border-right: 1px solid rgba(41,181,232,.25);}
section[data-testid="stSidebar"] * {color: #E6F6FD;}
section[data-testid="stSidebar"] label {font-weight: 600; font-size: .85rem; letter-spacing: .3px;}
.sb-brand {text-align: center; padding: 18px 10px 14px 10px; margin-bottom: 10px; border-radius: 16px; background: rgba(255,255,255,.06); border: 1px solid rgba(41,181,232,.35);}
.sb-logo {font-size: 2.4rem; line-height: 1;}
.sb-title {font-size: 1.35rem; font-weight: 800; margin-top: 6px; background: linear-gradient(90deg,#29B5E8,#8E7CF0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.sb-sub {font-size: .75rem; color: #9FB3C8 !important;}
.sb-status {display: flex; align-items: center; gap: 8px; padding: 9px 12px; margin: 8px 0 14px 0; border-radius: 12px; background: rgba(48,164,108,.12); border: 1px solid rgba(48,164,108,.45); font-size: .8rem;}
.sb-dot {width: 9px; height: 9px; border-radius: 50%; background: #30A46C; box-shadow: 0 0 0 0 rgba(48,164,108,.7); animation: pulse 1.8s infinite;}
.sb-dot.off {background: #F5A524; animation: none;}
@keyframes pulse {0% {box-shadow: 0 0 0 0 rgba(48,164,108,.7);} 70% {box-shadow: 0 0 0 8px rgba(48,164,108,0);} 100% {box-shadow: 0 0 0 0 rgba(48,164,108,0);}}
.sb-head {font-size: .72rem; text-transform: uppercase; letter-spacing: 1.2px; color: #29B5E8 !important; font-weight: 700; margin: 16px 0 4px 0; border-bottom: 1px solid rgba(41,181,232,.25); padding-bottom: 4px;}
.sb-card {border-radius: 12px; padding: 10px 12px; margin-top: 10px; background: rgba(255,255,255,.05); border: 1px dashed rgba(41,181,232,.4); font-size: .78rem;}
.sb-pill {display: inline-block; padding: 2px 9px; margin: 3px 4px 0 0; border-radius: 20px; background: rgba(41,181,232,.22); font-size: .72rem;}
.sb-count {font-size: .7rem; color: #9FB3C8 !important; margin: -4px 0 6px 2px;}
.sb-foot {text-align: center; font-size: .7rem; color: #9FB3C8 !important; margin-top: 18px;}
section[data-testid="stSidebar"] span[data-baseweb="tag"] {background: linear-gradient(90deg,#1478A8,#29B5E8) !important; border-radius: 8px !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] > div {background: rgba(255,255,255,.07) !important; border: 1px solid rgba(41,181,232,.35) !important; border-radius: 10px !important;}
section[data-testid="stSidebar"] .stButton button {width: 100%; border-radius: 10px; border: 1px solid rgba(41,181,232,.5); background: linear-gradient(90deg,#1478A8,#29B5E8); color: #fff; font-weight: 700;}
section[data-testid="stSidebar"] details {border-radius: 12px; background: rgba(255,255,255,.04); border: 1px solid rgba(41,181,232,.25);}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================
@st.cache_data(ttl=600, show_spinner="Loading data from Snowflake...")
def load(sql):
    df = session.sql(sql).to_pandas()
    for c in df.columns:
        if df[c].dtype == object and df[c].notna().any():
            num = pd.to_numeric(df[c], errors="coerce")
            if num.notna().sum() == df[c].notna().sum():
                df[c] = num
    return df


def safe(sql, label):
    try:
        return load(sql)
    except Exception as e:
        st.sidebar.warning(label + ": not available (" + str(e)[0:70] + ")")
        return pd.DataFrame()

orders = safe(f"""
    SELECT f.ORDER_ID, f.ORDER_DATE, d.YEAR_MONTH, d.DAY_NAME,
           st.REGION, st.STORE_ID, st.STORE_NAME,
           p.CATEGORY, p.PRODUCT_ID, p.PRODUCT_NAME, p.BRAND,
           f.SALES_CHANNEL, f.ORDER_STATUS, f.QUANTITY_SOLD,
           f.GROSS_AMOUNT, f.DISCOUNT_AMOUNT, f.TAX_AMOUNT, f.NET_AMOUNT, f.IS_REVENUE_ORDER
    FROM {G}.FACT_SALES_ORDER f
    JOIN {G}.DIM_DATE d ON d.DATE_KEY = f.ORDER_DATE_KEY
    JOIN {G}.DIM_STORE st ON st.STORE_SK = f.STORE_SK
    JOIN {G}.DIM_PRODUCT p ON p.PRODUCT_SK = f.PRODUCT_SK""", "Sales fact")

repl = safe(f"""
    SELECT f.REPLENISHMENT_ID, f.REQUEST_DATE, f.PRIORITY_CODE, f.REPLENISHMENT_STATUS,
           f.DESTINATION_STORE_ID, f.PRODUCT_ID,
           f.REQUEST_QTY, f.ALLOCATED_QTY, f.DISPATCH_QTY, f.DELIVERED_QTY,
           f.LEAD_TIME_DAYS, f.IS_ON_TIME, f.IS_DELIVERED, f.PENDING_QTY,
           w.WAREHOUSE_ID, w.WAREHOUSE_NAME, w.REGION
    FROM {G}.FACT_REPLENISHMENT_ORDER f
    JOIN {G}.DIM_WAREHOUSE w ON w.WAREHOUSE_SK = f.WAREHOUSE_SK""", "Replenishment fact")

inv = safe(f"SELECT * FROM {G}.MART_INVENTORY_HEALTH", "Inventory mart")
risk = safe(f"SELECT * FROM {G}.MART_REORDER_RISK_SCORE", "Risk score")
audit = safe(f"SELECT * FROM {S}.SILVER_LOAD_AUDIT", "Load audit")
dq = safe(f"""SELECT TABLE_NAME, ISSUE_TYPE, ISSUE_REASON, COUNT(*) AS RECORDS
              FROM {S}.SILVER_DQ_EXCEPTIONS GROUP BY 1,2,3""", "DQ exceptions")
layers = safe("""SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT
                 FROM FMCG_DB.INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA IN ('BRONZE','SILVER','GOLD') AND TABLE_TYPE = 'BASE TABLE'""", "Layer stats")
tasks = safe("""SELECT NAME, STATE, SCHEDULED_TIME, COMPLETED_TIME, ERROR_MESSAGE
                FROM TABLE(FMCG_DB.INFORMATION_SCHEMA.TASK_HISTORY(
                     SCHEDULED_TIME_RANGE_START => DATEADD(DAY, -7, CURRENT_TIMESTAMP()),
                     RESULT_LIMIT => 1000))
                WHERE DATABASE_NAME = 'FMCG_DB'""", "Task history")

if orders.empty or inv.empty or repl.empty:
    st.error("Gold tables are empty or missing. Run CALL FMCG_DB.GOLD.SP_GOLD_REFRESH(); first.")
    st.stop()

orders["ORDER_DATE"] = pd.to_datetime(orders["ORDER_DATE"])
orders["IS_REVENUE_ORDER"] = orders["IS_REVENUE_ORDER"].fillna(False).astype(bool)
repl["REQUEST_DATE"] = pd.to_datetime(repl["REQUEST_DATE"])
repl["YEAR_MONTH"] = repl["REQUEST_DATE"].dt.strftime("%Y-%m")
repl["IS_DELIVERED"] = repl["IS_DELIVERED"].fillna(False).astype(bool)
repl["ON_TIME_NUM"] = pd.to_numeric(repl["IS_ON_TIME"].map({True: 1.0, False: 0.0}), errors="coerce")
repl["OT_DELIV"] = repl["ON_TIME_NUM"].where(repl["IS_DELIVERED"])
repl["LEAD_DELIV"] = repl["LEAD_TIME_DAYS"].where(repl["IS_DELIVERED"])

# ============================================================
# HELPERS
# ============================================================
def clean(v, default=0.0):
    try:
        v = float(v)
        if np.isnan(v) or np.isinf(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


def fmt(v, kind="num"):
    v = clean(v, None)
    if v is None:
        return "–"
    if kind == "pct":
        return f"{v:.1f}%"
    if abs(v) >= 1e6:
        return f"{v / 1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{v / 1e3:.1f}K"
    return f"{v:,.0f}"


def div(a, b):
    a, b = clean(a), clean(b)
    return (a / b * 100) if b else 0.0


def opts(df, col):
    return sorted(df[col].dropna().unique().tolist()) if col in df.columns else []


def rerun():
    fn = getattr(st, "rerun", None) or st.experimental_rerun
    fn()


def short_ts(v):
    try:
        return pd.Timestamp(v).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "–"


def kpi(col, label, value, sub="", tone="flat"):
    col.markdown(f'<div class="kpi"><div class="lbl">{label}</div><div class="val">{value}</div>'
                 f'<div class="sub {tone}">{sub}</div></div>', unsafe_allow_html=True)

CHART_N = {"n": 0}

# FIXED: no title=None is ever sent to Plotly.
def show(fig, h=360, title=None):
    layout_options = {
        "template": "plotly_dark",
        "height": h,
        "margin": dict(l=10, r=10, t=50 if title else 15, b=10),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "legend": dict(orientation="h", yanchor="bottom", y=-0.25, x=0),
        "hoverlabel": dict(bgcolor="#0B1F33"),
        "colorway": SEQ,
    }
    if title is not None and str(title).strip():
        layout_options["title"] = dict(text=str(title), font=dict(size=15))
    fig.update_layout(**layout_options)
    CHART_N["n"] += 1
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "responsive": True}, key="chart_" + str(CHART_N["n"]))


def table(df, height=None, progress=None):
    kw = {"use_container_width": True}
    if height:
        kw["height"] = height
    if hasattr(st, "column_config"):
        kw["hide_index"] = True
        if progress:
            kw["column_config"] = {c: st.column_config.ProgressColumn(c, min_value=0, max_value=100, format="%.1f") for c in progress}
    st.dataframe(df, **kw)

# FIXED: no delta=None is sent to Plotly.
def gauge(value, title, target=None, color=BLUE):
    value = clean(value)
    has_target = target is not None
    indicator = {
        "mode": "gauge+number",
        "value": value,
        "number": {"suffix": "%", "font": {"size": 34, "color": "white"}},
        "title": {"text": str(title), "font": {"size": 14, "color": "white"}},
        "gauge": {
            "shape": "angular",
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
            "bar": {"color": color, "thickness": 0.72},
            "bgcolor": "rgba(255,255,255,.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "rgba(229,72,77,.18)"},
                {"range": [60, 85], "color": "rgba(245,165,36,.18)"},
                {"range": [85, 100], "color": "rgba(48,164,108,.18)"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.8, "value": clean(target) if has_target else value},
        },
    }
    if has_target:
        indicator["mode"] = "gauge+number+delta"
        indicator["delta"] = {
            "reference": clean(target), "relative": False, "position": "bottom", "valueformat": ".1f",
            "increasing": {"color": GREEN}, "decreasing": {"color": RED},
        }
    return go.Figure(go.Indicator(**indicator))


def pills_html(values, total, name):
    if len(values) == len(total):
        return f'<span class="sb-pill">All {name}</span>'
    return "".join(f'<span class="sb-pill">{v}</span>' for v in values)


def chip_filter(label, options, key):
    if HAS_PILLS:
        picked = st.sidebar.pills(label, options, selection_mode="multi", default=options, key=key)
    else:
        picked = st.sidebar.multiselect(label, options, default=options, key=key)
    picked = list(picked or [])
    st.sidebar.markdown(f'<div class="sb-count">{len(picked)} of {len(options)} selected</div>', unsafe_allow_html=True)
    return picked


def one_choice(label, options, default, key):
    if HAS_SEG:
        val = st.sidebar.segmented_control(label, options, default=default, key=key)
    else:
        val = st.sidebar.radio(label, options, index=options.index(default), horizontal=True, key=key)
    return val or default

# ============================================================
# SIDEBAR
# ============================================================
all_reg, all_cat, all_ch = opts(orders, "REGION"), opts(orders, "CATEGORY"), opts(orders, "SALES_CHANNEL")
dmin, dmax = orders.ORDER_DATE.min().date(), orders.ORDER_DATE.max().date()
FILTER_KEYS = ("f_reg", "f_cat", "f_ch", "f_period", "f_date", "f_rev")
if st.session_state.get("do_reset"):
    for key_name in FILTER_KEYS:
        st.session_state.pop(key_name, None)
    st.session_state["do_reset"] = False

st.sidebar.markdown('<div class="sb-brand"><div class="sb-logo">📦</div><div class="sb-title">FMCG Pulse</div><div class="sb-sub">Supply Chain Control Tower</div></div>', unsafe_allow_html=True)
last_gold = None
if not tasks.empty:
    ok_runs = tasks.loc[(tasks.NAME == "TASK_GOLD_REFRESH") & (tasks.STATE == "SUCCEEDED"), "COMPLETED_TIME"]
    if len(ok_runs):
        last_gold = short_ts(ok_runs.max())
if last_gold:
    st.sidebar.markdown(f'<div class="sb-status"><div class="sb-dot"></div>Pipeline live · Gold refreshed {last_gold}</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="sb-status"><div class="sb-dot off"></div>Pipeline status unknown</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sb-head">🌍 Where</div>', unsafe_allow_html=True)
sel_reg = chip_filter("Region", all_reg, "f_reg")
st.sidebar.markdown('<div class="sb-head">🏷️ What</div>', unsafe_allow_html=True)
sel_cat = chip_filter("Category", all_cat, "f_cat")
sel_ch = chip_filter("Sales channel", all_ch, "f_ch")
st.sidebar.markdown('<div class="sb-head">📅 When</div>', unsafe_allow_html=True)
PERIODS = ["Year", "6M", "3M", "1M", "Custom"]
period = one_choice("Period", PERIODS, "Year", "f_period")
months_back = {"6M": 6, "3M": 3, "1M": 1}.get(period)
if period == "Custom":
    dr = st.sidebar.date_input("Pick dates", value=(dmin, dmax), min_value=dmin, max_value=dmax, key="f_date")
    d_from, d_to = dr if isinstance(dr, (list, tuple)) and len(dr) == 2 else (dmin, dmax)
elif months_back:
    d_from, d_to = max((pd.Timestamp(dmax) - pd.DateOffset(months=months_back)).date(), dmin), dmax
else:
    d_from, d_to = dmin, dmax

st.sidebar.markdown('<div class="sb-head">⚙️ Options</div>', unsafe_allow_html=True)
only_revenue = st.sidebar.toggle("Revenue orders only", value=False, key="f_rev", help="Hide cancelled and returned orders") if HAS_TOGGLE else st.sidebar.checkbox("Revenue orders only", value=False, key="f_rev")
b1, b2 = st.sidebar.columns(2)
if b1.button("↺ Reset"):
    st.session_state["do_reset"] = True
    rerun()
if b2.button("🔄 Refresh"):
    st.cache_data.clear()
    rerun()

st.sidebar.markdown('<div class="sb-head">🎯 Targets</div>', unsafe_allow_html=True)
with st.sidebar.expander("Adjust KPI targets"):
    t_fill = st.slider("Fill rate target %", 50, 100, 95)
    t_ontime = st.slider("On-time target %", 50, 100, 90)
    t_so = st.slider("Max stock-out rate %", 1, 50, 5)
    t_lead = st.slider("Max avg lead time (days)", 1, 30, 7)

st.sidebar.markdown(f'<div class="sb-card"><b>Active view</b><br>{pills_html(sel_reg, all_reg, "regions")}{pills_html(sel_cat, all_cat, "categories")}{pills_html(sel_ch, all_ch, "channels")}<span class="sb-pill">📅 {d_from} → {d_to}</span></div>', unsafe_allow_html=True)

if not sel_reg or not sel_cat or not sel_ch:
    st.warning("Select at least one region, category and channel.")
    st.stop()

# ============================================================
# FILTERS + KPIs
# ============================================================
ts_from, ts_to = pd.Timestamp(d_from), pd.Timestamp(d_to)
o = orders[orders.REGION.isin(sel_reg) & orders.CATEGORY.isin(sel_cat) & orders.SALES_CHANNEL.isin(sel_ch) & orders.ORDER_DATE.between(ts_from, ts_to)]
if only_revenue:
    o = o[o.IS_REVENUE_ORDER]
rev = o[o.IS_REVENUE_ORDER]
i = inv[inv.REGION.isin(sel_reg) & inv.CATEGORY.isin(sel_cat)]
rf = repl[repl.REGION.isin(sel_reg) & repl.REQUEST_DATE.between(ts_from, ts_to)]
k0 = risk if risk.empty else risk[(risk.REGION.isin(sel_reg) | risk.REGION.isna()) & (risk.CATEGORY.isin(sel_cat) | risk.CATEGORY.isna())].copy()
if not risk.empty and k0.empty:
    st.sidebar.info("Risk filters matched 0 rows; showing all risk items.")
    k0 = risk.copy()
if o.empty:
    st.warning("No orders match these filters.")
    st.stop()

net, gross, disc, tax = rev.NET_AMOUNT.sum(), rev.GROSS_AMOUNT.sum(), rev.DISCOUNT_AMOUNT.sum(), rev.TAX_AMOUNT.sum()
units, n_orders, lost = rev.QUANTITY_SOLD.sum(), len(o), int((~o.IS_REVENUE_ORDER).sum())
items = i.PRODUCT_COUNT.sum()
so_rate, low_rate, ex_rate = div(i.STOCK_OUT_COUNT.sum(), items), div(i.LOW_STOCK_COUNT.sum(), items), div(i.EXCESS_STOCK_COUNT.sum(), items)
fill = div(rf.DELIVERED_QTY.sum(), rf.REQUEST_QTY.sum())
ontime, lead = clean(rf.OT_DELIV.mean() * 100), clean(rf.LEAD_DELIV.mean())
monthly = rev.groupby("YEAR_MONTH", as_index=False).agg(NET=("NET_AMOUNT", "sum"), UNITS=("QUANTITY_SOLD", "sum"), ORDERS=("ORDER_ID", "count"))
mom = div(monthly.NET.iloc[-1] - monthly.NET.iloc[-2], monthly.NET.iloc[-2]) if len(monthly) >= 2 else None
att = {"Fill rate": min(max(fill / t_fill, 0), 1), "On-time delivery": min(max(ontime / t_ontime, 0), 1), "Stock availability": min(max(t_so / max(so_rate, .01), 0), 1), "Lead time": min(max(t_lead / max(lead, .01), 0), 1)}
health = float(np.mean([clean(v) for v in att.values()]) * 100)
hcolor = GREEN if health >= 85 else (AMBER if health >= 65 else RED)

# ============================================================
# HEADER + TABS
# ============================================================
st.markdown(f'<div class="hero"><h1>FMCG Pulse · Supply Chain Control Tower</h1><p><span class="chip">📅 {d_from} → {d_to}</span><span class="chip">🌍 {len(sel_reg)} regions</span><span class="chip">🏷️ {len(sel_cat)} categories</span><span class="chip">🛒 {len(sel_ch)} channels</span><span class="chip">❤️ Health {health:.0f}/100</span><span class="chip">S3 → Bronze → Silver (SCD2) → Gold → Snowpark</span></p></div>', unsafe_allow_html=True)

t_cmd, t_sales, t_inv, t_repl, t_risk, t_store, t_quality = st.tabs(["🎯 Command Center", "💰 Sales Studio", "📦 Inventory Lens", "🚚 Replenishment", "⚠️ Risk Simulator", "🏬 Store 360", "🧪 Quality & Pipeline"])

# ============================================================
# TAB 1: COMMAND CENTER
# ============================================================
with t_cmd:
    c = st.columns(6)
    kpi(c[0], "Net sales", fmt(net), "–" if mom is None else f"{mom:+.1f}% vs last month", "flat" if mom is None else ("up" if mom >= 0 else "down"))
    kpi(c[1], "Units sold", fmt(units), fmt(len(rev)) + " revenue orders")
    kpi(c[2], "Lost orders", f"{div(lost, n_orders):.1f}%", f"{lost:,} cancelled / returned", "down")
    kpi(c[3], "Stock-out rate", fmt(so_rate, "pct"), f"target ≤ {t_so}%", "up" if so_rate <= t_so else "down")
    kpi(c[4], "Fill rate", fmt(fill, "pct"), f"{fill - t_fill:+.1f} pts vs target", "up" if fill >= t_fill else "down")
    kpi(c[5], "Avg lead time", f"{lead:.1f} d", f"target ≤ {t_lead} d", "up" if lead <= t_lead else "down")

    g0, g1, g2 = st.columns(3)
    with g0: show(gauge(health, "Health score", color=hcolor), h=240)
    with g1: show(gauge(fill, "Fill rate", target=t_fill, color=BLUE), h=240)
    with g2: show(gauge(100 - so_rate, "In-stock rate", target=100 - t_so, color=PURPLE), h=240)

    a, b = st.columns([2, 1])
    with a:
        mt = monthly.copy(); mt["ROLL"] = mt.NET.rolling(3, min_periods=1).mean()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=mt.YEAR_MONTH, y=mt.NET, name="Net sales", marker_color=BLUE, opacity=.85)
        fig.add_scatter(x=mt.YEAR_MONTH, y=mt.ROLL, name="3-month avg", mode="lines", line=dict(color="white", dash="dash"))
        fig.add_scatter(x=mt.YEAR_MONTH, y=mt.ORDERS, name="Orders", mode="lines+markers", line=dict(color=AMBER), secondary_y=True)
        show(fig, 340, "Net sales, trend and orders")
    with b:
        if not k0.empty:
            bd = k0.RISK_BAND.value_counts().reindex(BANDS).fillna(0).reset_index(); bd.columns = ["BAND", "ITEMS"]
            fig = px.pie(bd, names="BAND", values="ITEMS", hole=.6, color="BAND", color_discrete_map=BAND_COLORS); fig.update_traces(textinfo="percent+label")
            show(fig, 340, "Reorder risk mix")

# ============================================================
# TAB 2: SALES STUDIO
# ============================================================
with t_sales:
    c = st.columns(6)
    kpi(c[0], "Net sales", fmt(net)); kpi(c[1], "Gross sales", fmt(gross)); kpi(c[2], "Discount", fmt(div(disc, gross), "pct"), fmt(disc)); kpi(c[3], "Avg selling price", f"{gross / units:,.2f}" if units else "–"); kpi(c[4], "Avg order value", f"{net / len(rev):,.0f}" if len(rev) else "–"); kpi(c[5], "Cancel + return", fmt(div(lost, n_orders), "pct"), "", "down")
    measure = st.radio("Measure", ["Net sales", "Units", "Orders"], horizontal=True)
    rv = rev.copy(); rv["VAL"] = rv.NET_AMOUNT if measure == "Net sales" else (rv.QUANTITY_SOLD if measure == "Units" else 1)
    a, b = st.columns([3, 2])
    with a:
        fig = px.treemap(rv, path=[px.Constant("All regions"), "REGION", "CATEGORY"], values="VAL", color="VAL", color_continuous_scale="Blues"); fig.update_traces(textinfo="label+value+percent root", root_color="rgba(0,0,0,0)"); show(fig, 420, measure + " treemap · click a region to drill in")
    with b:
        fig = px.sunburst(o.assign(N=1), path=["SALES_CHANNEL", "ORDER_STATUS"], values="N", color="SALES_CHANNEL"); show(fig, 420, "Channel → order status · click to zoom")
    daily = rv.groupby(rv.ORDER_DATE.dt.date).VAL.sum().reset_index(); daily.columns = ["DATE", "VAL"]
    fig = px.area(daily, x="DATE", y="VAL", color_discrete_sequence=[BLUE]); show(fig, 360, "Daily " + measure.lower())
    st.markdown('<div class="section">🏬 Store leaderboard</div>', unsafe_allow_html=True)
    lb = rev.groupby(["STORE_ID", "STORE_NAME", "REGION"], as_index=False).agg(NET_SALES=("NET_AMOUNT", "sum"), UNITS=("QUANTITY_SOLD", "sum"), ORDERS=("ORDER_ID", "count")).sort_values("NET_SALES", ascending=False)
    lb["SHARE_%"] = lb.NET_SALES / lb.NET_SALES.max() * 100
    table(lb.head(15), progress=["SHARE_%"])
    st.download_button("⬇️ Download filtered orders (CSV)", o.to_csv(index=False), file_name="filtered_orders.csv", mime="text/csv")

# ============================================================
# TAB 3: INVENTORY
# ============================================================
with t_inv:
    c = st.columns(6)
    kpi(c[0], "Locations", f"{i.LOCATION_ID.nunique():,}"); kpi(c[1], "On-hand qty", fmt(i.ON_HAND_QTY.sum())); kpi(c[2], "Available qty", fmt(i.AVAILABLE_QTY.sum())); kpi(c[3], "Stock-out rate", fmt(so_rate, "pct"), "", "down" if so_rate > t_so else "up"); kpi(c[4], "Low-stock rate", fmt(low_rate, "pct")); kpi(c[5], "Excess rate", fmt(ex_rate, "pct"))
    metric = st.radio("Heatmap metric", ["Stock-out %", "Low-stock %", "Excess %"], horizontal=True)
    col, scale = ("STOCK_OUT_COUNT", "Reds") if metric == "Stock-out %" else (("LOW_STOCK_COUNT", "Oranges") if metric == "Low-stock %" else ("EXCESS_STOCK_COUNT", "Purples"))
    hm = i.groupby(["REGION", "CATEGORY"])[[col, "PRODUCT_COUNT"]].sum(); hm["PCT"] = hm[col] / hm.PRODUCT_COUNT.replace(0, np.nan) * 100
    fig = px.imshow(hm.PCT.unstack().round(1), aspect="auto", color_continuous_scale=scale, text_auto=".0f"); show(fig, 380, metric + " · region × category")

# ============================================================
# TAB 4: REPLENISHMENT
# ============================================================
with t_repl:
    c = st.columns(6)
    kpi(c[0], "Replenishments", f"{len(rf):,}"); kpi(c[1], "Delivered", f"{int(rf.IS_DELIVERED.sum()):,}"); kpi(c[2], "Fill rate", fmt(fill, "pct"), f"{fill - t_fill:+.1f} vs target", "up" if fill >= t_fill else "down"); kpi(c[3], "On-time", fmt(ontime, "pct"), f"{ontime - t_ontime:+.1f} vs target", "up" if ontime >= t_ontime else "down"); kpi(c[4], "Avg lead time", f"{lead:.1f} d", f"{lead - t_lead:+.1f} vs target", "up" if lead <= t_lead else "down"); kpi(c[5], "Pending qty", fmt(rf.PENDING_QTY.sum()))
    fig = go.Figure(go.Funnel(y=["Requested", "Allocated", "Dispatched", "Delivered"], x=[rf.REQUEST_QTY.sum(), rf.ALLOCATED_QTY.sum(), rf.DISPATCH_QTY.sum(), rf.DELIVERED_QTY.sum()], textinfo="value+percent initial", marker=dict(color=["#0B3C5D", NAVY, BLUE, GREEN]))); show(fig, 360, "Quantity funnel")
    scw = rf.groupby(["WAREHOUSE_ID", "WAREHOUSE_NAME", "REGION"], as_index=False).agg(ORDERS=("REPLENISHMENT_ID", "count"), REQ=("REQUEST_QTY", "sum"), DLV=("DELIVERED_QTY", "sum"), OT=("OT_DELIV", "mean"), LEAD=("LEAD_DELIV", "mean"), PENDING_QTY=("PENDING_QTY", "sum"))
    scw["FILL_RATE_%"] = (scw.DLV / scw.REQ.replace(0, np.nan) * 100).round(1); scw["ON_TIME_%"] = (scw.OT * 100).round(1); scw["AVG_LEAD_DAYS"] = scw.LEAD.round(1)
    scw = scw.drop(columns=["REQ", "DLV", "OT", "LEAD"]).sort_values("FILL_RATE_%"); table(scw, height=320, progress=["FILL_RATE_%", "ON_TIME_%"])

# ============================================================
# TAB 5: RISK SIMULATOR
# ============================================================
with t_risk:
    if k0.empty:
        st.info("No risk data. Run the Snowpark notebook, then refresh.")
    else:
        preset_names = ["Baseline", "Peak season (+50% demand)", "Supplier delay (+5 days)", "Worst case"]
        preset_values = {"Baseline": (0, 0), "Peak season (+50% demand)": (50, 0), "Supplier delay (+5 days)": (0, 5), "Worst case": (80, 7)}
        preset = st.segmented_control("Quick scenario", preset_names, default="Baseline", key="preset") if HAS_SEG else st.radio("Quick scenario", preset_names, horizontal=True, key="preset")
        preset = preset or "Baseline"; p_dem, p_del = preset_values[preset]
        with st.expander("🎛️ Fine-tune the scoring rules", expanded=False):
            w = st.columns(5)
            wt_so, wt_rp, wt_cv, wt_ss, wt_np = w[0].slider("Stock-out pts", 0, 60, 40, 5), w[1].slider("Below reorder pts", 0, 60, 25, 5), w[2].slider("Cover < lead pts", 0, 60, 20, 5), w[3].slider("Below safety pts", 0, 60, 10, 5), w[4].slider("No pending pts", 0, 60, 5, 5)
            x = st.columns(4)
            high_t, med_t = x[0].slider("HIGH if score ≥", 10, 150, 60, 5), x[1].slider("MEDIUM if score ≥", 0, 145, 30, 5)
            demand_pct, delay = x[2].slider("Demand change %", -50, 150, p_dem, 10, key="dem_" + preset), x[3].slider("Supplier delay (days)", 0, 15, p_del, 1, key="del_" + preset)
        if med_t >= high_t:
            st.error("MEDIUM threshold must be lower than HIGH threshold."); st.stop()
        k = k0.copy(); demand = k.AVG_DAILY_DEMAND.fillna(0) * (1 + demand_pct / 100); k["WI_DEMAND"] = demand
        k["WI_COVER"] = np.where(demand > 0, k.AVAILABLE_QTY.fillna(0) / demand.replace(0, np.nan), 9999); k["WI_LEAD"] = k.AVG_LEAD_TIME_DAYS.fillna(0) + delay
        f_so = k.AVAILABLE_QTY.fillna(0) <= 0; f_rp = k.AVAILABLE_QTY.fillna(0) <= k.REORDER_POINT.fillna(0); f_cv = k.WI_COVER < k.WI_LEAD; f_ss = k.AVAILABLE_QTY.fillna(0) < k.SAFETY_STOCK.fillna(0); f_np = (k.PENDING_REPLEN_QTY.fillna(0) == 0) & f_rp
        k["WI_SCORE"] = (wt_so*f_so + wt_rp*f_rp + wt_cv*f_cv + wt_ss*f_ss + wt_np*f_np).astype(int); k["WI_BAND"] = np.select([k.WI_SCORE >= high_t, k.WI_SCORE >= med_t], ["HIGH", "MEDIUM"], default="LOW")
        need = k.REORDER_POINT.fillna(0) + k.SAFETY_STOCK.fillna(0) + demand*k.WI_LEAD - k.AVAILABLE_QTY.fillna(0) - k.PENDING_REPLEN_QTY.fillna(0); k["SUGGESTED_ORDER_QTY"] = np.ceil(need.fillna(0).clip(lower=0)).astype(int); k.loc[k.WI_BAND == "LOW", "SUGGESTED_ORDER_QTY"] = 0
        cnt = {b_: int((k.WI_BAND == b_).sum()) for b_ in BANDS}; c = st.columns(4)
        for idx, band in enumerate(BANDS): kpi(c[idx], band + " risk", f"{cnt[band]:,}")
        kpi(c[3], "Suggested order", fmt(k.SUGGESTED_ORDER_QTY.sum()), "units to reorder")
        fig = px.histogram(k, x="WI_SCORE", color="WI_BAND", nbins=20, color_discrete_map=BAND_COLORS, category_orders={"WI_BAND": BANDS}); fig.add_vline(x=high_t, line_dash="dash", line_color=RED); fig.add_vline(x=med_t, line_dash="dash", line_color=AMBER); show(fig, 400, "Score distribution")

# ============================================================
# TAB 6: STORE 360
# ============================================================
with t_store:
    stores = o.loc[:, ["STORE_ID", "STORE_NAME", "REGION"]].drop_duplicates().sort_values("STORE_ID").reset_index(drop=True)
    labels = (stores.STORE_ID.astype(str) + " · " + stores.STORE_NAME.astype(str) + " (" + stores.REGION.astype(str) + ")").tolist()
    pick_label = st.selectbox("🏬 Choose a store", labels); srow = stores.iloc[labels.index(pick_label)]; sid, sreg = srow.STORE_ID, srow.REGION
    srev, sall, rr = rev[rev.STORE_ID == sid], o[o.STORE_ID == sid], rev[rev.REGION == sreg]
    srisk = k0[k0.STORE_ID == sid] if not k0.empty else pd.DataFrame(); sin = repl[repl.DESTINATION_STORE_ID == sid]
    c = st.columns(6)
    kpi(c[0], "Net sales", fmt(srev.NET_AMOUNT.sum())); kpi(c[1], "Units", fmt(srev.QUANTITY_SOLD.sum())); kpi(c[2], "Orders", f"{len(sall):,}"); kpi(c[3], "Region", str(sreg)); kpi(c[4], "HIGH-risk items", f"{int((srisk.RISK_BAND == 'HIGH').sum()) if len(srisk) else 0}"); kpi(c[5], "Inbound pending", fmt(sin.PENDING_QTY.sum()))
    sm = srev.groupby("YEAR_MONTH", as_index=False).NET_AMOUNT.sum(); fig = px.line(sm, x="YEAR_MONTH", y="NET_AMOUNT", markers=True, color_discrete_sequence=[BLUE]); show(fig, 380, "Monthly net sales")

# ============================================================
# TAB 7: QUALITY & PIPELINE
# ============================================================
with t_quality:
    st.markdown('<div class="section">🧪 Data quality</div>', unsafe_allow_html=True)
    if audit.empty:
        st.info("No Silver load audit available.")
    else:
        is_ok = audit.STATUS.astype(str).str.startswith("SUCCESS"); ok = audit[is_ok].fillna(0)
        staged, inserted, rej, dup, stale = ok.STAGED.sum(), ok.INSERTED.sum(), ok.REJECTED.sum(), ok.DUPLICATES.sum(), ok.STALE.sum(); failed = int((~is_ok).sum())
        c = st.columns(6)
        kpi(c[0], "Rows staged", f"{staged:,.0f}"); kpi(c[1], "Inserted", f"{inserted:,.0f}", "", "up"); kpi(c[2], "Rejected", f"{rej:,.0f}", "", "down"); kpi(c[3], "Dup + stale", f"{dup + stale:,.0f}"); kpi(c[4], "Acceptance", fmt(div(inserted, staged), "pct")); kpi(c[5], "Failed runs", f"{failed}", "", "up" if failed == 0 else "down")
        if not dq.empty:
            rr2 = dq.groupby(["ISSUE_TYPE", "ISSUE_REASON"], as_index=False).RECORDS.sum(); fig = px.bar(rr2.sort_values("RECORDS"), y="ISSUE_REASON", x="RECORDS", color="ISSUE_TYPE", orientation="h", text_auto=True); show(fig, 360, "Exceptions by reason")
    nodes = ["Source files", "IDMC", "S3", "BRONZE", "SILVER (SCD2)", "GOLD", "SNOWPARK", "CONSUMPTION", "STREAMLIT"]
    fig = go.Figure(go.Sankey(node=dict(label=nodes, pad=25, thickness=20, color=["#5BC0EB", PURPLE, AMBER, "#CD7F32", "#C0C0C0", "#FFD700", BLUE, GREEN, RED]), link=dict(source=[0,1,2,3,4,5,5,6,6], target=[1,2,3,4,5,6,7,8,7], value=[10,10,10,10,10,6,4,4,2], color="rgba(41,181,232,.25)"))); show(fig, 300, "Data flow · S3 → Bronze → Silver → Gold → Snowpark → apps")
    if not tasks.empty:
        tl = tasks.dropna(subset=["SCHEDULED_TIME"]).copy(); tl["SCHEDULED_TIME"] = pd.to_datetime(tl.SCHEDULED_TIME)
        fig = px.scatter(tl, x="SCHEDULED_TIME", y="NAME", color="STATE", color_discrete_map={"SUCCEEDED": GREEN, "SKIPPED": "#888", "FAILED": RED, "SCHEDULED": BLUE, "EXECUTING": AMBER}, hover_data=["ERROR_MESSAGE"]); fig.update_traces(marker=dict(size=12, symbol="diamond")); show(fig, 360, "Task-run timeline · drag to zoom")
