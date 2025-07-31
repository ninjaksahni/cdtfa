import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Amazon Tax Sales Analyzer", layout="centered")
st.title("📊 Amazon Tax Sales Analyzer")

# Custom styles
st.markdown("""
<style>
.summary-card {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 20px;
    text-align: center;
}
.summary-card h3 {
    color: #444;
    margin-bottom: 10px;
}
.summary-card h1 {
    font-size: 2.5rem;
    margin: 0;
}
.date-banner {
    background-color: #f1f3f5;
    padding: 10px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    font-weight: 600;
    font-size: 1.1rem;
    color: #333;
    text-align: center;
}
.total-banner {
    background-color: #fff3cd;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin-top: 20px;
}
.total-banner h2 {
    color: #856404;
}
.total-banner h1 {
    color: #d48806;
    font-size: 3rem;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("Upload a CSV with your Amazon sales tax data and get instant summaries by state.")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your CSV file", type="csv")

if uploaded_file is not None:
    # Read and clean data
    df = pd.read_csv(uploaded_file)
    required_columns = ['Ship_To_State', 'Total_Tax_Collected_By_Amazon', 'TaxExclusive_Selling_Price']
    df = df[required_columns]

    df['Total_Tax_Collected_By_Amazon'] = pd.to_numeric(df['Total_Tax_Collected_By_Amazon'], errors='coerce')
    df['TaxExclusive_Selling_Price'] = pd.to_numeric(df['TaxExclusive_Selling_Price'], errors='coerce')
    df_cleaned = df[df['Total_Tax_Collected_By_Amazon'].fillna(0) != 0]

    # Classify state
    df_cleaned['state_lower'] = df_cleaned['Ship_To_State'].astype(str).str.strip().str.lower()
    california_states = ['ca', 'california']

    # Compute totals
    california_sales = df_cleaned[df_cleaned['state_lower'].isin(california_states)]['TaxExclusive_Selling_Price'].sum()
    other_sales = df_cleaned[~df_cleaned['state_lower'].isin(california_states)]['TaxExclusive_Selling_Price'].sum()
    total_sales = california_sales + other_sales

    # Static date (bolded) at top of summary
    st.markdown(f"""
    <div class="date-banner">
        📅 <strong>Date:</strong> <strong>July 31, 2025</strong>
    </div>
    """, unsafe_allow_html=True)

    # Summary section
    st.markdown("## 🧾 Summary Totals")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="summary-card">
            <h3>🇺🇸 California Sales</h3>
            <h1 style="color:#0072c6;">${california_sales:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="summary-card">
            <h3>🌎 Other States Sales</h3>
            <h1 style="color:#2e8b57;">${other_sales:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="total-banner">
        <h2>💰 Total Sales</h2>
        <h1>${total_sales:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Pie Chart
    st.markdown("### 🥧 Sales Distribution")
    fig, ax = plt.subplots()
    ax.pie(
        [california_sales, other_sales],
        labels=["California", "Other States"],
        autopct='%1.1f%%',
        startangle=90,
        colors=['#0072c6', '#2e8b57']
    )
    ax.axis('equal')
    st.pyplot(fig)

    # Top 10 states by sales
    st.markdown("### 🏆 Top 10 States by Sales")
    top_states = (
        df_cleaned.groupby('Ship_To_State')['TaxExclusive_Selling_Price']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top_states.columns = ['State', 'Total Sales']
    top_states['Total Sales'] = top_states['Total Sales'].map('${:,.2f}'.format)
    st.table(top_states)

    # Data table in expander
    with st.expander("📂 View Cleaned Dataset (Tax > 0)", expanded=False):
        st.dataframe(df_cleaned.drop(columns=['state_lower']), use_container_width=True)
