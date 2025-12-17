import streamlit as st
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Employee Attrition Lite", page_icon="📉", layout="centered")

# --- Load Model ---
@st.cache_resource
def load_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "employees_attrition_model.pkl")
    
    if not os.path.exists(model_path):
        st.error(f"Model not found at {model_path}")
        return None

    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()

# --- Main Interface ---
st.title("📉 Attrition Predictor (Simplified)")
st.write("Enter the key details below to get a quick attrition risk assessment.")

if model:
    with st.form("simplified_form"):
        col1, col2 = st.columns(2)
        
        # TOP 8 FEATURES ONLY (Based on Model Importance)
        with col1:
            total_working_years = st.number_input("Total Working Years", 0, 40, 10)
            monthly_income = st.number_input("Monthly Income", 1000, 20000, 5000)
            age = st.number_input("Age", 18, 65, 30)
            distance_home = st.number_input("Distance From Home (km)", 1, 30, 5)

        with col2:
            over_time = st.selectbox("OverTime?", ["No", "Yes"])
            stock_option_level = st.selectbox("Stock Option Level (0-3)", [0, 1, 2, 3], index=1)
            env_satisfaction = st.slider("Environment Satisfaction (1-Low, 4-High)", 1, 4, 3)
            num_companies = st.number_input("Num Companies Worked", 0, 10, 1)

        submit = st.form_submit_button("Analyze Risk")

    if submit:
        # --- 1. Prepare Full Input Vector with Defaults ---
        # The model expects ALL columns, so we fill missing ones with average/mode values
        # derived from typical dataset averages.
        
        # List of all 44 columns expected by the model
        all_columns = [
            'Age', 'DailyRate', 'DistanceFromHome', 'Education', 'EnvironmentSatisfaction',
            'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobSatisfaction', 'MonthlyIncome',
            'MonthlyRate', 'NumCompaniesWorked', 'PercentSalaryHike', 'PerformanceRating',
            'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
            'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
            'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager',
            'BusinessTravel_Travel_Frequently', 'BusinessTravel_Travel_Rarely',
            'Department_Research & Development', 'Department_Sales',
            'EducationField_Life Sciences', 'EducationField_Marketing',
            'EducationField_Medical', 'EducationField_Other',
            'EducationField_Technical Degree', 'Gender_Male',
            'JobRole_Human Resources', 'JobRole_Laboratory Technician', 'JobRole_Manager',
            'JobRole_Manufacturing Director', 'JobRole_Research Director',
            'JobRole_Research Scientist', 'JobRole_Sales Executive',
            'JobRole_Sales Representative', 'MaritalStatus_Married',
            'MaritalStatus_Single', 'OverTime_Yes'
        ]

        # Initialize with zeros
        input_df = pd.DataFrame(0, index=[0], columns=all_columns)

        # --- 2. Fill User Inputs ---
        input_df['TotalWorkingYears'] = total_working_years
        input_df['MonthlyIncome'] = monthly_income
        input_df['Age'] = age
        input_df['DistanceFromHome'] = distance_home
        input_df['StockOptionLevel'] = stock_option_level
        input_df['EnvironmentSatisfaction'] = env_satisfaction
        input_df['NumCompaniesWorked'] = num_companies
        if over_time == "Yes":
            input_df['OverTime_Yes'] = 1

        # --- 3. Fill Defaults for Missing Inputs (Mode/Mean) ---
        # These values are harmless averages to satisfy the model structure
        defaults = {
            'DailyRate': 800, 'Education': 3, 'HourlyRate': 65, 'JobInvolvement': 3,
            'JobLevel': 2, 'JobSatisfaction': 3, 'MonthlyRate': 14000, 
            'PercentSalaryHike': 15, 'PerformanceRating': 3, 'RelationshipSatisfaction': 3,
            'TrainingTimesLastYear': 2, 'WorkLifeBalance': 3, 'YearsAtCompany': 5,
            'YearsInCurrentRole': 2, 'YearsSinceLastPromotion': 1, 'YearsWithCurrManager': 2,
            'BusinessTravel_Travel_Rarely': 1, 'Department_Research & Development': 1,
            'EducationField_Life Sciences': 1, 'Gender_Male': 1, 'JobRole_Research Scientist': 1,
            'MaritalStatus_Married': 1
        }
        for col, val in defaults.items():
            input_df[col] = val

        # --- 4. Prediction & Plotting ---
        prediction_prob = model.predict_proba(input_df)[0] # [prob_stay, prob_leave]
        attrition_risk = prediction_prob[1]
        
        st.divider()
        st.subheader("Analysis Results")
        
        # Columns for result text and chart
        r_col1, r_col2 = st.columns([1, 2])
        
        with r_col1:
            st.markdown(f"**Attrition Probability:**")
            if attrition_risk > 0.5:
                st.error(f"{attrition_risk:.1%} (High Risk)")
            else:
                st.success(f"{attrition_risk:.1%} (Safe)")
            
            st.caption("Based on the top factors, this employee shows these characteristics.")

        with r_col2:
            # --- PLOT 1: Donut Chart for Probability ---
            fig1, ax1 = plt.subplots(figsize=(3, 3))
            colors = ['#ff9999', '#66b3ff']
            labels = ['Attrition', 'Retention']
            sizes = [attrition_risk, 1 - attrition_risk]
            
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            # Draw circle for donut chart
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig1.gca().add_artist(centre_circle)
            ax1.axis('equal')  
            st.pyplot(fig1, use_container_width=False)

        # --- PLOT 2: Feature Importance Context ---
        st.subheader("What drives this model?")
        st.write("The chart below shows the most important factors the model considers.")
        
        # Hardcoded top feature importances from model analysis
        features = ['Total Working Years', 'Monthly Income', 'Age', 'OverTime', 'Daily Rate', 'Stock Level']
        importance = [0.20, 0.13, 0.11, 0.08, 0.07, 0.07]
        
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        y_pos = np.arange(len(features))
        ax2.barh(y_pos, importance, align='center', color='#4CAF50')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(features)
        ax2.invert_yaxis()  # Labels read top-to-bottom
        ax2.set_xlabel('Relative Importance')
        ax2.set_title('Top Influencing Factors for Attrition')
        st.pyplot(fig2)
