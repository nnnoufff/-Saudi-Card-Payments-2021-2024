"""Saudi Card Payments dashboard (Streamlit).

Weekly card (point-of-sale) payments in Saudi Arabia, May 2020 - July 2025.
Run with:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Saudi Card Payments", page_icon="💸", layout="wide")

# ================================================================ constants and style
ACCENT, INK, MUTED, GRID = "#006c35", "#12312e", "#5d6f6b", "#e3ebe8"
GOLD, SOFT = "#c9a227", "#a9d9bb"
SERIES = ["#1f6feb", "#e8743b", "#14a38b", "#8a5cc2"]   # validated categorical order
BLUE, NEUTRAL, UP, DOWN = "#1a8f4e", "#b4bac6", "#1a8f4e", "#e5484d"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL_YEARS = [2021, 2022, 2023, 2024]
DATA_PATH = Path(__file__).parent / "clean_data.csv"
MEASURES = {
    "Spending": {"unit": "billion SAR per week", "fmt": ".1f", "short": "bn SAR"},
    "Number of payments": {"unit": "million payments per week", "fmt": ".0f", "short": "million"},
    "Average payment": {"unit": "SAR per payment", "fmt": ".0f", "short": "SAR"},
}
PAGES = ["🏠  Overview", "🛍️  Sectors", "🏙️  Cities", "🌙  Seasonal Insights", "📋  Data & Methodology"]

st.markdown(
    f"""
    <style>
      .block-container {{padding: 4rem 2.2rem 3rem 2.2rem; max-width: 100%;}}
      [data-testid="stSidebar"] {{background: #ffffff; border-right: 1px solid {GRID};}}
      [data-testid="stSidebar"] [role="radiogroup"] {{gap: 0.15rem;}}
      [data-testid="stSidebar"] [role="radiogroup"] label {{padding: 0.55rem 0.8rem; border-radius: 10px; width: 100%;}}
      [data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {{display: none;}}
      [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{background: {ACCENT};}}
      [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {{color: #fff !important; font-weight: 600;}}
      div[data-testid="stVerticalBlockBorderWrapper"] {{background: #fff; border: 1px solid {GRID}; border-radius: 14px;}}
      .ptitle {{font-size: 2rem !important; font-weight: 700; color: {INK}; margin: 0; line-height: 1.2;}}
      .hdr {{display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1rem; padding: 1.2rem 1.6rem; border-radius: 16px; background: linear-gradient(120deg, #004d26 0%, #006c35 60%, #1a8f4e 100%); border-bottom: 4px solid {GOLD};}}
      .hdr .ptitle {{color: #fff;}} .hdr .psub {{color: #d6eedd;}} .hdr .flying {{font-size: 2.2rem; letter-spacing: 0.3rem; opacity: 0.95;}}
      .psub {{color: {MUTED}; margin: 0.2rem 0 0 0;}}
      .pill {{display: inline-block; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.35); border-radius: 10px; padding: 0.3rem 0.8rem; color: #fff; font-size: 0.82rem; margin-top: 0.3rem;}}
      .kpi {{background: #fff; border: 1px solid {GRID}; border-radius: 14px; padding: 1rem 1.1rem; display: flex; gap: 0.9rem; align-items: center;}}
      .kpi .ic {{width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex: none;}}
      .kpi .lb {{color: {MUTED}; font-size: 0.85rem;}}
      .kpi .vl {{color: {INK}; font-size: 1.7rem; font-weight: 700; line-height: 1.2;}}
      .kpi .dl {{display: inline-block; font-size: 0.78rem; padding: 0.1rem 0.5rem; border-radius: 999px; margin-top: 0.2rem;}}
      .up {{background: #dcf5ec; color: #0b7a5a;}} .down {{background: #fde4e5; color: #b4232a;}} .flat {{background: #eef1f0; color: {MUTED};}}
      .ctitle {{font-size: 1.05rem; font-weight: 650; color: {INK}; margin: 0;}}
      .csub {{color: {MUTED}; font-size: 0.85rem; margin: 0 0 0.4rem 0;}}
      .how {{background: #f1f7f5; border-left: 4px solid {ACCENT}; padding: 0.5rem 0.8rem; border-radius: 6px; color: {INK}; font-size: 0.92rem; margin: 0.2rem 0 0.6rem 0;}}
      .big {{font-size: 2.4rem; font-weight: 700; line-height: 1.1;}}
      .bigsub {{color: {MUTED}; font-size: 0.85rem;}}
      .stat {{background: #fff; border: 1px solid {GRID}; border-radius: 14px; padding: 0.9rem 1.1rem;}}
      .takeaway li {{margin-bottom: 0.4rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)


# ================================================================ data
@st.cache_data
def load_data() -> pd.DataFrame:
    d = pd.read_csv(DATA_PATH, parse_dates=["date"])
    d["spending_bn"] = d["value_sar_k"] / 1e6
    d["payments_m"] = d["transactions_k"] / 1e3
    return d


df = load_data()


def meas(t: pd.DataFrame, measure: str) -> pd.Series:
    t = t.sort_values("date").set_index("date")
    if measure == "Spending":
        return t["spending_bn"]
    if measure == "Number of payments":
        return t["payments_m"]
    return t["value_sar_k"] / t["transactions_k"]


def period_value(t: pd.DataFrame, measure: str) -> float:
    """One number for a table: weekly average (or weighted average payment)."""
    if t.empty:
        return float("nan")
    if measure == "Average payment":
        return t["value_sar_k"].sum() / t["transactions_k"].sum()
    return t["spending_bn" if measure == "Spending" else "payments_m"].mean()


def compare_event(table: pd.DataFrame, flag: str) -> pd.DataFrame:
    table = table.sort_values("date").reset_index(drop=True)
    is_event = table[flag] == 1
    eid_ = (is_event != is_event.shift()).cumsum()
    rows = []
    for _, ev in table[is_event].groupby(eid_[is_event]):
        first, last = ev.index.min(), ev.index.max()
        around = pd.concat([table.loc[max(0, first - 4):first - 1], table.loc[last + 1:last + 4]])
        around = around[around[flag] == 0]
        rows.append({
            "year": ev["date"].min().year,
            "value": (ev["value_sar_k"].mean() / around["value_sar_k"].mean() - 1) * 100,
            "transactions": (ev["transactions_k"].mean() / around["transactions_k"].mean() - 1) * 100,
            "ticket": (ev["avg_ticket_sar"].mean() / around["avg_ticket_sar"].mean() - 1) * 100,
        })
    out = pd.DataFrame(rows)
    return out[out["year"].isin(FULL_YEARS)]


@st.cache_data
def event_effect(level: str, name: str | None, flag: str) -> pd.Series:
    t = df[df["level"] == level]
    if name:
        t = t[t["name"] == name]
    return compare_event(t, flag)[["value", "transactions", "ticket"]].mean()


@st.cache_data
def event_by_name(level: str, flag: str) -> pd.Series:
    names = sorted(df.loc[df["level"] == level, "name"].unique())
    return pd.Series({n: event_effect(level, n, flag)["value"] for n in names}).sort_values()


@st.cache_data
def event_by_year(level: str, name: str | None, flag: str) -> pd.DataFrame:
    t = df[df["level"] == level]
    if name:
        t = t[t["name"] == name]
    return compare_event(t, flag)


@st.cache_data
def ramadan_profile(level: str, name: str | None) -> pd.DataFrame:
    """Weekly spending index (100 = the 4 weeks before and after) around each Ramadan, averaged over 2021-2024."""
    t = df[df["level"] == level]
    if name:
        t = t[t["name"] == name]
    t = t.sort_values("date").reset_index(drop=True)
    ev = t["is_ramadan"] == 1
    bid = (ev != ev.shift()).cumsum()
    rows, lengths = [], []
    for _, b in t[ev].groupby(bid[ev]):
        if b["date"].min().year not in FULL_YEARS:
            continue
        first, last = b.index.min(), b.index.max()
        lengths.append(len(b))
        around = pd.concat([t.loc[first - 4:first - 1], t.loc[last + 1:last + 4]])
        base = around["value_sar_k"].mean()
        for k in range(-6, len(b) + 6):
            if 0 <= first + k < len(t):
                rows.append({"week": k, "index": t.loc[first + k, "value_sar_k"] / base * 100})
    prof = pd.DataFrame(rows).groupby("week")["index"].mean().reset_index()
    prof.attrs["len"] = min(lengths)
    return prof


@st.cache_data
def pay_cycle() -> pd.Series:
    nat = df[df["level"] == "national"].sort_values("date").reset_index(drop=True)
    nat["dev"] = (nat["value_sar_k"] / nat["value_sar_k"].rolling(9, center=True, min_periods=5).median() - 1) * 100
    cyc = nat[nat["year"].between(2021, 2024) & (nat["is_ramadan"] == 0)].copy()
    cyc["bucket"] = pd.cut(cyc["date"].dt.day, [0, 6, 13, 20, 27, 31],
                           labels=["1st-6th", "7th-13th", "14th-20th", "21st-27th", "28th-31st"])
    return cyc.groupby("bucket", observed=True)["dev"].mean()


EID_FITR = ["2021-05-13", "2022-05-02", "2023-04-21", "2024-04-10", "2025-03-30"]


@st.cache_data
def eid_profile(level: str, name: str | None) -> pd.Series:
    t = df[df["level"] == level]
    if name:
        t = t[t["name"] == name]
    t = t.sort_values("date").reset_index(drop=True)
    rows = []
    for d in EID_FITR:
        d = pd.Timestamp(d)
        i = t.index[(t["date"] <= d) & (t["date"] + pd.Timedelta(days=6) >= d)][0]
        base = pd.concat([t.loc[i - 6:i - 4], t.loc[i + 3:i + 5]])["value_sar_k"].mean()
        for k in range(-3, 3):
            rows.append({"week": k, "change": (t.loc[i + k, "value_sar_k"] / base - 1) * 100})
    return pd.DataFrame(rows).groupby("week")["change"].mean()


# ================================================================ chart helpers
_n = [0]


def style(fig: go.Figure, height: int = 360, legend: bool = True) -> go.Figure:
    fig.update_layout(height=height, margin=dict(l=4, r=4, t=8, b=4), showlegend=legend, bargap=0.3,
                      font=dict(color=INK), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None), hoverlabel=dict(font_size=13))
    fig.update_xaxes(showgrid=False, ticks="outside", tickcolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def show(fig: go.Figure) -> None:
    _n[0] += 1
    st.plotly_chart(fig, theme="streamlit", width="stretch", config={"displaylogo": False}, key=f"c{_n[0]}")


def card_title(title: str, sub: str = "") -> None:
    for key, icon in [("ranked", "🏆"), ("growth", "📈"), ("Average payment", "🏷️"), ("month", "🗓️"), ("Typical", "🗓️"), ("Share", "🥧"),
                      ("stands out", "💡"), ("Spending", "💸"), ("Weekly", "💸"), ("Ramadan", "🌙"), ("Eid", "🎁"), ("pay", "💰"),
                      ("Change", "📊"), ("Data", "🗂️"), ("Summary", "🧮"), ("Key", "📌"), ("over time", "📉"), ("by year", "📆")]:
        if key.lower() in title.lower():
            title = f"{icon} {title}"
            break
    st.markdown(f"<p class='ctitle'>{title}</p><p class='csub'>{sub}</p>", unsafe_allow_html=True)


def how(text: str) -> None:
    st.markdown(f"<div class='how'><b>How to read:</b> {text}</div>", unsafe_allow_html=True)


def header(title: str, sub: str) -> None:
    pill = f"{df['date'].min():%b %Y} - {df['date'].max():%b %Y} · national, 17 sectors, 11 cities"
    st.markdown(f"<div class='hdr'><div><div class='ptitle'>{title}</div><div class='psub'>{sub}</div></div><div style='text-align:right'><div class='flying'>💸 💳 💰</div><div class='pill'>{pill}</div></div></div>",
                unsafe_allow_html=True)


def kpi(label: str, value: str, delta: str | None, tone: str, icon: str, bg: str) -> None:
    d = f"<span class='dl {tone}'>{delta}</span>" if delta else ""
    st.markdown(f"<div class='kpi'><div class='ic' style='background:{bg}'>{icon}</div><div><div class='lb'>{label}</div>"
                f"<div class='vl'>{value}</div>{d}</div></div>", unsafe_allow_html=True)


def change_bars(s: pd.Series, height: int | None = None, title_x: str = "Change (%)") -> go.Figure:
    s = s.sort_values()
    fig = go.Figure(go.Bar(x=s.values, y=s.index, orientation="h", marker_color=[UP if v >= 0 else DOWN for v in s.values],
                           text=[f"{v:+.1f}%" for v in s.values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:+.1f}%<extra></extra>"))
    lo, hi = min(s.min(), 0), max(s.max(), 0)
    pad = (hi - lo) * 0.18
    fig.update_xaxes(range=[lo - pad, hi + pad], title_text=title_x, zeroline=True, zerolinecolor=MUTED)
    fig.update_yaxes(showgrid=False)
    return style(fig, height or 110 + 26 * len(s), legend=False)


def ramadan_bands(fig: go.Figure) -> None:
    r = df[df["level"] == "national"].sort_values("date")
    r = r[(r["date"].dt.year >= y1) & (r["date"].dt.year <= y2)]
    g = (r["is_ramadan"] != r["is_ramadan"].shift()).cumsum()
    for _, b in r[r["is_ramadan"] == 1].groupby(g[r["is_ramadan"] == 1]):
        fig.add_vrect(x0=b["date"].min(), x1=b["date"].max() + pd.Timedelta(days=7), fillcolor=NEUTRAL, opacity=0.25,
                      line_width=0, layer="below")


def colors_for(names: list[str], key: str) -> dict[str, str]:
    slots = st.session_state.setdefault(f"slots_{key}", {})
    for n in list(slots):
        if n not in names:
            slots.pop(n)
    free = [c for c in SERIES if c not in slots.values()]
    for n in names:
        if n not in slots:
            slots[n] = free.pop(0)
    return {n: slots[n] for n in names}


def line_chart(level: str, names: list[str], key: str, height: int = 380) -> None:
    col = colors_for(names, key)
    if len(names) == 1:
        col = {names[0]: BLUE}
    fig = go.Figure()
    for n in names:
        t = df[(df["level"] == level) & (df["name"] == n) & df["year"].between(y1, y2)] if level != "national" \
            else df[(df["level"] == "national") & df["year"].between(y1, y2)]
        y = meas(t, measure)
        y = y.rolling(4, min_periods=1).mean() if smooth else y
        fig.add_trace(go.Scatter(x=y.index, y=y.values, mode="lines", name=n, line=dict(color=col[n], width=2.3),
                                 hovertemplate=f"%{{y:{MEASURES[measure]['fmt']}}}<extra>{n}</extra>"))
    if show_ramadan:
        ramadan_bands(fig)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title_text=MEASURES[measure]["unit"], rangemode="tozero" if measure != "Average payment" else "normal")
    show(style(fig, height, legend=len(names) > 1))


def month_index(t: pd.DataFrame, measure_: str, years: list[int]) -> pd.Series:
    t = t[t["year"].isin(years)]
    v = meas(t, measure_)
    v.index = pd.DatetimeIndex(v.index)
    rel = v / v.groupby(v.index.year).transform("mean")
    return rel.groupby(rel.index.month).mean()


# ================================================================ sidebar
with st.sidebar:
    st.markdown(f"<p style='font-size:1.08rem;font-weight:700;color:{INK};margin:0'>💸 Saudi Card Payments 🌴</p>"
                f"<p style='color:{MUTED};font-size:0.82rem;margin:0 0 0.6rem 0'>Weekly point-of-sale (card) payments, "
                f"May 2020 - July 2025. Source: KAPSARC / SAMA. Cash, transfers and online payments are not included.</p>",
                unsafe_allow_html=True)
    page = st.radio("Navigation", PAGES, label_visibility="collapsed")
    st.divider()
    st.markdown("**Filters**")
    y1, y2 = st.slider("Year range", 2020, 2025, (2021, 2024),
                       help="2020 starts in May and 2025 ends in July. 2021-2024 are the complete years.")
    measure = st.selectbox("Measure", list(MEASURES),
                           help="Spending = SAR paid. Number of payments = card payments made. Average payment = spending / payments.")
    smooth = st.checkbox("Smooth lines (4-week average)", value=False)
    show_ramadan = st.checkbox("Shade Ramadan weeks", value=True)

sel_years = list(range(y1, y2 + 1))
period = df[df["year"].between(y1, y2)]
nat_p = period[period["level"] == "national"]
full_in_sel = [y for y in FULL_YEARS if y in sel_years]
M = MEASURES[measure]


# ================================================================ shared blocks
def ranking_block(level: str, names: list[str], key: str) -> None:
    by = "sector" if level == "sector" else "city"
    card_title(f"{'Cities' if by == 'city' else 'Sectors'} ranked by {measure.lower()}", f"{y1}-{y2}" if y1 != y2 else f"{y1}")
    agg = period[period["level"] == by].groupby("name")[["value_sar_k", "transactions_k"]].sum()
    agg["Spending (bn SAR)"] = agg["value_sar_k"] / 1e6
    agg["Payments (million)"] = agg["transactions_k"] / 1e3
    agg["Average payment (SAR)"] = agg["value_sar_k"] / agg["transactions_k"]
    agg["Share of spending (%)"] = agg["value_sar_k"] / agg["value_sar_k"].sum() * 100
    colname = {"Spending": "Spending (bn SAR)", "Number of payments": "Payments (million)", "Average payment": "Average payment (SAR)"}[measure]
    rank = agg[colname].sort_values()
    col = colors_for(names, key)
    fig = go.Figure(go.Bar(x=rank.values, y=rank.index, orientation="h",
                           marker_color=[col.get(n, SOFT if names else BLUE) for n in rank.index],
                           text=[f"{v:,.1f}" if measure == "Spending" else f"{v:,.0f}" for v in rank.values],
                           textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x:,.1f}<extra></extra>"))
    fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, rank.max() * 1.15])
    fig.update_yaxes(showgrid=False)
    show(style(fig, 90 + 27 * len(rank), legend=False))
    with st.expander("All three measures (table)"):
        st.dataframe(agg[["Spending (bn SAR)", "Payments (million)", "Average payment (SAR)", "Share of spending (%)"]]
                     .sort_values(colname, ascending=False).round(1), width="stretch")


def avg_payment_block(level: str, exclude: str) -> None:
    by = "sector" if level == "sector" else "city"
    card_title(f"Average payment by {by}", f"SAR per card payment, {y1}-{y2}. Highest and lowest in orange.")
    a = period[(period["level"] == by) & (period["name"] != exclude)].groupby("name")[["value_sar_k", "transactions_k"]].sum()
    s = (a["value_sar_k"] / a["transactions_k"]).sort_values()
    fig = go.Figure(go.Bar(x=s.values, y=s.index, orientation="h", marker_color=[SERIES[1] if v in (s.min(), s.max()) else BLUE for v in s.values],
                           text=[f"{v:,.0f}" for v in s.values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,.0f} SAR<extra></extra>"))
    fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, s.max() * 1.13])
    fig.update_yaxes(showgrid=False)
    show(style(fig, 90 + 27 * len(s), legend=False))
    st.caption(f"'{exclude}' is left out because it mixes many {'cities' if by == 'city' else 'sectors'}.")


def growth_block(level: str) -> None:
    by = "sector" if level == "sector" else "city"
    card_title(f"{by.capitalize()} growth, 2021 vs 2024", "Change in average weekly spending. Fixed years, not affected by the year filter.")
    t = df[df["level"] == by]
    g = (t[t["year"] == 2024].groupby("name")["spending_bn"].mean() / t[t["year"] == 2021].groupby("name")["spending_bn"].mean() - 1) * 100
    fig = go.Figure(go.Bar(x=g.sort_values(ascending=False).index, y=g.sort_values(ascending=False).values,
                           marker_color=[UP if v >= 0 else DOWN for v in g.sort_values(ascending=False).values],
                           text=[f"{v:+.0f}%" for v in g.sort_values(ascending=False).values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}: %{y:+.1f}%<extra></extra>"))
    fig.update_yaxes(title_text="Change 2021 to 2024 (%)", zeroline=True, zerolinecolor=MUTED)
    fig.update_xaxes(tickangle=-40)
    show(style(fig, 400, legend=False))


# ================================================================ pages
def page_overview() -> None:
    header("🏠 Overview", "A high-level view of card payments in Saudi Arabia, nationally.")
    n = nat_p
    cols = st.columns(4)
    sp, py, tk = period_value(n, "Spending"), period_value(n, "Number of payments"), period_value(n, "Average payment")

    def delta(m: str):
        if len(full_in_sel) < 2:
            return None, "flat"
        a, b = full_in_sel[0], full_in_sel[-1]
        va = period_value(n[n["year"] == a], m)
        vb = period_value(n[n["year"] == b], m)
        ch = (vb / va - 1) * 100
        tone = "flat" if m == "Average payment" else ("up" if ch >= 0 else "down")
        return f"{'↑' if ch >= 0 else '↓'} {ch:+.0f}% ({b} vs {a})", tone

    with cols[0]:
        d, t = delta("Spending")
        kpi("Average weekly spending", f"{sp:.1f} bn SAR", d, t, "💰", "#dcf5ec")
    with cols[1]:
        d, t = delta("Number of payments")
        kpi("Average weekly payments", f"{py:.0f} million", d, t, "🛒", "#e1ecff")
    with cols[2]:
        d, t = delta("Average payment")
        kpi("Average payment", f"{tk:.0f} SAR", d, t, "🏷️", "#fff0d6")
    with cols[3]:
        kpi("Weeks covered", f"{n['date'].nunique()}", f"{n['date'].min():%b %Y} - {n['date'].max():%b %Y}", "flat", "📅", "#efe7fb")
    st.write("")

    a, b = st.columns([3, 2])
    with a, st.container(border=True):
        card_title(f"{measure} over time", f"Weekly, {M['unit']}." + (" Grey bands are Ramadan weeks." if show_ramadan else ""))
        line_chart("national", ["Saudi Arabia"], "ov", 380)
    with b, st.container(border=True):
        card_title(f"{measure} by year", "Average week in each year. Light bars are partial years (2020 from May, 2025 to July).")
        ys = sel_years
        vals = [period_value(n[n["year"] == y], measure) for y in ys]
        fig = go.Figure(go.Bar(x=[str(y) for y in ys], y=vals, marker_color=[BLUE if y in FULL_YEARS else SOFT for y in ys],
                               text=[f"{v:{M['fmt']}}" for v in vals], textposition="outside", cliponaxis=False,
                               hovertemplate=f"%{{x}}: %{{y:{M['fmt']}}} {M['short']}<extra></extra>"))
        fig.update_yaxes(title_text=M["unit"], rangemode="tozero")
        show(style(fig, 380, legend=False))

    c, d_ = st.columns([3, 2])
    with c, st.container(border=True):
        card_title("Which months are busier?", "Each month compared with its own year's average (1.0 = average month). Complete years in your selection.")
        if not full_in_sel:
            st.info("Select a range that includes at least one complete year (2021-2024).")
        else:
            idx = month_index(df[df["level"] == "national"], measure, full_in_sel)
            fig = go.Figure(go.Bar(x=MONTHS, y=idx.values, marker_color=[BLUE if v >= 1 else SOFT for v in idx.values],
                                   text=[f"{v:.2f}" for v in idx.values], textposition="outside", cliponaxis=False,
                                   hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
            fig.add_hline(y=1, line_dash="dot", line_color=MUTED)
            fig.update_yaxes(range=[min(idx.min() * 0.97, 0.9), idx.max() * 1.04], title_text="Compared with an average month")
            show(style(fig, 330, legend=False))
    with d_, st.container(border=True):
        card_title("What stands out", "Fixed analysis of 2021-2024. Details in Seasonal Insights.")
        nt = df[(df["level"] == "national") & df["year"].isin(FULL_YEARS)]
        yv = {y: period_value(nt[nt["year"] == y], "Spending") for y in (2021, 2024)}
        yp = {y: period_value(nt[nt["year"] == y], "Number of payments") for y in (2021, 2024)}
        yt = {y: period_value(nt[nt["year"] == y], "Average payment") for y in (2021, 2024)}
        ram = event_effect("national", None, "is_ramadan")
        sal = event_effect("national", None, "is_salary_week")
        st.markdown(
            f"<ul class='takeaway'><li>💳 <b>More, smaller payments.</b> The average week grew from {yv[2021]:.1f} to {yv[2024]:.1f} bn SAR "
            f"and from {yp[2021]:.0f} to {yp[2024]:.0f} million payments (2021 to 2024), while the average payment fell from "
            f"{yt[2021]:.0f} to {yt[2024]:.0f} SAR.</li>"
            f"<li>💰 <b>Pay cycle.</b> Weeks containing the 27th are {sal['value']:+.0f}% above the weeks around them.</li>"
            f"<li>🌙 <b>Ramadan.</b> Total spending {ram['value']:+.0f}%, payments {ram['transactions']:+.0f}%, average payment {ram['ticket']:+.0f}%: "
            f"fewer but larger payments.</li></ul>", unsafe_allow_html=True)


def page_sectors() -> None:
    header("🛍️ Sectors", "Compare card payments across 17 sectors (national level).")
    opts = sorted(df.loc[df["level"] == "sector", "name"].unique())
    with st.sidebar:
        st.markdown("**Sectors**")
        names = st.multiselect("Sectors to compare over time (max 4)", opts,
                               default=["Restaurants & Café", "Beverage and Food", "Clothing and Footwear"], max_selections=4, key="sec_names")
    a, b = st.columns(2)
    with a, st.container(border=True):
        ranking_block("sector", names, "sec")
    with b, st.container(border=True):
        card_title("Sector pattern by month", "Top 8 sectors. Each row is compared with its own yearly average, so darker = busier month for that sector.")
        if not full_in_sel:
            st.info("Select a range that includes at least one complete year (2021-2024).")
        else:
            sec = period[period["level"] == "sector"]
            top8 = sec.groupby("name")["value_sar_k"].sum().nlargest(8).index.tolist()
            z = [month_index(df[(df["level"] == "sector") & (df["name"] == s)], "Spending", full_in_sel).values for s in top8]
            fig = go.Figure(go.Heatmap(z=z, x=MONTHS, y=top8, colorscale="Greens", colorbar=dict(title="Index", thickness=12),
                                       text=[[f"{v:.2f}" for v in row] for row in z], texttemplate="%{text}", textfont=dict(size=11),
                                       hovertemplate="%{y}, %{x}: %{z:.2f}<extra></extra>"))
            fig.update_yaxes(autorange="reversed", showgrid=False)
            show(style(fig, 540, legend=False))
    c, d_ = st.columns(2)
    with c, st.container(border=True):
        growth_block("sector")
    with d_, st.container(border=True):
        avg_payment_block("sector", "Other sector")
    with st.container(border=True):
        card_title(f"{measure} of selected sectors over time", M["unit"])
        if names:
            line_chart("sector", names, "sec", 380)
        else:
            st.info("Choose at least one sector in the sidebar.")
    sec_all = df[(df["level"] == "sector") & df["year"].isin(FULL_YEARS)].groupby("name")[["value_sar_k", "transactions_k"]].sum()
    sec_all["ticket"] = sec_all["value_sar_k"] / sec_all["transactions_k"]
    named = sec_all.drop(index="Other sector")
    top4 = (sec_all["value_sar_k"] / sec_all["value_sar_k"].sum() * 100).nlargest(4).sum()
    with st.container(border=True):
        card_title("What stands out", "Fixed analysis of 2021-2024.")
        st.markdown(f"<ul class='takeaway'><li>🏆 <b>Concentrated.</b> Four sectors take {top4:.0f}% of spending.</li>"
                    f"<li>🏷️ <b>Different reasons for being big.</b> The average payment goes from {named['ticket'].min():.0f} SAR in "
                    f"{named['ticket'].idxmin()} to {named['ticket'].max():,.0f} SAR in {named['ticket'].idxmax()}: some sectors are large "
                    f"because of many small payments, others because of a few large ones.</li>"
                    f"<li>🎁 <b>Ramadan and Eid</b> change sectors in opposite ways: see Seasonal Insights.</li></ul>", unsafe_allow_html=True)


def page_cities() -> None:
    header("🏙️ Cities", "Compare card payments across 11 cities (the last group, 'Other cities', combines all remaining cities).")
    opts = sorted(df.loc[df["level"] == "city", "name"].unique())
    with st.sidebar:
        st.markdown("**Cities**")
        mode = st.radio("Comparison mode", ["Single city", "Multiple cities"], key="city_mode")
        if mode == "Single city":
            one = st.selectbox("City", opts, index=opts.index("Riyadh"), key="city_one")
            names = [one]
        else:
            names = st.multiselect("Cities to compare (max 4)", opts, default=["Riyadh", "Jeddah", "Makkah"], max_selections=4, key="city_names")
    a, b = st.columns(2)
    with a, st.container(border=True):
        ranking_block("city", names, "cty")
    with b, st.container(border=True):
        avg_payment_block("city", "Other cities")
    c, d_ = st.columns(2)
    with c, st.container(border=True):
        growth_block("city")
    with d_, st.container(border=True):
        card_title("Share of spending by city", f"{y1}-{y2}")
        agg = period[period["level"] == "city"].groupby("name")["value_sar_k"].sum()
        s = (agg / agg.sum() * 100).sort_values(ascending=False)
        fig = go.Figure(go.Bar(x=s.index, y=s.values, marker_color=BLUE, text=[f"{v:.1f}%" for v in s.values], textposition="outside",
                               cliponaxis=False, hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        fig.update_xaxes(tickangle=-40)
        fig.update_yaxes(title_text="% of national spending")
        show(style(fig, 400, legend=False))
    with st.container(border=True):
        card_title(f"{measure} of selected cities over time", M["unit"])
        if names:
            line_chart("city", names, "cty", 380)
        else:
            st.info("Choose at least one city in the sidebar.")
    cty = df[(df["level"] == "city") & df["year"].isin(FULL_YEARS)].groupby("name")[["value_sar_k", "transactions_k"]].sum()
    cty["ticket"] = cty["value_sar_k"] / cty["transactions_k"]
    cty["share"] = cty["value_sar_k"] / cty["value_sar_k"].sum() * 100
    named = cty.drop(index="Other cities")
    rk = named["ticket"].rank(ascending=False).astype(int)
    mk = event_effect("city", "Makkah", "is_ramadan")["value"]
    with st.container(border=True):
        card_title("What stands out", "Fixed analysis of 2021-2024.")
        st.markdown(f"<ul class='takeaway'><li>🏙️ <b>Riyadh and Jeddah lead.</b> Riyadh holds {cty['share']['Riyadh']:.0f}% of spending and Jeddah "
                    f"{cty['share']['Jeddah']:.0f}%.</li>"
                    f"<li>🏷️ <b>Largest market, not the largest payment.</b> The average payment is highest in {named['ticket'].idxmax()} "
                    f"({named['ticket'].max():.0f} SAR) and lowest in {named['ticket'].idxmin()} ({named['ticket'].min():.0f} SAR); Riyadh ranks "
                    f"{rk['Riyadh']} of {len(named)} ({named.loc['Riyadh', 'ticket']:.0f} SAR).</li>"
                    f"<li>🕋 <b>Makkah in Ramadan.</b> Spending rises {mk:.0f}% in Ramadan weeks although Makkah holds only "
                    f"{cty['share']['Makkah']:.0f}% of spending.</li></ul>", unsafe_allow_html=True)


def trio(e: pd.Series, labels=("Spending", "Payments", "Average payment")) -> None:
    c = st.columns(3)
    for col, lab, v in zip(c, labels, (e["value"], e["transactions"], e["ticket"])):
        color = UP if v >= 0 else DOWN
        col.markdown(f"<div class='stat'><div class='bigsub'>{lab}</div><div class='big' style='color:{color}'>{v:+.1f}%</div>"
                     f"<div class='bigsub'>vs surrounding weeks</div></div>", unsafe_allow_html=True)


def page_seasonal() -> None:
    header("🌙 Seasonal Insights", "How Ramadan, pay weeks and Eid change card spending. Fixed analysis of 2021-2024 (the year filter does not apply).")
    ev = st.radio("Event", ["Ramadan", "Pay weeks", "Eid al-Fitr", "Monthly pattern"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div class='csub'>Each event is compared with the 4 weeks before and the 4 weeks after it.</div>", unsafe_allow_html=True)

    if ev == "Ramadan":
        scope = st.radio("Scope", ["National", "By sector", "By city"], horizontal=True, key="r_scope")
        if scope == "National":
            e = event_effect("national", None, "is_ramadan")
            trio(e)
            with st.container(border=True):
                card_title("Weekly spending around Ramadan", "Index: 100 = the average of the 4 weeks before and after. Average of 2021-2024.")
                p = ramadan_profile("national", None)
                fig = go.Figure(go.Scatter(x=p["week"], y=p["index"], mode="lines+markers", line=dict(color=BLUE, width=2.6), marker=dict(size=7),
                                           hovertemplate="Week %{x}: %{y:.0f}<extra></extra>"))
                fig.add_vrect(x0=-0.5, x1=p.attrs["len"] - 0.5, fillcolor=NEUTRAL, opacity=0.3, line_width=0, layer="below")
                fig.add_hline(y=100, line_dash="dot", line_color=MUTED)
                fig.update_xaxes(title_text="Weeks from the start of Ramadan (grey = Ramadan weeks)", dtick=1)
                fig.update_yaxes(title_text="Spending index")
                show(style(fig, 360, legend=False))
        elif scope == "By sector":
            s = event_by_name("sector", "is_ramadan")
            with st.container(border=True):
                card_title("Change in spending during Ramadan, by sector", "Average of 2021-2024 vs the surrounding weeks.")
                show(change_bars(s))
            st.markdown(f"<div class='how'><b>Hypothesis 1:</b> restaurants and cafés fall {abs(s['Restaurants & Café']):.0f}% in Ramadan weeks "
                        f"(payments {event_effect('sector', 'Restaurants & Café', 'is_ramadan')['transactions']:+.0f}%), the opposite of what many expect. "
                        f"Possible reasons (not tested): meals move home, shopping happens before the month.</div>", unsafe_allow_html=True)
            ry = event_by_year("sector", "Restaurants & Café", "is_ramadan")
            with st.container(border=True):
                card_title("Restaurants and cafés, every Ramadan", "Fell in every one of the four years.")
                fig = go.Figure(go.Bar(x=ry["year"].astype(str), y=ry["value"], marker_color=DOWN, text=[f"{v:+.0f}%" for v in ry["value"]],
                                       textposition="outside", cliponaxis=False, hovertemplate="%{x}: %{y:+.1f}%<extra></extra>"))
                fig.update_yaxes(title_text="Change vs surrounding weeks (%)", range=[min(ry["value"]) * 1.3, 5])
                show(style(fig, 300, legend=False))
        else:
            s = event_by_name("city", "is_ramadan")
            with st.container(border=True):
                card_title("Change in spending during Ramadan, by city", "Average of 2021-2024 vs the surrounding weeks.")
                show(change_bars(s))
            st.markdown(f"<div class='how'><b>Hypothesis 3:</b> Makkah rises {s['Makkah']:.0f}%, Madinah {s['Madinah']:.0f}%, Jeddah {s['Jeddah']:.0f}% "
                        f"and Riyadh {s['Riyadh']:.0f}%. Consistent with Umrah and visitor spending, but the data has no visitor information.</div>",
                        unsafe_allow_html=True)

    elif ev == "Pay weeks":
        scope = st.radio("Scope", ["National", "By sector"], horizontal=True, key="p_scope")
        st.markdown("<div class='how'>A <b>pay week</b> is a week containing the 27th of the month. This is an assumption, not a verified payday.</div>",
                    unsafe_allow_html=True)
        if scope == "National":
            trio(event_effect("national", None, "is_salary_week"))
            with st.container(border=True):
                card_title("Spending across the month", "Week compared with the local level, by the day of the month the week starts (Ramadan weeks excluded).")
                cyc = pay_cycle()
                fig = go.Figure(go.Bar(x=cyc.index.astype(str), y=cyc.values, marker_color=[UP if v >= 0 else DOWN for v in cyc.values],
                                       text=[f"{v:+.0f}%" for v in cyc.values], textposition="outside", cliponaxis=False,
                                       hovertemplate="Weeks starting %{x}: %{y:+.1f}%<extra></extra>"))
                fig.update_yaxes(title_text="Compared with normal (%)", zeroline=True, zerolinecolor=MUTED)
                show(style(fig, 340, legend=False))
        else:
            s = event_by_name("sector", "is_salary_week")
            with st.container(border=True):
                card_title("Change in spending in pay weeks, by sector", "Average of 2021-2024 vs the surrounding weeks.")
                show(change_bars(s))

    elif ev == "Eid al-Fitr":
        e = eid_profile("national", None)
        c = st.columns(3)
        c[0].markdown(f"<div class='stat'><div class='bigsub'>Week before Eid, all sectors</div><div class='big' style='color:{UP}'>{e.loc[-1]:+.0f}%</div></div>", unsafe_allow_html=True)
        for col, nme in zip(c[1:], ["Clothing and Footwear", "Jewelry"]):
            v = eid_profile("sector", nme).loc[-1]
            col.markdown(f"<div class='stat'><div class='bigsub'>Week before Eid, {nme}</div><div class='big' style='color:{UP}'>{v:+.0f}%</div></div>", unsafe_allow_html=True)
        st.write("")
        kind = st.radio("Compare", ["Sectors", "Cities"], horizontal=True, key="eid_kind")
        lv = "sector" if kind == "Sectors" else "city"
        opts = sorted(df.loc[df["level"] == lv, "name"].unique())
        dflt = ["Clothing and Footwear", "Jewelry", "Restaurants & Café"] if lv == "sector" else ["Riyadh", "Jeddah", "Makkah"]
        picked = st.multiselect("Compare with the national total (up to 3)", opts, default=dflt, max_selections=3, key=f"eid_{lv}")
        with st.container(border=True):
            card_title("Spending around Eid al-Fitr", "Average of five Eids (2021-2025). 0 = the week containing Eid day.")
            fig = go.Figure(go.Scatter(x=e.index, y=e.values, name="All sectors (national)", mode="lines+markers", line=dict(color=NEUTRAL, width=3),
                                       marker=dict(size=8), hovertemplate="Week %{x}: %{y:+.0f}%<extra>National</extra>"))
            for i, nme in enumerate(picked):
                v = eid_profile(lv, nme)
                fig.add_trace(go.Scatter(x=v.index, y=v.values, name=nme, mode="lines+markers", line=dict(color=SERIES[i], width=2.6),
                                         marker=dict(size=8), hovertemplate="Week %{x}: %{y:+.0f}%<extra>" + nme + "</extra>"))
            fig.add_vline(x=0, line_dash="dot", line_color=MUTED)
            fig.add_hline(y=0, line_color=MUTED, line_width=1)
            fig.update_xaxes(title_text="Weeks relative to Eid", dtick=1)
            fig.update_yaxes(title_text="Change vs normal weeks (%)")
            show(style(fig, 400))

    else:
        with st.container(border=True):
            card_title("Typical month, year by year", "Each month compared with its own year's average (1.0 = average month), national, complete years.")
            nat = df[df["level"] == "national"]
            fig = go.Figure()
            for i, y in enumerate(FULL_YEARS):
                idx = month_index(nat, measure, [y])
                fig.add_trace(go.Scatter(x=MONTHS, y=idx.values, mode="lines+markers", name=str(y), line=dict(color=SERIES[i], width=2.4),
                                         marker=dict(size=7), hovertemplate="%{x}: %{y:.2f}<extra>" + str(y) + "</extra>"))
            fig.add_hline(y=1, line_dash="dot", line_color=MUTED)
            fig.update_yaxes(title_text="Compared with an average month")
            show(style(fig, 400))
        st.caption("The chart follows the Measure filter in the sidebar. Ramadan moves about 11 days earlier each year, so its months shift.")


def page_data() -> None:
    header("📋 Data & Methodology", "About the dataset, indicators and limitations.")
    c = st.columns(4)
    for col, (lab, val) in zip(c, [("Source", "KAPSARC Data Portal (SAMA weekly series)"), ("Period", "10 May 2020 - 6 Jul 2025 (270 weeks)"),
                                    ("Coverage", "National, 17 sectors, 11 cities"), ("Payment type", "Card payments only")]):
        col.markdown(f"<div class='stat'><div class='bigsub'>{lab}</div><div style='font-weight:650;color:{INK}'>{val}</div></div>", unsafe_allow_html=True)
    st.write("")
    with st.container(border=True):
        card_title("Data preview", "Filtered by the year range in the sidebar. Newest first.")
        lv = st.radio("Dataset", ["national", "sector", "city"], horizontal=True, format_func=lambda x: {"national": "National", "sector": "Sectors", "city": "Cities"}[x])
        view = period[period["level"] == lv].sort_values(["date", "name"], ascending=[False, True])[
            ["date", "name", "value_sar_k", "transactions_k", "avg_ticket_sar", "value_change_pct", "is_ramadan", "is_salary_week"]]
        st.caption(f"{len(view):,} rows")
        st.dataframe(view, width="stretch", height=320, hide_index=True, column_config={
            "date": st.column_config.DateColumn("Week starting", format="DD MMM YYYY"), "name": "Name",
            "value_sar_k": st.column_config.NumberColumn("Spending (thousand SAR)", format="%,.0f"),
            "transactions_k": st.column_config.NumberColumn("Payments (thousand)", format="%,.0f"),
            "avg_ticket_sar": st.column_config.NumberColumn("Average payment (SAR)", format="%.0f"),
            "value_change_pct": st.column_config.NumberColumn("Weekly change (%)", format="%.1f"),
            "is_ramadan": st.column_config.CheckboxColumn("Ramadan"), "is_salary_week": st.column_config.CheckboxColumn("Pay week")})
        st.download_button("Download filtered data (CSV)", view.to_csv(index=False).encode("utf-8"), "card_payments.csv", "text/csv")
    a, b = st.columns(2)
    with a, st.container(border=True):
        card_title("Summary statistics", "Weekly spending in billion SAR for the dataset above.")
        stats = view.assign(spending_bn=view["value_sar_k"] / 1e6).groupby("name")["spending_bn"].agg(
            ["count", "mean", "median", "min", "max", "std"]).rename(columns={"count": "weeks", "std": "std dev"})
        st.dataframe(stats.round(2), width="stretch", height=300)
    with b, st.container(border=True):
        card_title("Key indicators and notes")
        st.markdown(
            """
- **Spending:** total value of card payments (SAR). **Payments:** number of card payments. **Average payment:** total spending / total payments.
- **Three levels:** national, sector and city rows each add up to the same national total, so they are never added together.
- **Complete years:** only 2021-2024. 2020 starts in May and 2025 ends in July, so partial years are marked.
- **Limitations:** card payments only (no cash, transfers or online), nominal values (no inflation adjustment), no sector-by-city split,
  large "Other" categories, no demographics. Results are descriptive, not causal.
- **Source:** [KAPSARC dataset page](https://data.kapsarc.org/explore/dataset/point-of-sale-transactions-by-sector-and-city/).
            """)


{PAGES[0]: page_overview, PAGES[1]: page_sectors, PAGES[2]: page_cities, PAGES[3]: page_seasonal, PAGES[4]: page_data}[page]()
