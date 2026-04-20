import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# -----------------------------
# SUPABASE (YOUR PROVIDED)
# -----------------------------
SUPABASE_URL =  "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY =  "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# STYLE (PREMIUM UI)
# -----------------------------
st.markdown("""
<style>
body { background:#F5F7FA; }

.card {
    padding:16px;
    border-radius:14px;
    margin-bottom:12px;
    background:white;
    box-shadow:0 3px 8px rgba(0,0,0,0.06);
}

.kpi {
    padding:12px;
    border-radius:12px;
    text-align:center;
    color:white;
    font-weight:bold;
}

.blue { background:#4A90E2; }
.orange { background:#F5A623; }
.green { background:#7ED321; }
.red { background:#D0021B; }

.title { font-size:13px; opacity:0.8; }
.value { font-size:18px; }
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
# DATA
# -----------------------------
fixed_expenses = {
    "🏠 Rent": 16000,
    "📶 WiFi": 1000,
    "👨 Abba": 10000,
    "💳 Loan": 10000,
    "👩 Ammi": 3000,
    "🧹 Maid": 3000
}

variable_budget = {
    "🛒 Groceries": 9000,
    "💡 Electricity": 1000,
    "🍔 Outside Food": 5000,
    "📦 Misc": 7000
}

investments = {
    "💰 Bissi": 10000,
    "📈 SIP": 50000
}

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Budget Dashboard")

month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# INPUTS (CARDS)
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Fixed")

fixed_total = 0
for k,v in fixed_expenses.items():
    if st.checkbox(f"{k} ₹{v}", key=k):
        fixed_total += v
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Variable")

variable_total = 0
var_data = {}

for k,v in variable_budget.items():
    val = st.number_input(k, value=v, step=100, key=k+"_var")
    variable_total += val
    var_data[k.split(" ",1)[1]] = val

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Investment")

investment_total = 0
for k,v in investments.items():
    if st.checkbox(f"{k} ₹{v}", key=k+"_inv"):
        investment_total += v
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total

# -----------------------------
# SAVE
# -----------------------------
if st.button("💾 Save"):
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved")

# -----------------------------
# LOAD DATA
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    # -----------------------------
    # KPI STRIP WITH COLORS
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="kpi blue"><div class="title">Total</div><div class="value">₹{int(latest["grand_total"])}</div></div>', unsafe_allow_html=True)

    with col2:
        if prev is not None:
            diff = latest["grand_total"] - prev["grand_total"]
            color = "green" if diff < 0 else "red"
            st.markdown(f'<div class="kpi {color}"><div class="title">Change</div><div class="value">₹{int(diff)}</div></div>', unsafe_allow_html=True)

    cat_map = {
        "Groceries":"groceries",
        "Electricity":"electricity",
        "Outside Food":"outside_food",
        "Miscellaneous":"miscellaneous"
    }

    biggest = max(cat_map, key=lambda k: latest[cat_map[k]])

    with col3:
        st.markdown(f'<div class="kpi orange"><div class="title">Top</div><div class="value">{biggest}</div></div>', unsafe_allow_html=True)

    score = 100
    if latest["variable_total"] > 22000:
        score -= 20
    if latest["investment_total"] < 60000:
        score -= 20

    with col4:
        st.markdown(f'<div class="kpi blue"><div class="title">Score</div><div class="value">{score}</div></div>', unsafe_allow_html=True)

    # -----------------------------
    # MINI CHART (INSIDE DASHBOARD)
    # -----------------------------
    st.markdown("### 📊 Spending Trend")
    st.line_chart(df.set_index("month")["grand_total"])

    # -----------------------------
    # CATEGORY MINI BAR
    # -----------------------------
    st.markdown("### 📊 Category Split")
    st.bar_chart(df[["fixed_total","variable_total","investment_total"]])

    # -----------------------------
    # AI SUMMARY
    # -----------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)

    overspend = {}
    for k,v in variable_budget.items():
        name = k.split(" ",1)[1]
        col = name.lower().replace(" ","_")
        if latest[col] > v:
            overspend[name] = latest[col] - v

    text = ""

    if overspend:
        worst = max(overspend, key=overspend.get)
        text += f"⚠️ Overspending on {worst}. "

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            text += f"Spending increased ₹{int(diff)}. "
        else:
            text += f"You saved ₹{int(abs(diff))}. "

    total_waste = sum(overspend.values())
    if total_waste > 0:
        text += f"Save ₹{int(total_waste)}/month."

    st.write(text)

    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### 🎯 Action Plan")

        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"• Reduce {k} by ₹{int(v)}")

        st.markdown('</div>', unsafe_allow_html=True)