import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="wide")
st.title("FPL Allocation Tool")

# --- Input Formatting Logic ---
with st.form("fpl_form"):
    st.header("Enter Current Balances")

    raw_tristate = st.text_input("Tristate", value=st.session_state.get("tristate_display", "0"))
    raw_customers = st.text_input("Customer's Bank", value=st.session_state.get("customers_display", "0"))
    raw_wells = st.text_input("Wells Fargo", value=st.session_state.get("wells_display", "0"))
    raw_bmo = st.text_input("BMO", value=st.session_state.get("bmo_display", "0"))
    raw_net = st.text_input("Net Daily Movement", value=st.session_state.get("net_display", "0"))

    submitted = st.form_submit_button("Confirm Inputs")

def parse_and_format(raw, key):
    try:
        cleaned = raw.replace(",", "").strip()
        amount = float(cleaned)
        formatted = f"{amount:,.2f}"
        st.session_state[f"{key}_display"] = formatted
        return amount
    except:
        return 0.0

if submitted:
    tristate = parse_and_format(raw_tristate, "tristate")
    customers = parse_and_format(raw_customers, "customers")
    wells = parse_and_format(raw_wells, "wells")
    bmo = parse_and_format(raw_bmo, "bmo")
    net = parse_and_format(raw_net, "net")
else:
    # Initial load fallback
    tristate = float(raw_tristate.replace(",", "") or 0)
    customers = float(raw_customers.replace(",", "") or 0)
    wells = float(raw_wells.replace(",", "") or 0)
    bmo = float(raw_bmo.replace(",", "") or 0)
    net = float(raw_net.replace(",", "") or 0)

# --- Allocation Logic ---
banks = ["Tristate", "Customer's", "Wells Fargo", "BMO"]
balances = [tristate, customers, wells, bmo]
actions = []
amounts = []
ending_balances = []

remaining = net

if net < 0:
    targets = [100_000, 100_000, 25_000_000, -float("inf")]
    for i, (bank, balance, target) in enumerate(zip(banks[::-1], balances[::-1], targets)):
        available = balance - target
        take = min(-remaining, available)
        take = max(0, take)
        actions.insert(0, "Withdraw")
        amounts.insert(0, -take)
        ending_balances.insert(0, balance - take)
        remaining += take
        if remaining >= 0:
            break
    while len(actions) < 4:
        actions.insert(0, "No Action")
        amounts.insert(0, 0.0)
        ending_balances.insert(0, balances[3 - len(actions)])
else:
    initial_targets = [400_000_000, 25_000_000, 75_000_000]
    deposits = [0, 0, 0, 0]

    if tristate < 400_000_000:
        d = min(400_000_000 - tristate, remaining)
        deposits[0] += d
        remaining -= d

    if customers < 25_000_000 and remaining > 0:
        d = min(25_000_000 - customers, remaining)
        deposits[1] += d
        remaining -= d

    if wells < 75_000_000 and remaining > 0:
        d = min(75_000_000 - wells, remaining)
        deposits[2] += d
        remaining -= d

    if tristate + deposits[0] < 460_000_000 and remaining > 0:
        d = min(460_000_000 - (tristate + deposits[0]), remaining)
        deposits[0] += d
        remaining -= d

    if customers + deposits[1] < 50_000_000 and remaining > 0:
        d = min(50_000_000 - (customers + deposits[1]), remaining)
        deposits[1] += d
        remaining -= d

    if remaining > 0:
        deposits[2] += remaining
        remaining = 0

    for i, d in enumerate(deposits):
        if d > 0:
            actions.append("Deposit")
            amounts.append(d)
            ending_balances.append(balances[i] + d)
        else:
            actions.append("No Action")
            amounts.append(0.0)
            ending_balances.append(balances[i])

# --- Output Allocation Results ---
st.markdown("### Allocation Results")
df = pd.DataFrame({
    "Bank": banks,
    "Action": actions,
    "Amount": [f"${x:,.2f}" for x in amounts],
    "Ending Balance": [f"${x:,.2f}" for x in ending_balances],
})

total_amount = sum(amounts)
df.loc[len(df.index)] = {
    "Bank": "TOTAL",
    "Action": "",
    "Amount": f"${total_amount:,.2f}",
    "Ending Balance": ""
}

def highlight_rows(row):
    if row["Action"] == "Deposit":
        return ["background-color: #d4f8d4"] * len(row)
    elif row["Action"] == "Withdraw":
        return ["background-color: #f8d4d4"] * len(row)
    elif row["Bank"] == "TOTAL":
        return ["background-color: #e0e0e0"] * len(row)
    else:
        return [""] * len(row)

st.dataframe(df.style.apply(highlight_rows, axis=1), hide_index=True, use_container_width=True)
