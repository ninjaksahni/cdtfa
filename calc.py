import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Tax Sales Analyzer", layout="centered")
st.title("📊 Amazon Tax Sales Analyzer")

st.markdown("Upload a CSV with your Amazon sales tax data and get instant summaries by state.")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your CSV file", type="csv")

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Keep only required columns
    required_columns = ['Ship_To_State', 'Total_Tax_Collected_By_Amazon', 'TaxExclusive_Selling_Price']
    df = df[required_columns]

    # Convert to numeric
    df['Total_Tax_Collected_By_Amazon'] = pd.to_numeric(df['Total_Tax_Collected_By_Amazon'], errors='coerce')
    df['TaxExclusive_Selling_Price'] = pd.to_numeric(df['TaxExclusive_Selling_Price'], errors='coerce')

    # Drop rows where tax is 0 or NaN
    df_cleaned = df[df['Total_Tax_Collected_By_Amazon'].fillna(0) != 0]

    # Normalize state names
    df_cleaned['state_lower'] = df_cleaned['Ship_To_State'].astype(str).str.strip().str.lower()
    california_states = ['ca', 'california']

    # Compute totals
    california_sales = df_cleaned[df_cleaned['state_lower'].isin(california_states)]['TaxExclusive_Selling_Price'].sum()
    other_sales = df_cleaned[~df_cleaned['state_lower'].isin(california_states)]['TaxExclusive_Selling_Price'].sum()
    total_sales = california_sales + other_sales

    # Display summary with BIG FIGURES
    st.markdown("---")
    st.markdown("## 🧾 Summary Totals")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style="background-color:#f0f8ff;padding:25px;border-radius:12px">
                <h3 style="color:#333;">California Sales</h3>
                <h1 style="color:#0072c6;">${california_sales:,.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color:#f0fff0;padding:25px;border-radius:12px">
                <h3 style="color:#333;">Other States Sales</h3>
                <h1 style="color:#2e8b57;">${other_sales:,.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background-color:#fff3cd;padding:30px;border-radius:12px;margin-top:20px;">
            <h2 style="color:#856404;text-align:center;">💰 Total Sales</h2>
            <h1 style="color:#d48806;text-align:center;">${total_sales:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Display filtered table
    st.markdown("---")
    st.markdown("### 🧹 Cleaned Dataset (Tax > 0)")
    st.dataframe(df_cleaned.drop(columns=['state_lower']), use_container_width=True)