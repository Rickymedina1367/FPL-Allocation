import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="wide")

st.title("FPL Allocation Tool")

st.markdown("""
    <style>
    html, body, div, input, label {
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Split layout into two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Enter Current Balances")
    tristate = st.number_input("Tristate", value=0.00, step=1.0)
    customers = st.number_input("Customer's Bank", value=0.00, step=1.0)
    wells = st.number_input("Wells Fargo", value=0.00, step=1.0)
    bmo = st.number_input("BMO", value=100000.00, step=1.0)
    net = st.number_input("Net Daily Movement", value=0.00, step=1.0)

banks = ["Tristate", "Customer's", "Wells Fargo", "BMO"]
balances = [tristate, customers, wells, bmo]
actions = []
amounts = []
ending_balances = []

remaining = net

if net < 0:
    # Reverse banks and balances for withdrawal priority
    reversed_banks = banks[::-1]
    reversed_balances = balances[::-1]
    targets = [100_000, 100_000, 25_000_000, -float("inf")]

    for i, (bank, balance, target) in enumerate(zip(reversed_banks, reversed_balances, targets)):
        available = balance - target
        take = min(-remaining, available)
        take = max(0, take)
        actions.insert(0, "Withdraw" if take > 0 else "No Action")
        amounts.insert(0, -take)
        ending_balances.insert(0, balance - take)
        remaining += take
        if remaining >= 0:
            break

    # Fill in remaining rows with No Action (correctly aligned)
    while len(actions) < 4:
        i = 4 - len(actions) - 1
        actions.insert(0, "No Action")
        amounts.insert(0, 0.0)
        ending_balances.insert(0, balances[i])
else:
    # Deposit logic
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

# Create DataFrame
with col2:
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
