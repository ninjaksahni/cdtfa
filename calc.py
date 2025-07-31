import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Amazon Tax Sales Analyzer", layout="centered")
st.title("📊 Amazon Tax Sales Analyzer")

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

    # Summary cards
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

    # Pie Chart
    st.markdown("### 🥧 Sales Distribution")
    fig, ax = plt.subplots()
    ax.pie([california_sales, other_sales], labels=["California", "Other States"], autopct='%1.1f%%', startangle=90, colors=['#0072c6', '#2e8b57'])
    ax.axis('equal')
    st.pyplot(fig)

    # Data table
    st.markdown("---")
    st.markdown("### 🧹 Cleaned Dataset (Tax > 0)")
    st.dataframe(df_cleaned.drop(columns=['state_lower']), use_container_width=True)

    # Generate PDF
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Amazon Sales Tax Report", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        date_str = datetime.now().strftime("%B %d, %Y")
        pdf.cell(200, 10, f"Date: {date_str}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Summary", ln=True)

        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"California Sales: ${california_sales:,.2f}", ln=True)
        pdf.cell(200, 10, f"Other States Sales: ${other_sales:,.2f}", ln=True)
        pdf.cell(200, 10, f"Total Sales: ${total_sales:,.2f}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Note", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, "This summary is based on the uploaded CSV data and includes only records where tax collected is greater than zero.")

        # Output PDF to BytesIO
        output = io.BytesIO()
        pdf.output(output)
        return output

    # Button to download
    st.markdown("---")
    st.markdown("### 📥 Download Report")
    pdf_data = generate_pdf()
    st.download_button(
        label="📄 Download PDF Summary",
        data=pdf_data,
        file_name=f"amazon_tax_summary_{datetime.now().strftime('%Y_%m_%d')}.pdf",
        mime="application/pdf"
    )
