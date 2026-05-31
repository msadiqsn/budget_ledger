import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# INDIAN NUMBER FORMAT
# -----------------------------
def format_inr(num):
    num = int(num)
    s = str(num)

    if len(s) <= 3:
        return s

    last3 = s[-3:]
    rest = s[:-3]

    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts) + "," + last3

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL = "https://lmlzlilfoudxdtyvuhbz.supabase.co"
SUPABASE_KEY = "sb_publishable_uIw4d9MgIgoYfQkbXgIvgg_vYqGabBz"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# MASTER BUDGET CONFIG
# -----------------------------

FIXED_REF = {
    "rent": 16000,
    "abba": 10000,
    "loan": 10000,
    "ammi": 3000,
    "maid": 3000
}

VARIABLE_REF = {
    "groceries": 9000,
    "outside_food": 5000,
    "miscellaneous": 7000,
    "medical": 3000,
    "transport": 1000,
    "electricity": 1000,
    "wifi": 1000
}

INVESTMENT_REF = {
    "short_term": 10000,
    "sip": 50000,
    "lumpsum": 0
}


# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
.ref-box {
    border:1px solid rgba(128,128,128,0.5);
    padding:6px;
    border-radius:6px;
    text-align:center;
    font-weight:600;
    font-size:13px;
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
        "miscellaneous": var_data["Miscellaneous"],

        "short_term": short_term,
        "lumpsum": lumpsum,
        "withdraw_sip": withdraw_sip,
        "withdraw_lumpsum": withdraw_lumpsum
    }).execute()

def load_data():
    return supabase.table("budget").select("*").execute().data

# -----------------------------
# ROW INPUT
# -----------------------------
def row_input(label, ref, key):
    col1, col2, col3 = st.columns([1.2,1,1])

    with col1:
        st.write(label)

    with col2:
        st.markdown(f'<div class="ref-box">₹{format_inr(ref)}</div>', unsafe_allow_html=True)

    with col3:
        val = st.number_input("", value=ref, step=500, key=key)

    return val

# -----------------------------
# HEADER
# -----------------------------
st.title("💰 Monthly Budget")
# === PAGE NAVIGATION ===
# === DASHBOARD OR DAILY ENTRY ===
#page = st.sidebar.radio(
#    "Navigation",
#    ["Dashboard", "Daily Entry"]
#)

# === TEST NAVIGATION ===
# === SHOW IN MAIN PAGE ===
page = st.radio(
    "Navigation",
    ["Dashboard", "Daily Entry"]
)

# === DEFAULT CURRENT MONTH ===
# === AUTO SELECT CURRENT YEAR ===

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
years = list(range(2024, 2035))

current_month_name = datetime.now().strftime("%B")
current_year = datetime.now().year

month_index = months.index(current_month_name)
year_index = years.index(current_year)

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "Month",
        months,
        index=month_index
    )

with col2:
    selected_year = st.selectbox(
        "Year",
        years,
        index=year_index
    )

month = f"{selected_month} {selected_year}"

# === MONTH NUMBER MAP ===
# === FOR EXPENSE FILTERING ===
month_map = {
    "January":"01",
    "February":"02",
    "March":"03",
    "April":"04",
    "May":"05",
    "June":"06",
    "July":"07",
    "August":"08",
    "September":"09",
    "October":"10",
    "November":"11",
    "December":"12"
}

# === LOAD DAILY EXPENSES ===
# === ALWAYS CREATE DATAFRAME ===
expense_data = supabase.table("expense_log").select("*").execute().data

expense_df = pd.DataFrame(expense_data)

if expense_df.empty:
    expense_df = pd.DataFrame(
        columns=["expense_date", "category", "amount"]
    )
else:
    selected_month_num = month_map[selected_month]

    filter_prefix = f"{selected_year}-{selected_month_num}"

    expense_df = expense_df[
        expense_df["expense_date"]
        .astype(str)
        .str.startswith(filter_prefix)
    ]

