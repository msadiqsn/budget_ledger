import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# 🔌 SUPABASE CONNECTION
# -----------------------------
SUPABASE_URL =  "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY =  "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



# -----------------------------
# 🎨 UI STYLE
# -----------------------------
st.markdown("""
<style>
body { background-color: #F5F7FA; }
.card {
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.blue { background-color: #E3F2FD; }
.orange { background-color: #FFF3E0; }
.green { background-color: #E8F5E9; }
.title { font-size:16px; font-weight:600; margin-bottom:10px; }
.row {
    display:flex; justify-content:space-between;
    font-size:14px; padding:3px 0;
}
.total { font-weight:bold; margin-top:8px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# FUNCTIONS
# -----------------------------
def save_to_db(month, fixed, variable, investment, total):
    supabase.table("budget").insert({
        "month": month,
        "fixed_total": fixed,
        "variable_total": variable,
        "investment_total": investment,
        "grand_total": total
    }).execute()

def load_data():
    return supabase.table("budget").select("*").execute().data

# -----------------------------
# DATA
# -----------------------------
fixed_expenses = {
    "Home Rent": 16000,
    "WiFi": 1000,
    "Abba": 10000,
    "Loan": 10000,
    "Ammi": 3000,
    "Maid Aunty": 3000
}

variable_budget = {
    "Groceries": 9000,
    "Electricity": 1000,
    "Outside Food": 5000,
    "Miscellaneous": 7000
}

investments = {
    "Bissi": 10000,
    "SIP": 50000
}

# -----------------------------
# HEADER
# -----------------------------
st.title("MONTHLY BUDGET")

month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

col1, col2 = st.columns(2)

# -----------------------------
# FIXED
# -----------------------------
with col1:
    st.markdown('<div class="card blue">', unsafe_allow_html=True)
    st.markdown('<div class="title">FIXED EXPENSES</div>', unsafe_allow_html=True)

    fixed_total = 0
    for item, amount in fixed_expenses.items():
        paid = st.checkbox(f"{item} — ₹{amount}", key=item)
        if paid:
            fixed_total += amount
        st.markdown(f'<div class="row"><span>{item}</span><span>₹{amount}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Total: ₹{fixed_total}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# VARIABLE + INVESTMENT
# -----------------------------
with col2:

    st.markdown('<div class="card orange">', unsafe_allow_html=True)
    st.markdown('<div class="title">VARIABLE EXPENSES</div>', unsafe_allow_html=True)

    variable_total = 0
    for item, budget in variable_budget.items():
        actual = st.number_input(f"{item} (₹{budget})", min_value=0, step=100, key=item+"_var")
        variable_total += actual

        diff = actual - budget
        if diff > 0:
            st.error(f"{item}: +₹{diff}")
        elif diff < 0:
            st.success(f"{item}: ₹{abs(diff)} saved")

        st.markdown(f'<div class="row"><span>{item}</span><span>₹{actual}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Total: ₹{variable_total}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # INVESTMENT
    st.markdown('<div class="card green">', unsafe_allow_html=True)
    st.markdown('<div class="title">INVESTMENTS</div>', unsafe_allow_html=True)

    investment_total = 0
    for item, amount in investments.items():
        done = st.checkbox(f"{item} — ₹{amount}", key=item+"_inv")
        if done:
            investment_total += amount
        st.markdown(f'<div class="row"><span>{item}</span><span>₹{amount}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Total: ₹{investment_total}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# GRAND TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total

st.markdown(f"""
<div class="card" style="text-align:center;">
    <div class="title">GRAND TOTAL</div>
    <div style="font-size:22px; font-weight:bold; color:green;">
        ₹{grand_total}
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save Month Data"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total)
    st.success("Saved permanently!")

# -----------------------------
# HISTORY
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data)
    df = df.sort_values("created_at")

    st.subheader("📈 Trend")
    st.line_chart(df.set_index("month")["grand_total"])

    st.subheader("📊 Category")
    st.bar_chart(df[["fixed_total", "variable_total", "investment_total"]])

    # Pie
    latest = df.iloc[-1]
    fig, ax = plt.subplots()
    ax.pie(
        [latest["fixed_total"], latest["variable_total"], latest["investment_total"]],
        labels=["Fixed", "Variable", "Investment"],
        autopct="%1.1f%%"
    )
    st.pyplot(fig)

    # -----------------------------
    # 🤖 AI INSIGHTS
    # -----------------------------
    st.subheader("🤖 Smart Insights")

    avg_spending = df["grand_total"].mean()
    last = df.iloc[-1]["grand_total"]

    if last > avg_spending:
        st.warning(f"⚠️ You are spending ₹{int(last-avg_spending)} above your average")

    else:
        st.success(f"✅ You are saving ₹{int(avg_spending-last)} vs your average")

    # trend direction
    if len(df) > 2:
        if df.iloc[-1]["variable_total"] > df.iloc[-2]["variable_total"]:
            st.warning("📈 Variable spending is increasing")

    # investment consistency
    if df["investment_total"].mean() < 60000:
        st.error("❌ Investment average below target")

    else:
        st.success("🎯 Strong investment consistency")

    # prediction
    predicted = int(df["grand_total"].mean())
    st.info(f"📊 Predicted next month spending: ₹{predicted}")