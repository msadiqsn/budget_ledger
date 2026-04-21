import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL = "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY = "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
.ref-box {
    border:1px solid rgba(128,128,128,0.5);
    padding:6px;
    border-radius:6px;
    text-align:center;
    font-weight:600;
    font-size:13px;
}
.good { color:#00C853; font-weight:600; }
.bad { color:#FF5252; font-weight:600; }
.warn { color:#FFA000; font-weight:600; }
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
# ROW INPUT
# -----------------------------
def row_input(label, ref, key):
    col1, col2, col3 = st.columns([1.2,1,1])

    with col1:
        st.write(label)

    with col2:
        st.markdown(f'<div class="ref-box">₹{ref}</div>', unsafe_allow_html=True)

    with col3:
        val = st.number_input("", value=ref, step=500, key=key)

    return val

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
years = list(range(2024, 2035))

col1, col2 = st.columns(2)
with col1:
    selected_month = st.selectbox("Month", months)
with col2:
    selected_year = st.selectbox("Year", years)

month = f"{selected_month} {selected_year}"

# -----------------------------
# FIXED
# -----------------------------
st.subheader("🏠 Fixed")

rent = row_input("Rent",16000,"rent")
abba = row_input("Abba",10000,"abba")
loan = row_input("Loan",10000,"loan")
ammi = row_input("Ammi",3000,"ammi")
maid = row_input("Maid",3000,"maid")

fixed_total = rent + abba + loan + ammi + maid
fixed_ref = 42000

diff_fixed = fixed_total - fixed_ref

if diff_fixed <= 0:
    st.markdown(
        f'<span class="good">Stable foundation 👍 You are within fixed budget (Saved ₹{abs(diff_fixed)})</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Fixed costs increased by ₹{diff_fixed} — review commitments</span>',
        unsafe_allow_html=True
    )

# -----------------------------
# VARIABLE
# -----------------------------
st.subheader("📊 Variable")

groceries = row_input("Groceries",9000,"gro")
electricity = row_input("Electricity",1000,"elec")
wifi = row_input("WiFi",1000,"wifi")
outside = row_input("Outside Food",5000,"out")
misc = row_input("Miscellaneous",7000,"misc")

variable_total = groceries + electricity + wifi + outside + misc
variable_ref = 23000

diff_var = variable_total - variable_ref

if diff_var <= 0:
    saved = abs(diff_var)
    st.markdown(
        f'<span class="good">Excellent control 🔥 Saved ₹{saved} this month (~₹{saved*12}/year impact)</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Overspending ₹{diff_var} — lifestyle leak detected</span>',
        unsafe_allow_html=True
    )

var_data = {
    "Groceries": groceries,
    "Electricity": electricity + wifi,
    "Outside Food": outside,
    "Miscellaneous": misc
}

# -----------------------------
# INVESTMENT
# -----------------------------
st.subheader("📈 Investment")

bissi = row_input("Bissi",10000,"bissi")
sip = row_input("SIP",50000,"sip")

investment_total = bissi + sip
investment_ref = 60000

if investment_total > investment_ref:
    extra = investment_total - investment_ref
    st.markdown(
        f'<span class="good">🚀 Strong wealth building! Extra ₹{extra} invested — this accelerates your future</span>',
        unsafe_allow_html=True
    )
elif investment_total == investment_ref:
    st.markdown(
        '<span class="good">Disciplined investing 👍 you are on the right path</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="warn">Increase investment by ₹{investment_ref - investment_total} to stay on track</span>',
        unsafe_allow_html=True
    )

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("💰 Total", f"₹{grand_total}")

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved")

# -----------------------------
# DATA + AI INSIGHTS
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    st.subheader("📈 Trend")

    fig, ax = plt.subplots()
    ax.plot(df["month"], df["grand_total"], linewidth=3)
    ax.plot(df["month"], df["variable_total"])
    ax.plot(df["month"], df["fixed_total"])
    ax.legend(["Total","Variable","Fixed"])
    st.pyplot(fig)

    # -----------------------------
    # AI INSIGHTS (STRONG)
    # -----------------------------
    st.subheader("🤖 Smart Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    summary = []

    # TREND
    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            summary.append(f"Spending increased by ₹{int(diff)}")
        else:
            summary.append(f"You improved savings by ₹{int(abs(diff))}")

    # CATEGORY ANALYSIS
    budget = {
        "Groceries":9000,
        "Electricity":2000,
        "Outside Food":5000,
        "Miscellaneous":7000
    }

    overspend = {}
    for k,v in budget.items():
        col = k.lower().replace(" ","_")
        if latest[col] > v:
            overspend[k] = latest[col] - v

    if overspend:
        worst = max(overspend, key=overspend.get)
        total_waste = sum(overspend.values())

        summary.append(f"Biggest leak: {worst}")
        summary.append(f"Potential saving ₹{total_waste}/month (~₹{total_waste*12}/year)")

    # LIFESTYLE
    if latest["outside_food"] > 5000:
        summary.append("Frequent eating out increasing expenses")
    if latest["miscellaneous"] > 7000:
        summary.append("Untracked misc spending detected")

    # INVESTMENT
    if latest["investment_total"] > 60000:
        summary.append("Strong investment discipline")
    else:
        summary.append("Investment can be improved")

    # OUTPUT
    for s in summary:
        st.write("•", s)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    st.markdown("### 🎯 Action Plan")

    if overspend:
        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")

    if latest["investment_total"] < 60000:
        st.write("Increase SIP or Bissi contribution")
