import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# Only load .env file if not running in Docker
if not os.getenv('DOCKER_ENV'):
    from dotenv import load_dotenv
    load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.models.invoice_type_input import InvoiceType
from app.agents.anomaly_detector import AnomalyDetector
from app.agents.invoices_extractor import InvoicesExtractor
from app.agents.financial_analysis_agent import FinancialAnalysisAgent

# Page configuration
st.set_page_config(
    page_title="Invoice Anomaly Detection",
    page_icon="📊",
    layout="centered"  # Use "centered" to reduce unused right-side space
)

# Title
st.title("📊 Invoice Anomaly Detection")
st.info(
    f"**Institution:** `tatooine_mx_fiscal`  &nbsp;&nbsp;  "
    f"**Username:** `PMO010101000`",
    icon="🛡️"
)

st.markdown("Detect anomalies in invoice data based on type and date range")

# Sidebar for filters
st.sidebar.header("Filters")
extractor = InvoicesExtractor()

# Invoice type selector
invoice_type = st.sidebar.selectbox(
    "Select Invoice Type:",
    options=[InvoiceType.INFLOW.value, InvoiceType.OUTFLOW.value],
    index=0
)
min_date, max_date = extractor.get_date_range(InvoiceType(invoice_type))

# Date selectors
st.sidebar.subheader("Date Range")
from_date = st.sidebar.date_input(
    "From Date:",
    value=min_date,
    help="Select the start date for analysis"
)
to_date = st.sidebar.date_input(
    "To Date:",
    value=max_date,
    help="Select the end date for analysis"
)

# Button (full width in sidebar)
detect_button = st.sidebar.button("🔎 Detect Anomalies")

# Validate date range
if from_date > to_date:
    st.sidebar.error("From date must be before to date!")

# Initialize session state
if 'anomalies_detected' not in st.session_state:
    st.session_state.anomalies_detected = False
if 'anomalies_df' not in st.session_state:
    st.session_state.anomalies_df = pd.DataFrame()
if 'invoices_df' not in st.session_state:
    st.session_state.invoices_df = pd.DataFrame()

# Only run extraction and detection on button click and valid dates
if detect_button and from_date <= to_date:
    with st.spinner("Detecting anomalies..."):
        selected_type = InvoiceType(invoice_type)
        invoices_df = extractor.extract(str(from_date), str(to_date), selected_type)

        anomaly_detector = AnomalyDetector()
        anomalies = anomaly_detector.detect(invoices_df)
        anomalies_df = pd.DataFrame(anomalies.model_dump()['anomalies'])

        if not anomalies_df.empty:
            anomalies_df.rename(columns={"invoice_date": "date"}, inplace=True)
            st.session_state.anomalies_df = anomalies_df
            st.session_state.invoices_df = invoices_df
            st.session_state.anomalies_detected = True
        else:
            st.session_state.anomalies_detected = False

# Display results if anomalies were detected
if st.session_state.anomalies_detected and not st.session_state.anomalies_df.empty:
    data = st.session_state.invoices_df.copy()
    data['date'] = pd.to_datetime(data['date'])
    anomalies_df = st.session_state.anomalies_df.copy()
    anomalies_df['date'] = pd.to_datetime(anomalies_df['date'])

    fig = px.bar(
        data,
        x="date",
        y="total_amount",
        color="invoice_type",
        barmode="group",
        labels={"date": "Date", "total_amount": "Total Amount", "invoice_type": "Invoice Type"},
        title="Total Amount by Invoice Type Over Time"
    )

    fig.add_scatter(
        x=anomalies_df['date'],
        y=anomalies_df['total_amount'],
        mode='markers',
        marker=dict(color='red', size=12, symbol='circle'),
        name='Anomaly'
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Amount",
        legend_title="Invoice Type",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(anomalies_df, use_container_width=True)

    # Selector for anomaly
    selected_anomaly = st.selectbox(
        "Select an anomaly to analyze:",
        anomalies_df['date'].dt.strftime('%Y-%m-%d').astype(str) + " | " + anomalies_df['invoice_type'],
        index=0
    )
    analyze_button = st.button("Analyze Selected Anomaly", key="analyze_btn")

    if analyze_button:
        sel_date, sel_type = selected_anomaly.split(" | ")
        
        with st.spinner(f"Analyzing invoices for {sel_type} on {sel_date}..."):
            financial_agent = FinancialAnalysisAgent()
            anomaly_data = anomalies_df[(anomalies_df['date'].dt.strftime('%Y-%m-%d').astype(str) == sel_date) & (anomalies_df['invoice_type'] == sel_type)]
            
            summary = financial_agent.run(anomaly_data.to_markdown(), invoice_type)
        
        st.write(summary['messages'][-1].content)
elif detect_button and st.session_state.anomalies_df.empty:
    st.warning("No anomalies detected for the selected criteria.")
elif detect_button:
    st.warning("No data or invalid selection.")