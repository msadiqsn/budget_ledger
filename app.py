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
# MODERN STYLE
# -----------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #eef2f7 0%, #ffffff 100%);
}

.header {
    background: linear-gradient(135deg, #4A90E2, #6FC3FF);
    padding: 18px;
    border-radius: 16px;
    color: white;
    margin-bottom: 15px;
}

.card {
    background: white;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.section-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 8px;
}

.ref {
    font-size: 12px;
    color: #888;
    margin-bottom: 4px;
}

.total-box {
    text-align:center;
    padding:16px;
    border-radius:16px;
    background: linear-gradient(135deg, #E8F5E9, #D0F0D8);
    font-weight:bold;
    font-size:20px;
}

button {
    width:100%;
    height:50px;
    border-radius:12px;
    font-size:16px;
}
</style>
""", unsafe_allow_html=True)

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
# HEADER (MODERN)
# -----------------------------
st.markdown('<div class="header">💰 Monthly Budget</div>', unsafe_allow_html=True)

month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# INPUT SECTIONS
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏠 Fixed Expenses</div>', unsafe_allow_html=True)

rent = st.number_input("Rent", value=16000)
abba = st.number_input("Abba", value=10000)
loan = st.number_input("Loan", value=10000)
ammi = st.number_input("Ammi", value=3000)
maid = st.number_input("Maid", value=3000)

fixed_total = rent + abba + loan + ammi + maid
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 Variable Expenses</div>', unsafe_allow_html=True)

groceries = st.number_input("Groceries (₹9000 ref)", value=9000)
electricity = st.number_input("Electricity + WiFi (₹2000 ref)", value=2000)
outside = st.number_input("Outside Food (₹5000 ref)", value=5000)
misc = st.number_input("Miscellaneous (₹7000 ref)", value=7000)

variable_total = groceries + electricity + outside + misc

var_data = {
    "Groceries": groceries,
    "Electricity": electricity,
    "Outside Food": outside,
    "Miscellaneous": misc
}

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 Investments</div>', unsafe_allow_html=True)

bissi = st.number_input("Bissi", value=10000)
sip = st.number_input("SIP", value=50000)

investment_total = bissi + sip
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total

st.markdown(f'<div class="total-box">Total: ₹{grand_total}</div>', unsafe_allow_html=True)

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save Month Data"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved")

# -----------------------------
# LOAD DATA
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📈 Spending Trend")

    fig, ax = plt.subplots()

    ax.plot(df["month"], df["grand_total"], linewidth=3, label="Total")
    ax.plot(df["month"], df["variable_total"], linewidth=2, label="Variable")
    ax.plot(df["month"], df["fixed_total"], linestyle="--", label="Fixed")

    ax.legend()
    ax.grid(alpha=0.2)

    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # INSIGHTS
    # -----------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🤖 Smart Insight")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    text = ""

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        text += f"{'Increased' if diff>0 else 'Saved'} ₹{abs(int(diff))}. "

    if latest["variable_total"] > 22000:
        text += "Variable spending is high. "

    st.write(text)
    st.markdown('</div>', unsafe_allow_html=True)