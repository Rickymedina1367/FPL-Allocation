from ace_tools import code_from_text

code_from_text(name="fpl_allocation_app", type="code/python", content="""import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>FPL Allocation Tool</h1>", unsafe_allow_html=True)

# Input columns and output columns side-by-side
col1, col2 = st.columns(2)

# Left column for inputs
with col1:
    st.header("Enter Current Balances")

    tristate = st.number_input("Tristate Capital", value=0.0, format="%.2f")
    customers = st.number_input("Customer's Bank", value=0.0, format="%.2f")
    wells = st.number_input("Wells Fargo", value=0.0, format="%.2f")
    bmo = st.number_input("BMO", value=0.0, format="%.2f")
    net = st.number_input("Net Daily Movement", value=0.0, format="%.2f")

# Function to allocate deposits
def allocate_deposits(net, tristate, customers, wells, bmo):
    allocations = {"Tristate": 0, "Customer's": 0, "Wells Fargo": 0, "BMO": 0}
    
    # Initial maxes
    tristate_target = 400_000_000
    customer_max = 25_000_000
    wells_max = 75_000_000

    if tristate < tristate_target:
        amount = min(net, tristate_target - tristate)
        allocations["Tristate"] += amount
        net -= amount

    if net > 0 and customers < customer_max:
        amount = min(net, customer_max - customers)
        allocations["Customer's"] += amount
        net -= amount

    if net > 0 and wells < wells_max:
        amount = min(net, wells_max - wells)
        allocations["Wells Fargo"] += amount
        net -= amount

    # Dynamic limits after all are filled
    if net > 0:
        tristate_max = 460_000_000
        if wells >= wells_max and customers >= customer_max and tristate < tristate_max:
            amount = min(net, tristate_max - tristate)
            allocations["Tristate"] += amount
            net -= amount

    if net > 0 and customers < 50_000_000:
        amount = min(net, 50_000_000 - customers)
        allocations["Customer's"] += amount
        net -= amount

    if net > 0:
        allocations["Wells Fargo"] += net
        net = 0

    return allocations

# Function to allocate withdrawals
def allocate_withdrawals(net, tristate, customers, wells, bmo):
    allocations = {"Tristate": 0, "Customer's": 0, "Wells Fargo": 0, "BMO": 0}

    if bmo > 100_000:
        amount = min(abs(net), bmo - 100_000)
        allocations["BMO"] -= amount
        net += amount

    if net < 0 and wells > 100_000:
        amount = min(abs(net), wells - 100_000)
        allocations["Wells Fargo"] -= amount
        net += amount

    if net < 0 and customers > 25_000_000:
        amount = min(abs(net), customers - 25_000_000)
        allocations["Customer's"] -= amount
        net += amount

    if net < 0:
        allocations["Tristate"] += net
        net = 0

    return allocations

# Right column for allocation results
with col2:
    st.header("Allocation Results")

    if net != 0:
        if net > 0:
            allocation = allocate_deposits(net, tristate, customers, wells, bmo)
        else:
            allocation = allocate_withdrawals(net, tristate, customers, wells, bmo)

        df = pd.DataFrame([
            {
                "Bank": "Tristate",
                "Action": "Deposit" if allocation["Tristate"] > 0 else ("Withdraw" if allocation["Tristate"] < 0 else "No Action"),
                "Amount": f"${allocation['Tristate']:,.2f}",
                "Ending Balance": f"${tristate + allocation['Tristate']:,.2f}"
            },
            {
                "Bank": "Customer's",
                "Action": "Deposit" if allocation["Customer's"] > 0 else ("Withdraw" if allocation["Customer's"] < 0 else "No Action"),
                "Amount": f"${allocation['Customer's']:,.2f}",
                "Ending Balance": f"${customers + allocation['Customer's']:,.2f}"
            },
            {
                "Bank": "Wells Fargo",
                "Action": "Deposit" if allocation["Wells Fargo"] > 0 else ("Withdraw" if allocation["Wells Fargo"] < 0 else "No Action"),
                "Amount": f"${allocation['Wells Fargo']:,.2f}",
                "Ending Balance": f"${wells + allocation['Wells Fargo']:,.2f}"
            },
            {
                "Bank": "BMO",
                "Action": "Deposit" if allocation["BMO"] > 0 else ("Withdraw" if allocation["BMO"] < 0 else "No Action"),
                "Amount": f"${allocation['BMO']:,.2f}",
                "Ending Balance": f"${bmo + allocation['BMO']:,.2f}"
            },
        ])

        total_amount = sum(allocation.values())
        df.loc[len(df.index)] = {
            "Bank": "TOTAL",
            "Action": "",
            "Amount": f"${total_amount:,.2f}",
            "Ending Balance": ""
        }

        def color_rows(row):
            if row["Action"] == "Withdraw":
                return ["background-color: #ffe6e6"] * 4
            elif row["Action"] == "Deposit":
                return ["background-color: #e6ffe6"] * 4
            elif row["Bank"] == "TOTAL":
                return ["background-color: #f2f2f2"] * 4
            return [""] * 4

        st.dataframe(df.style.apply(color_rows, axis=1), hide_index=True)
    else:
        st.markdown("_Enter a non-zero Net Daily Movement to calculate allocation._")
""")
