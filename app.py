import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# 🔌 SUPABASE CONFIG
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
.row { display:flex; justify-content:space-between; font-size:14px; }
.total { font-weight:bold; margin-top:8px; }
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

def create_pdf(month, insights_text):
    file_path = f"{month}_report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f"<b>Monthly Financial Report</b>", styles["Title"]))
    elements.append(Spacer(1,10))
    elements.append(Paragraph(insights_text, styles["Normal"]))
    doc.build(elements)
    return file_path

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
    var_data = {}

    for item, budget in variable_budget.items():
        actual = st.number_input(f"{item} (₹{budget})", min_value=0, step=100, key=item+"_var")
        variable_total += actual
        var_data[item] = actual

    st.markdown(f'<div class="total">Total: ₹{variable_total}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card green">', unsafe_allow_html=True)
    st.markdown('<div class="title">INVESTMENTS</div>', unsafe_allow_html=True)

    investment_total = 0
    for item, amount in investments.items():
        done = st.checkbox(f"{item} — ₹{amount}", key=item+"_inv")
        if done:
            investment_total += amount

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
    save_to_db(month, fixed_total, variable_total, investment_total, grand_total, var_data)
    st.success("Saved permanently!")

# -----------------------------
# LOAD DATA
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    st.subheader("📈 Trend")
    st.line_chart(df.set_index("month")["grand_total"])

    st.subheader("📊 Category Trends")
    st.line_chart(df.set_index("month")[["groceries","electricity","outside_food","miscellaneous"]])

    # -----------------------------
    # 🧠 ULTIMATE AI ADVISOR
    # -----------------------------
    st.subheader("🤖 AI Financial Advisor")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    # Category analysis
    overspend = {}
    contributions = {}

    for k,v in variable_budget.items():
        col = k.lower().replace(" ","_")
        val = latest[col]
        contributions[k] = val

        if val > v:
            overspend[k] = val - v

    total_waste = sum(overspend.values())

    # Narrative
    insight_text = ""

    if overspend:
        worst = max(overspend, key=overspend.get)
        insight_text += f"You are overspending mainly on {worst}. "
    else:
        insight_text += "Your spending is well controlled this month. "

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            insight_text += f"Spending increased by ₹{int(diff)} compared to last month. "
        else:
            insight_text += f"You saved ₹{int(abs(diff))} compared to last month. "

    if total_waste > 0:
        insight_text += f"You can save ₹{int(total_waste)} per month (₹{int(total_waste*12)} yearly) by fixing overspending."

    st.info(insight_text)

    # Top 3 actions
    st.write("### 🎯 Top Actions")
    for k,v in sorted(overspend.items(), key=lambda x:-x[1])[:3]:
        st.write(f"• Reduce {k} by ₹{int(v)}")

    # Score
    score = 100
    score -= min(total_waste//200,30)

    if latest["investment_total"] < 60000:
        score -= 20

    if prev is not None and latest["grand_total"] > prev["grand_total"]:
        score -= 10

    score = max(score,0)

    st.subheader(f"💯 Score: {score}/100")

    # Prediction (trend-based)
    st.write("### 📉 3 Month Forecast")
    if len(df) > 1:
        trend = latest["grand_total"] - prev["grand_total"]
    else:
        trend = 0

    base = latest["grand_total"]

    for i in range(1,4):
        pred = base + (trend*i)
        st.write(f"Month +{i}: ₹{int(pred)}")

    # -----------------------------
    # PDF DOWNLOAD
    # -----------------------------
    if st.button("📄 Download Report"):
        path = create_pdf(month, insight_text)
        with open(path, "rb") as f:
            st.download_button("Download PDF", f, file_name=path)