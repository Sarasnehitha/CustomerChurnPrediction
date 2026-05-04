import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from utils import preprocess_data, encode_data, get_kpis
import os

# Set page config
st.set_page_config(
    page_title="Churn Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Metric card styling - Glassmorphism */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Heading colors and fonts */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar customization */
    section[data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, #1e3d59 0%, #111d2b 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 3rem;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛠 Settings")
st.sidebar.markdown("Upload your CSV file for analysis.")

sidebar_upload = st.sidebar.file_uploader("Choose a CSV file", type="csv", key="sidebar_uploader")

# Initialize session state
if 'show_analytics' not in st.session_state:
    st.session_state['show_analytics'] = False
if 'uploaded_file_name' not in st.session_state:
    st.session_state['uploaded_file_name'] = None
if 'current_df' not in st.session_state:
    st.session_state['current_df'] = None

# Logic to handle uploads from either uploader
active_upload = sidebar_upload

# If sidebar is empty, check main uploader via session state (handled in the 'else' block below)

def handle_new_file(file):
    if file is not None:
        if st.session_state['uploaded_file_name'] != file.name:
            st.session_state['uploaded_file_name'] = file.name
            st.session_state['current_df'] = pd.read_csv(file)
            st.session_state['show_analytics'] = False # Reset for new file

if active_upload:
    handle_new_file(active_upload)

df_raw = st.session_state['current_df']

if df_raw is not None and st.session_state['show_analytics']:
    # Show Analytics Dashboard
    # Add a reset button to sidebar
    if st.sidebar.button("🔄 Reset View"):
        st.session_state['show_analytics'] = False
        st.rerun()

    # Title
    st.title("📊 Customer Churn Analytics Dashboard")
    st.markdown("Analyze customer behavior and identify churn patterns with interactive visualizations.")

    # Preprocess
    df_clean = preprocess_data(df_raw)
    
    # KPIs
    total_cust, churn_rate, avg_charges = get_kpis(df_clean)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Total Customers", f"{total_cust:,}")
    with col2:
        st.metric("📉 Churn Rate", f"{churn_rate:.1f}%", delta=f"{-churn_rate:.1f}%", delta_color="inverse")
    with col3:
        st.metric("💳 Avg Monthly Charges", f"${avg_charges:.2f}")

    st.markdown("---")

    # Layout: Analytics Sections
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("🎯 Churn Distribution")
        fig_pie = px.pie(
            df_clean, 
            names='Churn', 
            title='Proportion of Churned vs. Retained Customers',
            hole=0.4,
            color='Churn',
            color_discrete_map={0: '#2ecc71', 1: '#e74c3c'},
            labels={'0': 'Retained', '1': 'Churned'}
        )
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with row1_col2:
        st.subheader("⏳ Tenure vs. Churn")
        fig_hist = px.histogram(
            df_clean, 
            x='Tenure_Months', 
            color='Churn',
            barmode='overlay',
            marginal='box',
            title='Customer Tenure (Months) by Churn Status',
            color_discrete_map={0: '#2ecc71', 1: '#e74c3c'},
            labels={'0': 'Retained', '1': 'Churned'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("📜 Contract Type Analysis")
        contract_churn = df_clean.groupby(['Contract_Type', 'Churn']).size().reset_index(name='Count')
        fig_contract = px.bar(
            contract_churn, 
            x='Contract_Type', 
            y='Count', 
            color='Churn',
            title='Churn Count by Contract Type',
            barmode='group',
            color_discrete_map={0: '#2ecc71', 1: '#e74c3c'}
        )
        st.plotly_chart(fig_contract, use_container_width=True)

    with row2_col2:
        st.subheader("🌐 Internet Service Analysis")
        internet_churn = df_clean.groupby(['Internet_Service', 'Churn']).size().reset_index(name='Count')
        fig_internet = px.bar(
            internet_churn, 
            x='Internet_Service', 
            y='Count', 
            color='Churn',
            title='Churn Count by Internet Service',
            barmode='group',
            color_discrete_map={0: '#2ecc71', 1: '#e74c3c'}
        )
        st.plotly_chart(fig_internet, use_container_width=True)

    st.markdown("---")
    
    # Correlation Heatmap
    st.subheader("🔗 Feature Correlation Matrix")
    df_encoded = encode_data(df_clean)
    corr = df_encoded.corr()
    
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Correlation Heatmap (Numeric & Encoded Features)",
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Data Preview Section
    with st.expander("👀 View Raw Data Preview"):
        st.dataframe(df_raw.head(50))

else:
    # Welcome / Upload Page / Button Page
    st.title("🚀 Welcome to Churn Analytics")
    st.markdown("""
        ### Get started by uploading your customer data.
        Analyze retention, discover churn drivers, and visualize patterns in seconds.
    """)
    
    # Show main uploader if no data yet
    main_upload = st.file_uploader("Upload your CSV file here", type="csv", key="main_uploader")
    
    if main_upload:
        handle_new_file(main_upload)
        
    # If a file is currently "active" (either from sidebar or main uploader)
    if st.session_state['current_df'] is not None:
        st.success(f"✅ File '{st.session_state['uploaded_file_name']}' loaded!")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("📊 Show Analytics", type="primary"):
                st.session_state['show_analytics'] = True
                st.rerun()
        with col_btn2:
            if st.button("🗑 Clear File"):
                st.session_state['current_df'] = None
                st.session_state['uploaded_file_name'] = None
                st.session_state['show_analytics'] = False
                st.rerun()
    else:
        st.info("💡 **Tip:** Ensure your CSV contains columns like 'Churn', 'Tenure_Months', and 'Monthly_Charges' for the best experience.")
        st.image("https://img.freepik.com/free-vector/data-extraction-concept-illustration_114360-4766.jpg", width=600)

st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit & Plotly</p>
    </div>
    """, unsafe_allow_html=True)
