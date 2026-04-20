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
# STYLE (PREMIUM)
# -----------------------------
st.markdown("""
<style>
body { background:#F5F7FA; }

.block {
    padding:14px;
    border-radius:12px;
    margin-bottom:10px;
    background:white;
    box-shadow:0 2px 6px rgba(0,0,0,0.05);
}

.label {
    font-size:14px;
    font-weight:500;
}

.ref {
    font-size:12px;
    color:gray;
    margin-bottom:4px;
}

button {
    width:100%;
    height:50px;
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
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")

month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# FIXED (EDITABLE + REF)
# -----------------------------
st.subheader("🏠 Fixed")

rent = st.number_input("Rent (Ref ₹16000)", value=16000, step=500)
abba = st.number_input("Abba (Ref ₹10000)", value=10000, step=500)
loan = st.number_input("Loan (Ref ₹10000)", value=10000, step=500)
ammi = st.number_input("Ammi (Ref ₹3000)", value=3000, step=500)
maid = st.number_input("Maid (Ref ₹3000)", value=3000, step=500)

fixed_total = rent + abba + loan + ammi + maid

# -----------------------------
# VARIABLE
# -----------------------------
st.subheader("📊 Variable")

groceries = st.number_input("Groceries (Ref ₹9000)", value=9000, step=500)
electricity = st.number_input("Electricity + WiFi (Ref ₹2000)", value=2000, step=500)
outside = st.number_input("Outside Food (Ref ₹5000)", value=5000, step=500)
misc = st.number_input("Miscellaneous (Ref ₹7000)", value=7000, step=500)

variable_total = groceries + electricity + outside + misc

var_data = {
    "Groceries": groceries,
    "Electricity": electricity,
    "Outside Food": outside,
    "Miscellaneous": misc
}

# -----------------------------
# INVESTMENTS
# -----------------------------
st.subheader("📈 Investments")

bissi = st.number_input("Bissi (Ref ₹10000)", value=10000, step=500)
sip = st.number_input("SIP (Ref ₹50000)", value=50000, step=500)

investment_total = bissi + sip

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total

st.metric("💰 Total Monthly Spend", f"₹{grand_total}")

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

    # -----------------------------
    # PREMIUM MULTI LINE CHART
    # -----------------------------
    st.subheader("📈 Spending Trend")

    fig, ax = plt.subplots()

    ax.plot(df["month"], df["grand_total"], marker='o', linewidth=2, label="Total")
    ax.plot(df["month"], df["fixed_total"], linestyle='--', label="Fixed")
    ax.plot(df["month"], df["variable_total"], linestyle='--', label="Variable")
    ax.plot(df["month"], df["investment_total"], linestyle='--', label="Investment")

    ax.set_xticklabels(df["month"], rotation=30)
    ax.legend()
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    # -----------------------------
    # SMART INSIGHTS
    # -----------------------------
    st.subheader("🤖 Smart Insight")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    text = ""

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            text += f"Spending increased ₹{int(diff)}. "
        else:
            text += f"You saved ₹{int(abs(diff))}. "

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
        text += f"Main issue: {worst}. "

        total_waste = sum(overspend.values())
        text += f"Save ₹{int(total_waste)}/month (~₹{int(total_waste*12)}/year)."

    st.info(text)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.subheader("🎯 Action Plan")

        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")