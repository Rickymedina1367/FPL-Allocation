import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="centered")

st.title("FPL Allocation Tool")
st.header("Enter Current Balances")

# Input fields
tristate = st.number_input("Tristate", value=460_000_000.00, step=1.0)
customers = st.number_input("Customer's Bank", value=50_000_000.00, step=1.0)
wells = st.number_input("Wells Fargo", value=100_000_000.00, step=1.0)
bmo = st.number_input("BMO", value=100_000.00, step=1.0)
net = st.number_input("Net Daily Movement", value=0.00, step=1.0)

banks = ["Tristate", "Customer's", "Wells Fargo", "BMO"]
balances = [tristate, customers, wells, bmo]
actions = []
amounts = []
ending_balances = []

remaining = net

if net < 0:
    # Withdrawals: BMO → Wells → Customers → Tristate
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
    # Fill in remaining with No Action
    while len(actions) < 4:
        actions.insert(0, "No Action")
        amounts.insert(0, 0.0)
        ending_balances.insert(0, balances[3 - len(actions)])
else:
    # Deposits: Tristate → Customer’s (25MM limit initially) → Wells (75MM) → Tristate again (up to 460MM) → Customer’s (up to 50MM)
    initial_targets = [400_000_000, 25_000_000, 75_000_000]
    later_targets = [460_000_000, 50_000_000]
    deposits = [0, 0, 0, 0]

    # Step 1: Tristate up to 400MM
    if tristate < 400_000_000:
        d = min(400_000_000 - tristate, remaining)
        deposits[0] += d
        remaining -= d

    # Step 2: Customer’s up to 25MM
    if customers < 25_000_000 and remaining > 0:
        d = min(25_000_000 - customers, remaining)
        deposits[1] += d
        remaining -= d

    # Step 3: Wells up to 75MM
    if wells < 75_000_000 and remaining > 0:
        d = min(75_000_000 - wells, remaining)
        deposits[2] += d
        remaining -= d

    # Step 4: Tristate up to 460MM
    if tristate + deposits[0] < 460_000_000 and remaining > 0:
        d = min(460_000_000 - (tristate + deposits[0]), remaining)
        deposits[0] += d
        remaining -= d

    # Step 5: Customer’s up to 50MM
    if customers + deposits[1] < 50_000_000 and remaining > 0:
        d = min(50_000_000 - (customers + deposits[1]), remaining)
        deposits[1] += d
        remaining -= d

    # Step 6: Wells above 75MM
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

# Format and display
df = pd.DataFrame({
    "Bank": banks,
    "Action": actions,
    "Amount": [f"${x:,.2f}" for x in amounts],
    "Ending Balance": [f"${x:,.2f}" for x in ending_balances],
})

# Add TOTAL row
total_amount = sum(amounts)
df.loc[len(df.index)] = {
    "Bank": "TOTAL",
    "Action": "",
    "Amount": f"${total_amount:,.2f}",
    "Ending Balance": ""
}

# Color rows based on action
def highlight_rows(row):
    if row["Action"] == "Deposit":
        return ["background-color: #d4f8d4"] * len(row)
    elif row["Action"] == "Withdraw":
        return ["background-color: #f8d4d4"] * len(row)
    elif row["Bank"] == "TOTAL":
        return ["background-color: #e0e0e0"] * len(row)
    else:
        return [""] * len(row)

st.markdown("### Allocation Results")
st.dataframe(df.style.apply(highlight_rows, axis=1), hide_index=True)
