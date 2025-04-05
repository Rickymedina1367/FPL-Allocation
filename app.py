import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="centered")
st.title("FPL Allocation Tool")

# Valid input format (no commas, 2 decimal places)
def formatted_number_input(label, value=0.0):
    return st.number_input(label, value=value, format="%.2f")

# User inputs
st.header("Enter Current Balances")
tristate = formatted_number_input("Tristate")
customers = formatted_number_input("Customer's Bank")
wells = formatted_number_input("Wells Fargo")
bmo = formatted_number_input("BMO")
net_movement = formatted_number_input("Net Daily Movement")

# Bank details
banks = {
    "Tristate": {"balance": tristate, "target": 400_000_000, "max": 460_000_000},
    "Customer's": {"balance": customers, "target": 25_000_000, "max": 50_000_000},
    "Wells Fargo": {"balance": wells, "target": 75_000_000, "max": float('inf')},
    "BMO": {"balance": bmo, "target": 100_000, "max": 100_000},
}

# Allocation priorities
deposit_order = ["Tristate", "Customer's", "Wells Fargo", "Tristate", "Customer's", "Wells Fargo"]
withdraw_order = ["BMO", "Wells Fargo", "Customer's", "Tristate"]

# Initialize result structure
results = {bank: {"action": "No Action", "amount": 0.0, "ending": banks[bank]["balance"]} for bank in banks}
movement = net_movement

# Allocation logic
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
        if bank == "Tristate":
            pull = min(abs(movement), current)
        else:
            pull = min(abs(movement), max(current - floor, 0))
        if pull > 0:
            results[bank]["action"] = "Withdraw"
            results[bank]["amount"] -= pull
