import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="centered")

st.title("FPL Allocation Tool")
st.header("Enter Current Balances")

# Function to reset values
def clear_balances():
    st.session_state.tristate = 0.0
    st.session_state.customers = 0.0
    st.session_state.wells = 0.0
    st.session_state.bmo = 0.0
    st.session_state.net = 0.0

# Inputs with default values stored in session state
if "tristate" not in st.session_state:
    st.session_state.tristate = 460_000_000.00
    st.session_state.customers = 50_000_000.00
    st.session_state.wells = 100_000_000.00
    st.session_state.bmo = 100_000.00
    st.session_state.net = 0.00

tristate = st.number_input("Tristate", value=st.session_state.tristate, format="%.2f", key="tristate")
customers = st.number_input("Customer's Bank", value=st.session_state.customers, format="%.2f", key="customers")
wells = st.number_input("Wells Fargo", value=st.session_state.wells, format="%.2f", key="wells")
bmo = st.number_input("BMO", value=st.session_state.bmo, format="%.2f", key="bmo")
net = st.number_input("Net Daily Movement", value=st.session_state.net, format="%.2f", key="net")

# Clear button
if st.button("Clear Balances"):
    clear_balances()

# Allocation logic
banks = [
    {"Bank": "Tristate", "Balance": tristate, "Min": 400_000_000, "Max": 460_000_000},
    {"Bank": "Customer's", "Balance": customers, "Min": 25_000_000, "Max": 50_000_000},
    {"Bank": "Wells Fargo", "Balance": wells, "Min": 100_000, "Max": 75_000_000},
    {"Bank": "BMO", "Balance": bmo, "Min": 100_000, "Max": 100_000},
]

amounts = []
actions = []
end_balances = []

movement = net

if movement > 0:
    # Deposits
    for bank in banks:
        max_cap = bank["Max"]
        current = bank["Balance"]
        space = max_cap - current
        deposit = min(movement, max(space, 0))
        if deposit > 0:
            actions.append("Deposit")
        else:
            actions.append("No Action")
        amounts.append(deposit)
        end_balances.append(current + deposit)
        movement -= deposit
else:
    # Withdrawals
    for bank in reversed(banks):
        min_cap = bank["Min"]
        current = bank["Balance"]
        available = current - min_cap
        withdraw = min(-movement, max(available, 0))
        if withdraw > 0:
            actions.append("Withdraw")
        else:
            actions.append("No Action")
        amounts.append(-withdraw)
        end_balances.append(current - withdraw)
        movement += withdraw

    # Reverse results back to original order
    actions.reverse()
    amounts.reverse()
    end_balances.reverse()

# Create display DataFrame
df = pd.DataFrame({
    "Bank": [bank["Bank"] for bank in banks],
    "Action": actions,
    "Amount": amounts,
    "Ending Balance": end_balances,
})

# Add total row
total = df["Amount"].sum()
df.loc[len(df.index)] = ["TOTAL", "", total, ""]

# Formatting for display
def format_currency(x):
    return f"${x:,.2f}" if isinstance(x, (int, float)) else x

display_df = df.copy()
display_df["Amount"] = display_df["Amount"].apply(format_currency)
display_df["Ending Balance"] = display_df["Ending Balance"].apply(format_currency)

# Conditional formatting
def highlight_rows(row):
    color = ""
    if row["Action"] == "Withdraw":
        color = "background-color: #ffe6e6;"  # light red
    elif row["Action"] == "Deposit":
        color = "background-color: #e6ffe6;"  # light green
    elif row["Bank"] == "TOTAL":
        color = "background-color: #f0f0f0;"  # light gray
    return [color] * len(row)

# Display allocation results
st.subheader("Allocation Results")
st.dataframe(display_df.style.apply(highlight_rows, axis=1), hide_index=True)
