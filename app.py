import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="centered")
st.title("FPL Allocation Tool")

# --- Clear state ---
if "clear" not in st.session_state:
    st.session_state.clear = False

if st.button("Clear Balances"):
    st.session_state.clear = True
else:
    st.session_state.clear = False

# --- Input fields ---
def formatted_number_input(label, key, default=0.0):
    return st.number_input(label, value=0.0 if st.session_state.clear else default, format="%.2f", key=key)

st.header("Enter Current Balances")
tristate = formatted_number_input("Tristate", "tristate")
customers = formatted_number_input("Customer's Bank", "customers")
wells = formatted_number_input("Wells Fargo", "wells")
bmo = formatted_number_input("BMO", "bmo")
net_movement = formatted_number_input("Net Daily Movement", "net_movement")

# --- Logic ---
results = {}

# --- Deposits ---
if net_movement > 0:
    banks = {
        "Tristate": {"balance": tristate, "target": 400_000_000, "max": 460_000_000},
        "Customer's": {"balance": customers, "target": 25_000_000, "max": 50_000_000},
        "Wells Fargo": {"balance": wells, "target": 75_000_000, "max": float('inf')},
    }
    deposit_order = ["Tristate", "Customer's", "Wells Fargo", "Tristate", "Customer's", "Wells Fargo"]
    results = {bank: {"action": "No Action", "amount": 0.0, "ending": banks[bank]["balance"]} for bank in banks}
    results["BMO"] = {"action": "No Action", "amount": 0.0, "ending": bmo}
    movement = net_movement

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

# --- Withdrawals ---
elif net_movement < 0:
    movement = -net_movement

    withdraw_bmo = min(movement, max(0, bmo - 100_000))
    movement -= withdraw_bmo

    withdraw_wells = min(movement, max(0, wells - 100_000))
    movement -= withdraw_wells

    withdraw_customers = min(movement, max(0, customers - 25_000_000))
    movement -= withdraw_customers

    withdraw_tristate = movement

    results = {
        "Tristate": {
            "action": "Withdraw" if withdraw_tristate > 0 else "No Action",
            "amount": -withdraw_tristate,
            "ending": tristate - withdraw_tristate
        },
        "Customer's": {
            "action": "Withdraw" if withdraw_customers > 0 else "No Action",
            "amount": -withdraw_customers,
            "ending": customers - withdraw_customers
        },
        "Wells Fargo": {
            "action": "Withdraw" if withdraw_wells > 0 else "No Action",
            "amount": -withdraw_wells,
            "ending": wells - withdraw_wells
        },
        "BMO": {
            "action": "Withdraw" if withdraw_bmo > 0 else "No Action",
            "amount": -withdraw_bmo,
            "ending": bmo - withdraw_bmo
        },
    }

# --- Display Results ---
if results:
    df = pd.DataFrame([
        {
            "Bank": bank,
            "Action": results[bank]["action"],
            "Amount": results[bank]["amount"],
            "Ending Balance": results[bank]["ending"]
        }
        for bank in results
    ])

    total_movement = df["Amount"].sum()
    df.loc[len(df)] = {
        "Bank": "TOTAL",
        "Action": "",
        "Amount": total_movement,
        "Ending Balance": ""
    }

    df["Amount"] = df["Amount"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
    df["Ending Balance"] = df["Ending Balance"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)

    def highlight_action(row):
        if row["Action"] == "Withdraw":
            return ["background-color: #ffe6e6"] * 4
        elif row["Action"] == "Deposit":
            return ["background-color: #e6ffe6"] * 4
        elif row["Bank"] == "TOTAL":
            return ["background-color: #f0f0f0; font-weight: bold"] * 4
        return [""] * 4

    st.header("Allocation Results")
    st.dataframe(df.style.apply(highlight_action, axis=1), use_container_width=True)
else:
    st.info("No allocations necessary for today's movement.")