# === DAILY ENTRY PAGE ===
# === SIMPLE EXPENSE LOGGER ===
if page == "Daily Entry":

    st.header("➕ Daily Expense Entry")

    # === EXPENSE DATE ===
    # === USER SELECTS DATE ===
    expense_date = st.date_input(
        "Expense Date"
    )

    amount = st.number_input(
        "Amount",
        min_value=0,
        step=10
    )

    category = st.selectbox(
        "Category",
        [
            "Groceries",
            "Outside Food",
            "Miscellaneous",
            "Medical",
            "Transport"
        ]
    )

    notes = st.text_input("Notes")

    if st.button("Save Expense"):

        from datetime import date

        supabase.table("expense_log").insert({
            "expense_date": expense_date.isoformat(),
            "category": category,
            "amount": amount,
            "notes": notes
        }).execute()

        st.success("Expense Saved")

    # === DAILY BUDGET STATUS ===
    # === QUICK REFERENCE ===

    expense_data = supabase.table("expense_log").select("*").execute().data

    expense_df = pd.DataFrame(expense_data)

    if not expense_df.empty:

        current_month = expense_date.strftime("%Y-%m")

        expense_df = expense_df[
            expense_df["expense_date"]
            .astype(str)
            .str.startswith(current_month)
        ]

        grocery_total = expense_df[
            expense_df["category"] == "Groceries"
        ]["amount"].sum()

        food_total = expense_df[
            expense_df["category"] == "Outside Food"
        ]["amount"].sum()

        misc_total = expense_df[
            expense_df["category"] == "Miscellaneous"
        ]["amount"].sum()

        medical_total = expense_df[
            expense_df["category"] == "Medical"
        ]["amount"].sum()

        transport_total = expense_df[
            expense_df["category"] == "Transport"
        ]["amount"].sum()

        st.subheader("🎯 Budget Remaining")

        st.write(
            f"🛒 Groceries: ₹{format_inr(9000 - grocery_total)} left"
        )

        st.write(
            f"🍔 Food: ₹{format_inr(5000 - food_total)} left"
        )

        st.write(
            f"💸 Misc: ₹{format_inr(7000 - misc_total)} left"
        )

        st.write(
            f"🏥 Medical: ₹{format_inr(3000 - medical_total)} left"
        )

        st.write(
            f"🚕 Transport: ₹{format_inr(1000 - transport_total)} left"
        )

    st.stop()

# -----------------------------
# FIXED
# -----------------------------
st.subheader("🏠 Fixed")

rent = row_input("Rent", FIXED_REF["rent"], "rent")
abba = row_input("Abba", FIXED_REF["abba"], "abba")
loan = row_input("Loan", FIXED_REF["loan"], "loan")
ammi = row_input("Ammi", FIXED_REF["ammi"], "ammi")
maid = row_input("Maid", FIXED_REF["maid"], "maid")


fixed_total = rent + abba + loan + ammi + maid

fixed_ref = sum(FIXED_REF.values())

diff_fixed = fixed_total - fixed_ref

if diff_fixed <= 0:
    st.markdown(
        f'<span class="good">Stable foundation 👍 You are within fixed budget (Saved ₹{format_inr(abs(diff_fixed))})</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Fixed costs increased by ₹{format_inr(diff_fixed)} — review commitments</span>',
        unsafe_allow_html=True
    )

# -----------------------------
# VARIABLE
# -----------------------------
st.subheader("📊 Variable")

# === VARIABLE BUDGET TARGETS ===
# === MONTHLY LIMITS ===

grocery_budget = VARIABLE_REF["groceries"]
food_budget = VARIABLE_REF["outside_food"]
misc_budget = VARIABLE_REF["miscellaneous"]
medical_budget = VARIABLE_REF["medical"]
transport_budget = VARIABLE_REF["transport"]

# === AUTO VARIABLE CATEGORIES ===
# === FROM DAILY EXPENSE LOG ===

if expense_df.empty:
    groceries = 0
    outside = 0
    misc = 0
    medical = 0
    transport = 0
else:
    groceries = expense_df[
        expense_df["category"] == "Groceries"
    ]["amount"].sum()

    outside = expense_df[
        expense_df["category"] == "Outside Food"
    ]["amount"].sum()

    misc = expense_df[
        expense_df["category"] == "Miscellaneous"
    ]["amount"].sum()

    medical = expense_df[
        expense_df["category"] == "Medical"
    ]["amount"].sum()

    transport = expense_df[
        expense_df["category"] == "Transport"
    ]["amount"].sum()

# === MANUAL MONTHLY EXPENSES ===
# === ELECTRICITY + WIFI ===

electricity = row_input(
    "Electricity",
    VARIABLE_REF["electricity"],
    "elec"
)

wifi = row_input(
    "WiFi",
    VARIABLE_REF["wifi"],
    "wifi"
)

st.markdown("---")

# === DAILY EXPENSE TOTALS ===
# === AUTO FROM EXPENSE LOG ===

st.metric("🛒 Groceries", f"₹{format_inr(groceries)}")

st.metric("🍔 Outside Food", f"₹{format_inr(outside)}")

st.metric("💸 Miscellaneous", f"₹{format_inr(misc)}")

st.metric("🏥 Medical", f"₹{format_inr(medical)}")

st.metric("🚕 Transport", f"₹{format_inr(transport)}")

variable_total = (
    groceries
    + outside
    + misc
    + medical
    + transport
    + electricity
    + wifi
)

variable_ref = 26000

