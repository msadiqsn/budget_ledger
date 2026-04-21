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
# ROW
# -----------------------------
def row_input(label, ref, key):
    col1, col2, col3 = st.columns([1.2,1,1])

    with col1:
        st.markdown(f"**{label}**")

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

# MOTIVATION
diff_var = variable_total - variable_ref

if diff_var <= 0:
    saved = abs(diff_var)
    st.markdown(
        f'<span class="good">Great control! You saved ₹{saved} this month (~₹{saved*12}/year)</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Overspent ₹{diff_var} — focus on reducing leaks</span>',
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
        f'<span class="good">Excellent! ₹{extra} extra invested — strong wealth growth 🚀</span>',
        unsafe_allow_html=True
    )
elif investment_total < investment_ref:
    st.markdown(
        f'<span class="warn">Invest ₹{investment_ref-investment_total} more</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<span class="good">Perfect investment discipline</span>', unsafe_allow_html=True)

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
    # AI INSIGHTS (ADVANCED)
    # -----------------------------
    st.subheader("🤖 Smart Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    # 1. TREND
    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        st.write("📈 Spending increased" if diff>0 else "📉 You improved savings", f"₹{abs(int(diff))}")

    # 2. RATIO ANALYSIS
    total = latest["grand_total"]
    st.write(
        f"📊 Allocation → Fixed: {latest['fixed_total']/total*100:.1f}% | "
        f"Variable: {latest['variable_total']/total*100:.1f}% | "
        f"Investment: {latest['investment_total']/total*100:.1f}%"
    )

    # 3. CATEGORY ANALYSIS
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

        st.write(f"🚨 Biggest leak: {worst}")
        st.write(f"💸 Potential saving: ₹{total_waste}/month (~₹{total_waste*12}/year)")

    # 4. LIFESTYLE SIGNALS
    if latest["outside_food"] > 5000:
        st.write("🍔 High eating-out trend impacting budget")
    if latest["miscellaneous"] > 7000:
        st.write("📦 Misc spending needs tracking")

    # 5. INVESTMENT HEALTH
    if latest["investment_total"] >= 60000:
        st.write("🚀 Strong investment discipline")
    else:
        st.write("⚠️ Investment below optimal level")

    # 6. PREDICTION
    if prev is not None:
        trend = latest["grand_total"] - prev["grand_total"]
        st.write(f"🔮 Next month projection: ₹{int(latest['grand_total'] + trend)}")

    # 7. ACTION PLAN
    st.markdown("### 🎯 Action Plan")
    if overspend:
        for k,v in overspend.items():
            st.write(f"Reduce {k} by ₹{int(v)}")