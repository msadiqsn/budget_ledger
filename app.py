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
# STYLE FIX
# -----------------------------
st.markdown("""
<style>
.ref-box {
    background:#D6E4FF;
    color:#000;
    padding:10px;
    border-radius:8px;
    text-align:center;
    font-weight:600;
    font-size:15px;
}

.progress-text {
    font-size:13px;
    margin-top:3px;
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
# ROW INPUT
# -----------------------------
def row_input(label, ref, key):
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown(f'<div class="ref-box">₹{ref}</div>', unsafe_allow_html=True)

    with col2:
        val = st.number_input(label, value=ref, step=500, key=key, label_visibility="collapsed")

    percent = val / ref if ref else 0

    if percent <= 1:
        st.progress(percent)
        st.markdown(f"<div class='progress-text' style='color:green;'>Saved ₹{ref - val}</div>", unsafe_allow_html=True)
    else:
        st.progress(1.0)
        st.markdown(f"<div class='progress-text' style='color:red;'>Overspent ₹{val - ref}</div>", unsafe_allow_html=True)

    return val

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# FIXED
# -----------------------------
st.subheader("🏠 Fixed Expenses")

rent = row_input("Rent",16000,"rent")
abba = row_input("Abba",10000,"abba")
loan = row_input("Loan",10000,"loan")
ammi = row_input("Ammi",3000,"ammi")
maid = row_input("Maid",3000,"maid")

fixed_total = rent + abba + loan + ammi + maid
fixed_ref = 16000 + 10000 + 10000 + 3000 + 3000

# SUMMARY
diff_fixed = fixed_total - fixed_ref
if diff_fixed > 0:
    st.error(f"Fixed: Ref ₹{fixed_ref} | Actual ₹{fixed_total} → Overspent ₹{diff_fixed}")
else:
    st.success(f"Fixed: Ref ₹{fixed_ref} | Actual ₹{fixed_total} → Saved ₹{abs(diff_fixed)}")

# -----------------------------
# VARIABLE
# -----------------------------
st.subheader("📊 Variable Expenses")

groceries = row_input("Groceries",9000,"gro")
electricity = row_input("Electricity",1000,"elec")
wifi = row_input("WiFi",1000,"wifi")
outside = row_input("Outside Food",5000,"out")
misc = row_input("Miscellaneous",7000,"misc")

variable_total = groceries + electricity + wifi + outside + misc
variable_ref = 9000 + 2000 + 5000 + 7000

diff_var = variable_total - variable_ref
if diff_var > 0:
    st.error(f"Variable: Ref ₹{variable_ref} | Actual ₹{variable_total} → Overspent ₹{diff_var}")
else:
    st.success(f"Variable: Ref ₹{variable_ref} | Actual ₹{variable_total} → Saved ₹{abs(diff_var)}")

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
    st.warning(f"Investment: Target ₹{investment_ref} | Actual ₹{investment_total} → Need ₹{abs(diff_inv)} more")
else:
    st.success(f"Investment: Target ₹{investment_ref} | Actual ₹{investment_total}")

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("Total Monthly Spend", f"₹{grand_total}")

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save Month"):
    save_to_db(month,fixed_total,variable_total,investment_total,grand_total,var_data)
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
    ax.plot(df["month"], df["variable_total"], label="Variable")
    ax.plot(df["month"], df["fixed_total"], label="Fixed")
    ax.plot(df["month"], df["investment_total"], label="Investment")

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)