diff_var = variable_total - variable_ref

if diff_var <= 0:
    saved = abs(diff_var)
    st.markdown(
        f'<span class="good">Excellent control 🔥 Saved ₹{format_inr(saved)} this month (~₹{format_inr(saved*12)}/year impact)</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="bad">Overspending ₹{format_inr(diff_var)} — lifestyle leak detected</span>',
        unsafe_allow_html=True
    )

# === REMAINING BUDGET ===
# === EASY TRACKING ===

st.subheader("🎯 Budget Remaining")

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "🛒 Groceries Left",
        f"₹{format_inr(grocery_budget - groceries)}"
    )

    st.metric(
        "💸 Misc Left",
        f"₹{format_inr(misc_budget - misc)}"
    )

    st.metric(
        "🚕 Transport Left",
        f"₹{format_inr(transport_budget - transport)}"
    )

with c2:
    st.metric(
        "🍔 Food Left",
        f"₹{format_inr(food_budget - outside)}"
    )

    st.metric(
        "🏥 Medical Left",
        f"₹{format_inr(medical_budget - medical)}"
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

# === SHORT TERM INVESTMENT ===
# === REPLACES OLD BISSI ===

short_term = row_input(
    "Short-Term Investment",
    INVESTMENT_REF["short_term"],
    "short_term"
)

sip = row_input(
    "SIP",
    INVESTMENT_REF["sip"],
    "sip"
)

lumpsum = row_input(
    "Lumpsum Investment",
    INVESTMENT_REF["lumpsum"],
    "lumpsum"
)

# === UPDATED INVESTMENT TOTAL ===
# === INCLUDES SHORT TERM + SIP + LUMPSUM ===
investment_total = short_term + sip + lumpsum

investment_ref = sum(INVESTMENT_REF.values())

if investment_total > investment_ref:
    extra = investment_total - investment_ref
    st.markdown(
        f'<span class="good">🚀 Strong wealth building! Extra ₹{format_inr(extra)} invested — this accelerates your future</span>',
        unsafe_allow_html=True
    )
elif investment_total == investment_ref:
    st.markdown(
        '<span class="good">Disciplined investing 👍 you are on the right path</span>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<span class="warn">Increase investment by ₹{format_inr(investment_ref - investment_total)} to stay on track</span>',
        unsafe_allow_html=True
    )

# === DEFAULT WITHDRAW VALUES ===
# === ENSURE VARIABLES EXIST ===
withdraw_sip = 0
withdraw_lumpsum = 0

# === WITHDRAW SECTION ===
# === USER SELECTS SOURCE ===
st.subheader("💸 Withdraw")

col1, col2 = st.columns(2)

with col1:
    withdraw_type = st.selectbox("Withdraw From", ["SIP", "Lumpsum"])

with col2:
    withdraw_amount = st.number_input("Amount", min_value=0, step=1000)

if st.button("Withdraw"):
    if withdraw_type == "SIP":
        withdraw_sip = withdraw_amount
    else:
        withdraw_lumpsum = withdraw_amount

    st.success("Withdrawal recorded")


# === RESET SHORT TERM ===
# === SIMPLE RESET BUTTON ===
if st.button("Reset Short-Term Investment"):
    short_term = 0
    st.success("Short-Term Investment Reset")



# -----------------------------
# TOTAL
# -----------------------------
grand_total = fixed_total + variable_total + investment_total
st.metric("💰 Total", f"₹{format_inr(grand_total)}")

# === DAILY EXPENSE SUMMARY ===
# === VERIFY MONTHLY TOTALS ===

if not expense_df.empty:

    st.subheader("🧾 Daily Expense Summary")

    grocery_total = expense_df[
        expense_df["category"] == "Groceries"
    ]["amount"].sum()

    food_total = expense_df[
        expense_df["category"] == "Outside Food"
    ]["amount"].sum()

    misc_total = expense_df[
        expense_df["category"] == "Miscellaneous"
    ]["amount"].sum()

    medical_total = expense_df[
        expense_df["category"] == "Medical"
    ]["amount"].sum()

    transport_total = expense_df[
        expense_df["category"] == "Transport"
    ]["amount"].sum()

    # === ROW 1 ===
    # === GROCERIES + FOOD ===
    c1, c2 = st.columns(2)

    with c1:
        st.metric("🛒 Groceries", f"₹{format_inr(grocery_total)}")

    with c2:
        st.metric("🍔 Food", f"₹{format_inr(food_total)}")

    # === ROW 2 ===
    # === MISC + MEDICAL ===
    c3, c4 = st.columns(2)

    with c3:
        st.metric("💸 Misc", f"₹{format_inr(misc_total)}")

    with c4:
        st.metric("🏥 Medical", f"₹{format_inr(medical_total)}")

    # === ROW 3 ===
    # === TRANSPORT ===
    c5, c6 = st.columns(2)

    with c5:
        st.metric("🚕 Transport", f"₹{format_inr(transport_total)}")


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

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None



    # === FIX LONG TERM SUMMARY ===
    # === CALCULATE SIP FROM INVESTMENT TOTAL ===
    total_sip = (
        df["investment_total"]
        - df["short_term"]
        - df["lumpsum"]
    ).sum() - df["withdraw_sip"].sum()

    total_lumpsum = (
        df["lumpsum"].sum()
        - df["withdraw_lumpsum"].sum()
    )

    st.subheader("📊 Long-Term Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total SIP", f"₹{format_inr(total_sip)}")

    with col2:
        st.metric("Total Lumpsum", f"₹{format_inr(total_lumpsum)}")

    # -----------------------------
    # 📊 FINANCIAL SCORE
    # -----------------------------
    st.subheader("📊 Financial Score")

    score = 100

    if latest["variable_total"] > 23000:
        score -= 25
    else:
        score += 5

    if sip < 50000:
        score -= 25
    else:
        score += 5

    if prev is not None:
        if latest["grand_total"] > prev["grand_total"]:
            score -= 15
        else:
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


# === ADVANCED WEALTH TABLE (WITH HISTORY) ===
    # === USES DB DATA + FUTURE PROJECTION ===
    st.subheader("📊 Wealth Accumulation (12 Years)")

    r = 12/100/12

    df_sorted = df.sort_values("created_at")

    # === SIP HISTORY ===
# === REMOVE SHORT TERM & LUMPSUM ===
    # === FIX SIP ESTIMATION ===
# === REMOVE SHORT TERM & LUMPSUM ===
    df_sorted["sip_est"] = (
        df_sorted["investment_total"]
        - df_sorted["short_term"]
        - df_sorted["lumpsum"]
    )  # assuming bissi = 10k

    total_months_done = len(df_sorted)

    def simulate(step):
        total = 0
        monthly = sip

        results = []

        for year in range(1, 13):
            for m in range(12):
                month_index = (year - 1) * 12 + m

                if month_index < total_months_done:
                    # Use historical SIP
                    invest = df_sorted.iloc[month_index]["sip_est"]
                else:
                    invest = monthly

                total = total * (1 + r) + invest

            results.append(total)
            monthly *= (1 + step)

        return results

    flat = simulate(0)
    s5 = simulate(0.05)
    s10 = simulate(0.10)
    s15 = simulate(0.15)

    table = pd.DataFrame({
        "Year": list(range(1, 13)),
        "Flat SIP": [f"₹{format_inr(x)}" for x in flat],
        "5% Step-up": [f"₹{format_inr(x)}" for x in s5],
        "10% Step-up": [f"₹{format_inr(x)}" for x in s10],
        "15% Step-up": [f"₹{format_inr(x)}" for x in s15],
    })

    st.table(table)


# === SIP GROWTH TABLE ===
    # === YEAR-WISE STEP-UP AMOUNTS ===
    st.subheader("📈 SIP Growth (Yearly)")

    sip_base = sip

    rows = []

    s5_val = sip_base
    s10_val = sip_base
    s15_val = sip_base

    for year in range(1, 13):
        rows.append({
            "Year": year,
            "5%": f"₹{format_inr(s5_val)}",
            "10%": f"₹{format_inr(s10_val)}",
            "15%": f"₹{format_inr(s15_val)}"
        })

        s5_val *= 1.05
        s10_val *= 1.10
        s15_val *= 1.15

    st.table(pd.DataFrame(rows))


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
    st.subheader("🤖 Smart Insights")

    summary = []

    if prev is not None:
        diff = latest["grand_total"] - prev["grand_total"]
        if diff > 0:
            summary.append(f"Spending increased by ₹{format_inr(diff)}")
        else:
            summary.append(f"You improved savings by ₹{format_inr(abs(diff))}")

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
        total_waste = sum(overspend.values())
        summary.append(f"Potential saving ₹{format_inr(total_waste)}/month (~₹{format_inr(total_waste*12)}/year)")

    for s in summary:
        st.write("•", s)

    # -----------------------------
    # ACTION PLAN
    # -----------------------------
    st.markdown("### 🎯 Action Plan")

    action_given = False

    if overspend:
        action_given = True
        for k, v in sorted(overspend.items(), key=lambda x: -x[1]):
            st.write(f"Reduce {k} by ₹{format_inr(v)}")

    if latest["investment_total"] < 60000:
        action_given = True
        st.write("Increase SIP to improve long-term wealth")

    if not action_given:
        st.success("All areas look good — maintain this discipline 👍")