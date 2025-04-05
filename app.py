import streamlit as st
import pandas as pd

st.set_page_config(page_title="FPL Allocation Tool", layout="wide")

# Initialize session state defaults
if "tristate" not in st.session_state:
    st.session_state.tristate = 0.0
    st.session_state.customers = 0.0
    st.session_state.wells = 0.0
    st.session_state.bmo = 0.0
    st.session_state.net = 0.0

# Title
st.title("FPL Allocation Tool")

# Layout using columns
col1, col2 = st.columns(2)

with col1:
    st.header("Enter Current Balances")

    st.markdown("#### Tristate Capital")
    tristate = st.number_input("", key="tristate", value=st.session_state.tristate, format="%.2f")

    st.markdown("#### Customer's Bank")
    customers = st.number_input("", key="customers", value=st.session_state.customers, format="%.2f")

    st.markdown("#### Wells Fargo")
    wells = st.number_input("", key="wells", value=st.session_state.wells, format="%.2f")

    st.markdown("#### BMO")
    bmo = st.number_input("", key="bmo", value=st.session_state.bmo, format="%.2f")

    st.markdown("#### Net Daily Movement")
    net = st.number_input("", key="net", value=st.session_state.net, format="%.2f")

# Allocation logic
actions = []
amounts = []
end_balances = []
banks = ["Tristate", "Customer's", "Wells Fargo", "BMO"]
balances = [tristate, customers, wells, bmo]

if net != 0:
    remaining = net
    result = [0, 0, 0, 0]  # Movement per bank

    if net > 0:
        # Deposit logic
        targets = [400_000_000, 25_000_000, 75_000_000, 0]  # Initial deposit caps
        max_caps = [460_000_000, 50_000_000, float("inf"), 0]  # After others are met

        # Step 1: Tristate to 400MM
        if tristate < 400_000_000:
            to_add = min(400_000_000 - tristate, remaining)
            result[0] += to_add
            remaining -= to_add

        # Step 2: Customer's to 25MM
        if customers < 25_000_000:
            to_add = min(25_000_000 - customers, remaining)
            result[1] += to_add
            remaining -= to_add

        # Step 3: Wells to 75MM
        if wells < 75_000_000:
            to_add = min(75_000_000 - wells, remaining)
            result[2] += to_add
            remaining -= to_add

        # Step 4: Tristate to 460MM
        if tristate >= 400_000_000 and remaining > 0:
            to_add = min(460_000_000 - (tristate + result[0]), remaining)
            result[0] += to_add
            remaining -= to_add

        # Step 5: Customer's to 50MM
        if customers >= 25_000_000 and remaining > 0:
            to_add = min(50_000_000 - (customers + result[1]), remaining)
            result[1] += to_add
            remaining -= to_add

        # Step 6: Wells beyond 75MM
        if remaining > 0:
            result[2] += remaining
            remaining = 0

    else:
        # Withdraw logic
        remaining = abs(net)

        # Step 1: BMO to 100K
        bmo_pull = min(bmo - 100_000, remaining)
        result[3] -= bmo_pull
        remaining -= bmo_pull

        # Step 2: Wells to 100K
        wells_pull = min(wells - 100_000, remaining)
        result[2] -= wells_pull
        remaining -= wells_pull

        # Step 3: Customer's to 25MM
        cust_pull = min(customers - 25_000_000, remaining)
        result[1] -= cust_pull
        remaining -= cust_pull

        # Step 4: Tristate no floor
        result[0] -= remaining

    # Build action, amount, ending balance
    for i in range(4):
        amt = result[i]
        bal = balances[i] + amt
        if amt > 0:
            act = "Deposit"
        elif amt < 0:
            act = "Withdraw"
        else:
            act = "No Action"
        actions.append(act)
        amounts.append(amt)
        end_balances.append(bal)

    # Prepare table
    df = pd.DataFrame({
        "Bank": banks,
        "Action": actions,
        "Amount": amounts,
        "Ending Balance": end_balances
    })

    total = sum(amounts)
    df.loc[len(df.index)] = ["TOTAL", "", total, ""]

    # Format numbers and highlight
    def highlight(row):
        color = "background-color: #d1ffd6" if row["Action"] == "Deposit" else ("background-color: #ffd6d6" if row["Action"] == "Withdraw" else "")
        return [color] * len(row)

    df["Amount"] = df["Amount"].apply(lambda x: f"${x:,.2f}")
    df["Ending Balance"] = df["Ending Balance"].apply(lambda x: f"${x:,.2f}" if x != "" else "")

    with col2:
        st.header("Allocation Results")
        st.dataframe(df.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

        # Summary callout
        if net > 0:
            st.success(f"Depositing a total of ${total:,.2f} across banks.")
        elif net < 0:
            st.error(f"Withdrawing a total of ${abs(total):,.2f} across banks.")
        else:
            st.info("No movement required today.")
