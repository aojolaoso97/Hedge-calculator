import streamlit as st

st.set_page_config(
    page_title="Prop Firm Hedge Cost Calculator",
    page_icon="📊",
    layout="centered"
)

st.title("Prop Firm Hedge Cost Calculator")
st.caption("Calculates hedge TP/SL by day and the total worst-case cost.")

with st.sidebar:
    st.header("Inputs")
    cost_per_account = st.number_input(
        "Cost per account ($)",
        min_value=0.0,
        value=182.0,
        step=1.0
    )
    num_accounts = st.number_input(
        "Number of accounts",
        min_value=1,
        value=5,
        step=1
    )
    drawdown = st.number_input(
        "Drawdown / SL ($)",
        min_value=0.01,
        value=2000.0,
        step=100.0
    )
    target = st.number_input(
        "Profit target / TP ($)",
        min_value=0.01,
        value=3000.0,
        step=100.0
    )
    consistency = st.selectbox(
        "Consistency rule",
        options=["40%", "50%", "0%"],
        index=0
    )

initial_cost = cost_per_account * num_accounts

def money(x):
    return f"${x:,.2f}"

def pct(x):
    return f"{x * 100:.2f}%"

# Profit allocation logic agreed in the conversation
if consistency == "40%":
    day_shares = [0.20, 0.40, 0.40]
elif consistency == "50%":
    day_shares = [0.50, 0.50]
else:  # 0% consistency
    day_shares = [1.00]

rows = []
prior_hedge_losses = 0.0

for i, share in enumerate(day_shares, start=1):
    prop_profit_for_day = target * share
    sl_ratio = prop_profit_for_day / drawdown

    # Each new hedge TP recovers the original account cost plus ALL prior hedge losses
    hedge_tp = initial_cost + prior_hedge_losses
    hedge_sl = hedge_tp * sl_ratio

    rows.append({
        "day": i,
        "share": share,
        "prop_profit": prop_profit_for_day,
        "sl_ratio": sl_ratio,
        "hedge_tp": hedge_tp,
        "hedge_sl": hedge_sl,
    })

    prior_hedge_losses += hedge_sl

total_hedge_losses = sum(r["hedge_sl"] for r in rows)
total_cost = initial_cost + total_hedge_losses

st.subheader("Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Initial Account Cost", money(initial_cost))
c2.metric("Total Hedge Losses", money(total_hedge_losses))
c3.metric("Total Worst-Case Cost", money(total_cost))

st.divider()
st.subheader("Hedge Plan")

for r in rows:
    st.markdown(f"### Day {r['day']}")
    a, b = st.columns(2)
    a.metric("Hedge TP", money(r["hedge_tp"]))
    b.metric("Hedge SL", money(r["hedge_sl"]))
    st.caption(
        f"Prop profit allocation: {r['share']*100:.0f}% of target = {money(r['prop_profit'])} "
        f"• Hedge SL ratio = {money(r['prop_profit'])} ÷ {money(drawdown)} = {pct(r['sl_ratio'])}"
    )

st.divider()
st.subheader("Calculation Breakdown")

for r in rows:
    st.write(
        f"**Day {r['day']}:** "
        f"TP {money(r['hedge_tp'])} | "
        f"SL {money(r['hedge_sl'])} | "
        f"SL ratio {pct(r['sl_ratio'])}"
    )

st.success(f"Total worst-case cost: {money(total_cost)}")

st.caption(
    "Logic: each new hedge TP = original total account cost + all previous hedge SL losses."
)
