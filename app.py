import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL =  "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY =  "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# STYLE (FINAL POLISH)
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
    padding:14px;
    border-radius:12px;
    text-align:center;
    color:white;
    font-weight:bold;
}

.blue { background:#4A90E2; }
.orange { background:#F5A623; }
.green { background:#7ED321; }
.red { background:#D0021B; }

.badge {
    padding:6px 10px;
    border-radius:8px;
    font-size:12px;
    display:inline-block;
    margin-right:6px;
}

.good { background:#E8F5E9; color:#2E7D32; }
.bad { background:#FFEBEE; color:#C62828; }

.big-btn button {
    width:100%;
    height:50px;
    font-size:16px;
    border-radius:10px;
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
# DATA
# -----------------------------
variable_budget = {
    "Groceries": 9000,
    "Electricity": 1000,
    "Outside Food": 5000,
    "Miscellaneous": 7000
}

fixed_expenses = {
    "Rent":16000,"WiFi":1000,"Abba":10000,"Loan":10000,"Ammi":3000,"Maid":3000
}

investments = {"Bissi":10000,"SIP":50000}

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Budget Dashboard")
month = st.text_input("Month", value=datetime.now().strftime("%B %Y"))

# -----------------------------
# INPUTS
# -----------------------------
fixed_total=0
for k,v in fixed_expenses.items():
    if st.checkbox(f"{k} ₹{v}", key=k):
        fixed_total+=v

variable_total=0
var_data={}
for k,v in variable_budget.items():
    val=st.number_input(k,value=v,step=100,key=k+"_var")
    variable_total+=val
    var_data[k]=val

investment_total=0
for k,v in investments.items():
    if st.checkbox(f"{k} ₹{v}", key=k+"_inv"):
        investment_total+=v

grand_total=fixed_total+variable_total+investment_total

# -----------------------------
# SAVE BUTTON
# -----------------------------
st.markdown('<div class="big-btn">', unsafe_allow_html=True)
if st.button("💾 Save Month Data"):
    save_to_db(month,fixed_total,variable_total,investment_total,grand_total,var_data)
    st.success("Saved successfully")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
data=load_data()

if data:
    df=pd.DataFrame(data).sort_values("created_at")
    latest=df.iloc[-1]
    prev=df.iloc[-2] if len(df)>1 else None

    # -----------------------------
    # KPI STRIP
    # -----------------------------
    col1,col2,col3,col4=st.columns(4)

    with col1:
        st.markdown(f'<div class="kpi blue">₹{int(latest["grand_total"])}<br>Total</div>',unsafe_allow_html=True)

    with col2:
        if prev is not None:
            diff=latest["grand_total"]-prev["grand_total"]
            color="green" if diff<0 else "red"
            st.markdown(f'<div class="kpi {color}">₹{int(diff)}<br>Change</div>',unsafe_allow_html=True)

    cat_map={"Groceries":"groceries","Electricity":"electricity","Outside Food":"outside_food","Miscellaneous":"miscellaneous"}
    biggest=max(cat_map,key=lambda k:latest[cat_map[k]])

    with col3:
        st.markdown(f'<div class="kpi orange">{biggest}<br>Top</div>',unsafe_allow_html=True)

    score=100
    if latest["variable_total"]>22000: score-=20
    if latest["investment_total"]<60000: score-=20

    with col4:
        st.markdown(f'<div class="kpi blue">{score}<br>Score</div>',unsafe_allow_html=True)

    # -----------------------------
    # CATEGORY % (LIKE REAL APPS)
    # -----------------------------
    st.subheader("📊 Category Breakdown")

    total_var=latest["variable_total"]

    for k,col in cat_map.items():
        val=latest[col]
        percent=(val/total_var*100) if total_var else 0

        badge_class="bad" if val>variable_budget[k] else "good"

        st.markdown(f"""
        <div class="card">
            <b>{k}</b><br>
            ₹{int(val)} ({percent:.1f}%)
            <span class="badge {badge_class}">
                {"Overspend" if val>variable_budget[k] else "Good"}
            </span>
        </div>
        """,unsafe_allow_html=True)

    # -----------------------------
    # TREND
    # -----------------------------
    st.subheader("📈 Trend")
    st.line_chart(df.set_index("month")["grand_total"])

    # -----------------------------
    # PREDICTION
    # -----------------------------
    st.subheader("🔮 Prediction")

    trend=(latest["grand_total"]-prev["grand_total"]) if prev is not None else 0

    for i in range(1,4):
        st.write(f"Month +{i}: ₹{int(latest['grand_total']+(trend*i))}")

    # -----------------------------
    # AI SUMMARY
    # -----------------------------
    st.subheader("🤖 AI Insight")

    overspend={k:latest[k.lower().replace(" ","_")]-v for k,v in variable_budget.items() if latest[k.lower().replace(" ","_")]>v}

    text=""

    if overspend:
        worst=max(overspend,key=overspend.get)
        text+=f"🚨 Biggest issue: {worst}. "

    if prev is not None:
        diff=latest["grand_total"]-prev["grand_total"]
        text+=f"{'Increased' if diff>0 else 'Saved'} ₹{abs(int(diff))}. "

    total_waste=sum(overspend.values())
    if total_waste>0:
        text+=f"Save ₹{int(total_waste)}/month (~₹{int(total_waste*12)}/year)."

    st.info(text)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    if overspend:
        st.subheader("🎯 Action Plan")

        for k,v in sorted(overspend.items(),key=lambda x:-x[1]):
            st.write(f"Reduce {k} by ₹{int(v)}")