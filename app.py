import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

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
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
years = list(range(2024, 2035))

col1, col2 = st.columns(2)
with col1:
    selected_month = st.selectbox("Month", months)
with col2:
    selected_year = st.selectbox("Year", years)

month = f"{selected_month} {selected_year}"

# -----------------------------
# ROW INPUT
# -----------------------------
def row_input(label, ref, key):
    col1, col2, col3 = st.columns([1.2,1,1])
    with col1:
        st.write(label)
    with col2:
        st.write(f"₹{ref}")
    with col3:
        val = st.number_input("", value=ref, step=500, key=key)
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
# VARIABLE
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
st.metric("💰 Total", f"₹{grand_total}")

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
    prev = df.iloc[-2] if len(df) > 1 else None

    # -----------------------------
    # 📊 FINANCIAL SCORE
    # -----------------------------
    st.subheader("📊 Financial Score")

    score = 100

    if latest["variable_total"] > 23000:
        score -= 25

    if latest["investment_total"] < 60000:
        score -= 25

    if prev is not None and latest["grand_total"] > prev["grand_total"]:
        score -= 15

    if latest["variable_total"] < 20000:
        score += 5

    score = max(0, min(100, score))

    if score >= 90:
        status = "Excellent 🚀"
    elif score >= 75:
        status = "Good 👍"
    elif score >= 60:
        status = "Average ⚠️"
    else:
        status = "Needs Attention 🚨"

    st.metric("Score", score)
    st.write(status)

    # -----------------------------
    # 🎯 GOAL TRACKING
    # -----------------------------
    st.subheader("🎯 Wealth Goal Tracker")

    target = 30000000  # 3 Cr
    monthly_invest = latest["investment_total"]
    years = 10
    rate = 12/100/12

    future_value = monthly_invest * (((1+rate)**(years*12)-1)/rate)

    st.write(f"Target: ₹{target}")
    st.write(f"Projected: ₹{int(future_value)}")

    gap = target - future_value

    if gap > 0:
        required = target / (((1+rate)**(years*12)-1)/rate)
        st.warning(f"Need ₹{int(required)} per month to reach goal")
    else:
        st.success("On track to reach goal 🎉")

    # -----------------------------
    # AI INSIGHTS
    # -----------------------------
    st.subheader("🤖 Insights")

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        st.write("Increased" if diff>0 else "Saved", f"₹{abs(int(diff))}")

    if latest["outside_food"] > 5000:
        st.write("Reduce outside food spending")

    if latest["miscellaneous"] > 7000:
        st.write("Track miscellaneous expenses")

    if latest["investment_total"] > 60000:
        st.write("Excellent investment habit")
