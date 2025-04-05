import streamlit as st

st.title("FPL Allocation Tool")

# User inputs
st.header("Enter Current Balances")
tristate = st.number_input("Tristate", value=0.0)
customers = st.number_input("Customer's Bank", value=0.0)
wells = st.number_input("Wells Fargo", value=0.0)
bmo = st.number_input("BMO", value=0.0)
net_movement = st.number_input("Net Daily Movement", value=0.0)

# Allocation logic
banks = {
    "Tristate": {"balance": tristate, "target": 400_000_000, "max": 460_000_000},
    "Customer's": {"balance": customers, "target": 25_000_000, "max": 50_000_000},
    "Wells Fargo": {"balance": wells, "target": 75_000_000, "max": float('inf')},
    "BMO": {"balance": bmo, "target": 100_000, "max": 100_000},
}

deposit_order = ["Tristate", "Customer's", "Wells Fargo", "Tristate", "Customer's", "Wells Fargo"]
withdraw_order = ["BMO", "Customer's", "Tristate", "Wells Fargo"]

results = {bank: {"action": "No Action", "amount": 0.0, "ending": banks[bank]["balance"]} for bank in banks}
movement = net_movement

if movement > 0:
    for bank in deposit_order:
        current = results[bank]["ending"]
        cap = banks[bank]["target"] if current < banks[bank]["target"] else banks[bank]["max"]
        room = cap - current
        move = min(movement, room)
        if move > 0:
            results[bank]["action"] = "Deposit"
            results[bank]["amount"] += move
            results[bank]["ending"] += move
            movement -= move
        if movement <= 0:
            break
elif movement < 0:
    for bank in withdraw_order:
        current = results[bank]["ending"]
        floor = banks[bank]["target"]
        pull = min(abs(movement), current - floor)
        if pull > 0:
            results[bank]["action"] = "Withdraw"
            results[bank]["amount"] -= pull
            results[bank]["ending"] -= pull
            movement += pull
        if movement >= 0:
            break

# Display Results
st.header("Allocation Results")
st.table([
    {
        "Bank": bank,
        "Action": results[bank]["action"],
        "Amount": f"${results[bank]['amount']:,.2f}",
        "Ending Balance": f"${results[bank]['ending']:,.2f}"
    }
    for bank in results
])
