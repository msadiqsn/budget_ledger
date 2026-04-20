import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL =  "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY =  "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# FUNCTIONS
# -----------------------------
def save_to_db(month, fixed, variable, investment, total, var_data):
    supabase.table("budget").insert({
        "month": month,
        "fixed_total": fixed,
        "variable_total": variable,
        "investment_total": investment,
        "grand_total": total,
        "groceries": var_data["Groceries"],
        "electricity": var_data["Electricity"],
        "outside_food": var_data["Outside Food"],
        "miscellaneous": var_data["Miscellaneous"]
    }).execute()

def load_data():
    return supabase.table("budget").select("*").execute().data

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Budget Dashboard")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# FIXED INPUT (NOW EDITABLE)
# -----------------------------
st.subheader("🏠 Fixed Expenses")

rent = st.number_input("Rent", value=16000, step=500)
abba = st.number_input("Abba", value=10000, step=500)
loan = st.number_input("Loan", value=10000, step=500)
ammi = st.number_input("Ammi", value=3000, step=500)
maid = st.number_input("Maid", value=3000, step=500)

fixed_total = rent + abba + loan + ammi + maid

# -----------------------------
# VARIABLE (WiFi merged)
# -----------------------------
st.subheader("📊 Variable Expenses")

groceries = st.number_input("Groceries", value=9000, step=500)
electricity = st.number_input("Electricity + WiFi", value=2000, step=500)
outside = st.number_input("Outside Food", value=5000, step=500)
misc = st.number_input("Miscellaneous", value=7000, step=500)

variable_total = groceries + electricity + outside + misc

var_data = {
    "Groceries": groceries,
    "Electricity": electricity,
    "Outside Food": outside,
    "Miscellaneous": misc
}

# -----------------------------
# INVESTMENT
# -----------------------------
st.subheader("📈 Investments")

bissi = st.number_input("Bissi", value=10000, step=500)
sip = st.number_input("SIP", value=50000, step=500)

investment_total = bissi + sip

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total

st.metric("Total Monthly Spend", f"₹{grand_total}")

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save Month"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved successfully")

# -----------------------------
# LOAD DATA
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    st.subheader("📊 Multi-Line Trend")

    # MULTI LINE CHART
    fig, ax = plt.subplots()

    ax.plot(df["month"], df["grand_total"], label="Total")
    ax.plot(df["month"], df["fixed_total"], label="Fixed")
    ax.plot(df["month"], df["variable_total"], label="Variable")
    ax.plot(df["month"], df["investment_total"], label="Investment")

    ax.legend()
    ax.set_xticklabels(df["month"], rotation=45)

    st.pyplot(fig)

    # -----------------------------
    # SMART INSIGHTS
    # -----------------------------
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    st.subheader("🤖 Insights")

    text = ""

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            text += f"📈 Spending increased ₹{int(diff)}. "
        else:
            text += f"📉 You saved ₹{int(abs(diff))}. "

    # Overspend logic
    budget = {
        "Groceries": 9000,
        "Electricity": 2000,
        "Outside Food": 5000,
        "Miscellaneous": 7000
    }

    overspend = {}
    for k,v in budget.items():
        col = k.lower().replace(" ","_")
        if latest[col] > v:
            overspend[k] = latest[col] - v

    if overspend:
        worst = max(overspend, key=overspend.get)
        text += f"🚨 Main issue: {worst}. "

        total_waste = sum(overspend.values())
        text += f"Save ₹{int(total_waste)}/month."

    st.info(text)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.subheader("🎯 Action Plan")
        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")