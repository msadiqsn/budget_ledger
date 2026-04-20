import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# 🔌 SUPABASE CONNECTION
# -----------------------------
SUPABASE_URL =  "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY =  "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# 💾 SAVE FUNCTION
# -----------------------------
def save_to_db(month, fixed, variable, investment, total):
    supabase.table("budget").insert({
        "month": month,
        "fixed_total": fixed,
        "variable_total": variable,
        "investment_total": investment,
        "grand_total": total
    }).execute()

# -----------------------------
# 📥 LOAD FUNCTION
# -----------------------------
def load_data():
    response = supabase.table("budget").select("*").execute()
    return response.data

# -----------------------------
# 🧱 UI START
# -----------------------------
st.set_page_config(page_title="Budget Tracker", layout="centered")

st.title("💼 Monthly Budget Tracker")

month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# FIXED EXPENSES
# -----------------------------
st.header("Fixed Expenses")

fixed_expenses = {
    "Home Rent": 16000,
    "WiFi": 1000,
    "Abba": 10000,
    "Loan": 10000,
    "Ammi": 3000,
    "Maid Aunty": 3000
}

fixed_total = 0

for item, amount in fixed_expenses.items():
    paid = st.checkbox(f"{item} (₹{amount})")
    if paid:
        fixed_total += amount

st.write(f"Total Fixed Paid: ₹{fixed_total}")

# -----------------------------
# VARIABLE EXPENSES
# -----------------------------
st.header("Variable Expenses")

variable_budget = {
    "Groceries": 9000,
    "Electricity": 1000,
    "Outside Food": 5000,
    "Miscellaneous": 7000
}

variable_total = 0

for item, budget in variable_budget.items():
    actual = st.number_input(f"{item} (Budget ₹{budget})", min_value=0, step=100)
    variable_total += actual

    diff = actual - budget
    if diff > 0:
        st.error(f"{item}: +₹{diff} extra")
    elif diff < 0:
        st.success(f"{item}: ₹{abs(diff)} saved")
    else:
        st.info(f"{item}: exact")

st.write(f"Total Variable: ₹{variable_total}")

# -----------------------------
# INVESTMENTS
# -----------------------------
st.header("Investments")

investments = {
    "Bissi": 10000,
    "SIP": 50000
}

investment_total = 0

for item, amount in investments.items():
    done = st.checkbox(f"{item} (₹{amount})")
    if done:
        investment_total += amount

st.write(f"Total Investment: ₹{investment_total}")

# -----------------------------
# SUMMARY
# -----------------------------
st.header("Summary")

grand_total = fixed_total + variable_total + investment_total

st.metric("Grand Total", f"₹{grand_total}")

# -----------------------------
# SAVE BUTTON
# -----------------------------
if st.button("💾 Save Month Data"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total)
    st.success("Saved permanently in database!")

# -----------------------------
# HISTORY + CHARTS
# -----------------------------
st.header("History & Insights")

data = load_data()

if data:
    df = pd.DataFrame(data)

    st.subheader("📅 Data Table")
    st.dataframe(df)

    # Trend chart
    st.subheader("📈 Monthly Spending Trend")
    df_sorted = df.sort_values("created_at")
    st.line_chart(df_sorted.set_index("month")["grand_total"])

    # Bar chart
    st.subheader("📊 Category Comparison")
    st.bar_chart(df_sorted[["fixed_total", "variable_total", "investment_total"]])

    # Pie chart (latest month)
    st.subheader("🥧 Latest Month Breakdown")

    latest = df_sorted.iloc[-1]

    labels = ["Fixed", "Variable", "Investment"]
    values = [
        latest["fixed_total"],
        latest["variable_total"],
        latest["investment_total"]
    ]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    st.pyplot(fig)

# -----------------------------
# SMART INSIGHTS
# -----------------------------
st.subheader("💡 Insights")

if variable_total > 22000:
    st.warning("⚠️ You are overspending on variable expenses")

if variable_total < 20000:
    st.success("✅ Good control on expenses")

if investment_total < 60000:
    st.error("❌ Investment target not met")

if investment_total >= 60000:
    st.success("🎯 Investment goal achieved")