import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# INDIAN NUMBER FORMAT
# -----------------------------
def format_inr(num):
    num = int(num)
    s = str(num)

    if len(s) <= 3:
        return s

    last3 = s[-3:]
    rest = s[:-3]

    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts) + "," + last3

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
        st.markdown(f'<div class="ref-box">₹{format_inr(ref)}</div>', unsafe_allow_html=True)

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
        f'<span class="good">Stable foundation 👍 You are within fixed budget (Saved ₹{format_inr(abs(diff_fixed))})</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Fixed costs increased by ₹{format_inr(diff_fixed)} — review commitments</span>',
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
        f'<span class="good">Excellent control 🔥 Saved ₹{format_inr(saved)} this month (~₹{format_inr(saved*12)}/year impact)</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Overspending ₹{format_inr(diff_var)} — lifestyle leak detected</span>',
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
        f'<span class="good">🚀 Strong wealth building! Extra ₹{format_inr(extra)} invested — this accelerates your future</span>',
        unsafe_allow_html=True
    )
elif investment_total == investment_ref:
    st.markdown(
        '<span class="good">Disciplined investing 👍 you are on the right path</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="warn">Increase investment by ₹{format_inr(investment_ref - investment_total)} to stay on track</span>',
        unsafe_allow_html=True
    )

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("💰 Total", f"₹{format_inr(grand_total)}")

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

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    # -----------------------------
    # 📊 FINANCIAL SCORE
    # -----------------------------
    st.subheader("📊 Financial Score")

    score = 100

    if latest["variable_total"] > 23000:
        score -= 25
    else:
        score += 5

    if sip < 50000:
        score -= 25
    else:
        score += 5

    if prev is not None:
        if latest["grand_total"] > prev["grand_total"]:
            score -= 15
        else:
            score += 5

    score = max(0, min(100, score))

    if score >= 90:
        status = "Excellent 🚀"
    elif score >= 75:
        status = "Good 👍"
    elif score >= 60:
        status = "Average ⚠️"
    else:
        status = "Needs Attention 🚨"

    st.metric("Score", score)
    st.write(status)

    # -----------------------------
    # 🎯 WEALTH PROJECTION
    # -----------------------------
    st.subheader("🎯 Wealth Projection")
    st.caption("Assuming 12% annual return")

    monthly_sip = sip
    r = 12/100/12

    def fv_sip(p, months):
        return p * (((1+r)**months - 1)/r)

    # ✅ FIXED FUNCTION
    def fv_step_up(p, years, step):
        total = 0
        total_months = years * 12
        current_sip = p

        for y in range(years):
            for m in range(12):
                month_index = y * 12 + m
                remaining_months = total_months - month_index
                total += current_sip * ((1 + r) ** remaining_months)

            current_sip *= (1 + step)

        return total

    durations = [5, 7, 10]
    steps = [0.05, 0.10, 0.15]

    for yrs in durations:
        months = yrs * 12

        flat = fv_sip(monthly_sip, months)
        step_vals = [fv_step_up(monthly_sip, yrs, s) for s in steps]

        st.markdown(f"**{yrs} Years:**")
        st.write(f"• Flat SIP → ₹{format_inr(flat)}")
        st.write(f"• Step-up 5% → ₹{format_inr(step_vals[0])}")
        st.write(f"• Step-up 10% → ₹{format_inr(step_vals[1])} 🚀")
        st.write(f"• Step-up 15% → ₹{format_inr(step_vals[2])}")
        st.write("")

    # -----------------------------
    # REQUIRED SIP TABLE
    # -----------------------------
    st.markdown("### 📊 Required SIP for Same Growth (10 Years Target)")

    target = fv_sip(monthly_sip, 10*12)

    def required_sip(target, step):
        sip_guess = 1000
        while True:
            if fv_step_up(sip_guess, 10, step) >= target:
                return sip_guess
            sip_guess += 500

    table = pd.DataFrame({
        "Step-up": ["5%", "10%", "15%"],
        "Required SIP": [
            f"₹{format_inr(required_sip(target, 0.05))}",
            f"₹{format_inr(required_sip(target, 0.10))}",
            f"₹{format_inr(required_sip(target, 0.15))}"
        ]
    })

    st.table(table)

    st.subheader("📈 Trend")

    fig, ax = plt.subplots()
    ax.plot(df["month"], df["grand_total"], linewidth=3)
    ax.plot(df["month"], df["variable_total"])
    ax.plot(df["month"], df["fixed_total"])
    ax.legend(["Total","Variable","Fixed"])
    st.pyplot(fig)

    st.subheader("🤖 Smart Insights")

    summary = []

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        summary.append(f"Spending changed by ₹{format_inr(abs(diff))}")

    for s in summary:
        st.write("•", s)

    st.markdown("### 🎯 Action Plan")
    st.success("Keep consistency and increase SIP gradually 🚀")