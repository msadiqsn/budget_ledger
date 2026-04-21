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
# COMPACT ROW
# -----------------------------
def row_input(label, ref, key):

    col1, col2, col3 = st.columns([1.2, 1, 1])

    # LABEL
    with col1:
        st.markdown(f"**{label}**")

    # REFERENCE
    with col2:
        st.markdown(f"""
        <div style="
            background:#E6ECFF;
            padding:6px;
            border-radius:6px;
            text-align:center;
            font-weight:600;
            font-size:13px;
        ">
            ₹{ref}
        </div>
        """, unsafe_allow_html=True)

    # INPUT
    with col3:
        val = st.number_input("", value=ref, step=500, key=key)

    # SMALL TEXT (no big gap)
    if val <= ref:
        st.caption(f"Saved ₹{ref - val}")
    else:
        st.caption(f"Overspent ₹{val - ref}")

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
fixed_ref = 43000

st.write(
    f"**Fixed → Ref ₹{fixed_ref} | Actual ₹{fixed_total}** "
    f"{'Overspent ₹'+str(fixed_total-fixed_ref) if fixed_total>fixed_ref else 'Saved ₹'+str(fixed_ref-fixed_total)}"
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

st.write(
    f"**Variable → Ref ₹{variable_ref} | Actual ₹{variable_total}** "
    f"{'Overspent ₹'+str(variable_total-variable_ref) if variable_total>variable_ref else 'Saved ₹'+str(variable_ref-variable_total)}"
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

if investment_total < investment_ref:
    st.warning(f"Invest ₹{investment_ref-investment_total} more to reach goal")
else:
    st.success("Investment on track")

# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("Total", f"₹{grand_total}")

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
    # AI INSIGHTS
    # -----------------------------
    st.subheader("🤖 Insights")

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df)>1 else None

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        st.write("Increase" if diff>0 else "Saved", f"₹{abs(int(diff))}")

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
        total = sum(overspend.values())

        st.write(f"Main issue: {worst}")
        st.write(f"Save ₹{total}/month (~₹{total*12}/year)")

    st.write("Tip: Reduce eating out & track misc expenses")
