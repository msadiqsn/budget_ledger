import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL = "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY = "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

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
# ROW COMPONENT
# -----------------------------
def row_input(label, ref, key):

    st.markdown(f"### {label}")

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown(f"""
        <div style="
            background:#D6E4FF;
            padding:12px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
        ">
            ₹{ref}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        val = st.number_input("", value=ref, step=500, key=key)

    percent = val / ref if ref else 0

    if percent <= 1:
        st.progress(percent)
        st.markdown(f"<span style='color:green;'>Saved ₹{ref-val}</span>", unsafe_allow_html=True)
    else:
        st.progress(1.0)
        st.markdown(f"<span style='color:red;'>Overspent ₹{val-ref}</span>", unsafe_allow_html=True)

    st.markdown("---")

    return val

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# FIXED
# -----------------------------
st.header("🏠 Fixed Expenses")

rent = row_input("Rent",16000,"rent")
abba = row_input("Abba",10000,"abba")
loan = row_input("Loan",10000,"loan")
ammi = row_input("Ammi",3000,"ammi")
maid = row_input("Maid",3000,"maid")

fixed_total = rent + abba + loan + ammi + maid
fixed_ref = 43000

diff_fixed = fixed_total - fixed_ref

if diff_fixed > 0:
    st.error(f"Fixed: Overspent ₹{diff_fixed}")
else:
    st.success(f"Fixed: Saved ₹{abs(diff_fixed)}")

# -----------------------------
# VARIABLE
# -----------------------------
st.header("📊 Variable Expenses")

groceries = row_input("Groceries",9000,"gro")
electricity = row_input("Electricity",1000,"elec")
wifi = row_input("WiFi",1000,"wifi")
outside = row_input("Outside Food",5000,"out")
misc = row_input("Miscellaneous",7000,"misc")

variable_total = groceries + electricity + wifi + outside + misc
variable_ref = 23000

diff_var = variable_total - variable_ref

if diff_var > 0:
    st.error(f"Variable: Overspent ₹{diff_var}")
else:
    st.success(f"Variable: Saved ₹{abs(diff_var)}")

var_data = {
    "Groceries": groceries,
    "Electricity": electricity + wifi,
    "Outside Food": outside,
    "Miscellaneous": misc
}

# -----------------------------
# INVESTMENT
# -----------------------------
st.header("📈 Investment")

bissi = row_input("Bissi",10000,"bissi")
sip = row_input("SIP",50000,"sip")

investment_total = bissi + sip
investment_ref = 60000

diff_inv = investment_total - investment_ref

if diff_inv < 0:
    st.warning(f"Invest ₹{abs(diff_inv)} more to reach target")
else:
    st.success("Investment on track")

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("💰 Total Spend", f"₹{grand_total}")

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save Month"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved")

# -----------------------------
# DATA + CHART
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    st.subheader("📈 Trend")

    fig, ax = plt.subplots()

    ax.plot(df["month"], df["grand_total"], label="Total", linewidth=3)
    ax.plot(df["month"], df["fixed_total"], label="Fixed")
    ax.plot(df["month"], df["variable_total"], label="Variable")
    ax.plot(df["month"], df["investment_total"], label="Investment")

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)

    # -----------------------------
    # 🤖 AI INSIGHTS
    # -----------------------------
    st.subheader("🤖 Smart Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    insights = []

    # change
    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            insights.append(f"📈 Spending increased by ₹{int(diff)}")
        else:
            insights.append(f"📉 You saved ₹{int(abs(diff))}")

    # overspend categories
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

        insights.append(f"🚨 Biggest issue: {worst}")
        insights.append(f"💸 You can save ₹{int(total_waste)}/month (~₹{int(total_waste*12)}/year)")

    # good categories
    good = [k for k in budget if k not in overspend]
    if good:
        insights.append(f"✅ Good control on: {', '.join(good)}")

    # suggestions
    if "Outside Food" in overspend:
        insights.append("🍔 Reduce eating out by 20% to save significantly")
    if "Miscellaneous" in overspend:
        insights.append("📦 Track small expenses — they are leaking money")

    # prediction
    if prev is not None:
        trend = latest["grand_total"] - prev["grand_total"]
        next_month = latest["grand_total"] + trend
        insights.append(f"🔮 Next month expected ~₹{int(next_month)}")

    for i in insights:
        st.write(i)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.subheader("🎯 Action Plan")

        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")