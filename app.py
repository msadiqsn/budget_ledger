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
    background:rgba(255,255,255,0.08);
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
# FIXED (CORRECTED)
# -----------------------------
st.subheader("🏠 Fixed")

rent = row_input("Rent",16000,"rent")
abba = row_input("Abba",10000,"abba")
loan = row_input("Loan",10000,"loan")
ammi = row_input("Ammi",3000,"ammi")
maid = row_input("Maid",3000,"maid")

fixed_total = rent + abba + loan + ammi + maid
fixed_ref = 42000  # ✅ corrected

diff_fixed = fixed_total - fixed_ref

if diff_fixed > 0:
    st.markdown(f'<span class="bad">Fixed → Overspent ₹{diff_fixed}</span>', unsafe_allow_html=True)
else:
    st.markdown(f'<span class="good">Fixed → Saved ₹{abs(diff_fixed)}</span>', unsafe_allow_html=True)

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

if diff_var > 0:
    st.markdown(f'<span class="bad">Variable → Overspent ₹{diff_var}</span>', unsafe_allow_html=True)
else:
    st.markdown(f'<span class="good">Variable → Saved ₹{abs(diff_var)}</span>', unsafe_allow_html=True)

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

diff_inv = investment_total - investment_ref

if diff_inv < 0:
    st.markdown(f'<span class="warn">Need ₹{abs(diff_inv)} more investment</span>', unsafe_allow_html=True)
else:
    st.markdown(f'<span class="good">Investment on track</span>', unsafe_allow_html=True)

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

    # CHART
    st.subheader("📈 Trend")
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["grand_total"], linewidth=3)
    ax.plot(df["month"], df["variable_total"])
    ax.plot(df["month"], df["fixed_total"])
    ax.legend(["Total","Variable","Fixed"])
    st.pyplot(fig)

    # -----------------------------
    # AI INSIGHTS (FULL)
    # -----------------------------
    st.subheader("🤖 Smart Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    # CHANGE
    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        st.write("📈 Increased" if diff>0 else "📉 Saved", f"₹{abs(int(diff))}")

    # CATEGORY ANALYSIS
    budget = {
        "Groceries":9000,
        "Electricity":2000,
        "Outside Food":5000,
        "Miscellaneous":7000
    }

    overspend = {}
    good = []

    for k,v in budget.items():
        col = k.lower().replace(" ","_")
        if latest[col] > v:
            overspend[k] = latest[col] - v
        else:
            good.append(k)

    if overspend:
        worst = max(overspend, key=overspend.get)
        total_waste = sum(overspend.values())

        st.write(f"🚨 Biggest issue: {worst}")
        st.write(f"💸 Save ₹{total_waste}/month (~₹{total_waste*12}/year)")

    if good:
        st.write(f"✅ Good control: {', '.join(good)}")

    # SMART SUGGESTIONS
    if "Outside Food" in overspend:
        st.write("🍔 Reduce outside food by 20% → big savings")
    if "Miscellaneous" in overspend:
        st.write("📦 Track small spends — hidden leakage")

    # PREDICTION
    if prev is not None:
        trend = latest["grand_total"] - prev["grand_total"]
        st.write(f"🔮 Next month ~₹{int(latest['grand_total'] + trend)}")
