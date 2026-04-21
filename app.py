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
# UI
# -----------------------------
st.title("💰 Monthly Budget")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# ROW WITH PROGRESS BAR
# -----------------------------
def row_input(label, ref, key):
    col1, col2 = st.columns([1,2], gap="small")

    with col1:
        st.markdown(f"""
        <div style="
            background:#EEF3FF;
            padding:12px;
            border-radius:10px;
            text-align:center;
            font-weight:bold;
        ">
            ₹{ref}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        val = st.number_input(label, value=ref, step=500, key=key)

    # progress logic
    percent = val / ref if ref else 0

    if percent <= 1:
        st.progress(percent)
        st.markdown(f"<span style='color:green;'>₹{ref - val} saved</span>", unsafe_allow_html=True)
    else:
        st.progress(1.0)
        st.markdown(f"<span style='color:red;'>Overspent ₹{val - ref}</span>", unsafe_allow_html=True)

    return val

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

# -----------------------------
# VARIABLE (wifi separate)
# -----------------------------
st.subheader("📊 Variable")

groceries = row_input("Groceries",9000,"gro")
electricity = row_input("Electricity",1000,"elec")
wifi = row_input("WiFi",1000,"wifi")
outside = row_input("Outside Food",5000,"out")
misc = row_input("Miscellaneous",7000,"misc")

variable_total = groceries + electricity + wifi + outside + misc

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
# LOAD DATA
# -----------------------------
data = load_data()

if data:
    df = pd.DataFrame(data).sort_values("created_at")

    # -----------------------------
    # CHART
    # -----------------------------
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
    # AI INSIGHTS
    # -----------------------------
    st.subheader("🤖 Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    text = ""

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            text += f"📈 Increased ₹{int(diff)}. "
        else:
            text += f"📉 Saved ₹{int(abs(diff))}. "

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
        text += f"🚨 Main issue: {worst}. "

        total_waste = sum(overspend.values())
        text += f"Save ₹{int(total_waste)}/month (~₹{int(total_waste*12)}/year). "

    if prev is not None:
        trend = latest["grand_total"] - prev["grand_total"]
        text += f"Next month ~₹{int(latest['grand_total'] + trend)}."

    st.info(text)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.subheader("🎯 Action Plan")

        for k,v in sorted(overspend.items(), key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")