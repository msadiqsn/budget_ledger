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
# STYLE
# -----------------------------
st.markdown("""
<style>
.ref-box {
    border:1px solid rgba(128,128,128,0.4);
    padding:6px;
    border-radius:8px;
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
    col1, col2, col3 = st.columns([1.3,1,1])

    with col1:
        st.markdown(f"**{label}**")

    with col2:
        st.markdown(f'<div class="ref-box">₹{ref}</div>', unsafe_allow_html=True)

    with col3:
        val = st.number_input("", value=ref, step=500, key=key)

    if val <= ref:
        st.caption(f"Saved ₹{ref-val}")
    else:
        st.caption(f"Overspent ₹{val-ref}")

    return val

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

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
# DATA + AI
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

    # CHANGE
    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        st.write("📈 Spending increased" if diff>0 else "📉 You saved", f"₹{abs(int(diff))}")

    # RATIOS
    total = latest["grand_total"]
    fixed_pct = latest["fixed_total"]/total*100
    variable_pct = latest["variable_total"]/total*100
    invest_pct = latest["investment_total"]/total*100

    st.write(f"📊 Fixed: {fixed_pct:.1f}% | Variable: {variable_pct:.1f}% | Investment: {invest_pct:.1f}%")

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

        st.write(f"🚨 Biggest leak: {worst}")
        st.write(f"💸 Save ₹{total_waste}/month (~₹{total_waste*12}/year)")

    # LIFESTYLE SIGNAL
    if latest["outside_food"] > 5000:
        st.write("🍔 High eating-out lifestyle detected")
    if latest["miscellaneous"] > 7000:
        st.write("📦 Misc expenses leaking money")

    # INVESTMENT FEEDBACK (IMPROVED)
    if investment_total > investment_ref:
        extra = investment_total - investment_ref
        st.success(f"🚀 Excellent! Investing ₹{extra} extra/month → strong wealth growth")
    elif investment_total < investment_ref:
        st.warning(f"⚠️ Invest ₹{investment_ref - investment_total} more to stay on track")

    # PREDICTION
    if prev is not None:
        trend = latest["grand_total"] - prev["grand_total"]
        st.write(f"🔮 Next month expected ~₹{int(latest['grand_total'] + trend)}")

    # FINAL ADVICE
    st.markdown("### 🎯 Action Advice")
    if overspend:
        for k,v in overspend.items():
            st.write(f"Reduce {k} by ₹{int(v)}")
