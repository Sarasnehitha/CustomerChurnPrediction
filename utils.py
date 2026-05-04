import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(df):
    """
    Cleans and preprocesses the churn data for analytics and prediction.
    """
    df_clean = df.copy()
    
    # Handle missing values in Total_Charges
    if 'Total_Charges' in df_clean.columns:
        df_clean['Total_Charges'] = pd.to_numeric(df_clean['Total_Charges'], errors='coerce')
        df_clean['Total_Charges'] = df_clean['Total_Charges'].fillna(df_clean['Total_Charges'].median())
    
    # Drop CustomerID if present
    if 'CustomerID' in df_clean.columns:
        df_clean = df_clean.drop('CustomerID', axis=1)
        
    return df_clean

def encode_data(df):
    """
    Encodes categorical variables for correlation analysis or modeling.
    """
    df_encoded = df.copy()
    categorical_cols = ['Gender', 'Contract_Type', 'Internet_Service', 'Payment_Method']
    
    le = LabelEncoder()
    for col in categorical_cols:
        if col in df_encoded.columns:
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            
    return df_encoded

def get_kpis(df):
    """
    Calculates key performance indicators.
    """
    total_customers = len(df)
    churn_rate = (df['Churn'].sum() / total_customers) * 100 if 'Churn' in df.columns else 0
    avg_charges = df['Monthly_Charges'].mean() if 'Monthly_Charges' in df.columns else 0
    
    return total_customers, churn_rate, avg_charges
