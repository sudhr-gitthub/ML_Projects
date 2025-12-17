import streamlit as st
import pandas as pd
import pickle
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Employee Attrition Predictor",
    page_icon="👔",
    layout="wide"
)

# --- Load Model ---
@st.cache_resource
def load_model():
    # Attempt to load the model locally
    # Ensure 'employees_attrition_model.pkl' is in the same folder as app.py
    model_path = "employees_attrition_model.pkl" 
    
    if not os.path.exists(model_path):
        st.error(f"Model file not found at {model_path}. Please ensure the .pkl file is uploaded to the repository.")
        return None

    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()

# --- Main Interface ---
st.title("👔 Employee Attrition Prediction App")
st.write("Enter the employee details below to predict the likelihood of attrition.")

# Check if model loaded correctly
if model:
    # --- Input Form ---
    with st.form("attrition_form"):
        # Divide inputs into logical columns for a cleaner UI
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Personal Info")
            age = st.number_input("Age", min_value=18, max_value=60, value=30)
            gender = st.selectbox("Gender", ["Male", "Female"])
            marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
            education_field = st.selectbox("Education Field", [
                "Life Sciences", "Medical", "Marketing", "Technical Degree", "Human Resources", "Other"
            ])
            education = st.selectbox("Education Level (1-5)", [1, 2, 3, 4, 5], index=2)
            distance_home = st.number_input("Distance From Home (km)", min_value=1, max_value=30, value=5)

        with col2:
            st.subheader("Job Details")
            department = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])
            job_role = st.selectbox("Job Role", [
                "Sales Executive", "Research Scientist", "Laboratory Technician", 
                "Manufacturing Director", "Healthcare Representative", "Manager", 
                "Sales Representative", "Research Director", "Human Resources"
            ])
            job_level = st.selectbox("Job Level (1-5)", [1, 2, 3, 4, 5], index=1)
            business_travel = st.selectbox("Business Travel", ["Non-Travel", "Travel_Rarely", "Travel_Frequently"])
            over_time = st.selectbox("OverTime", ["No", "Yes"])
            
        with col3:
            st.subheader("Compensation & Satisfaction")
            monthly_income = st.number_input("Monthly Income", min_value=1000, value=5000)
            daily_rate = st.number_input("Daily Rate", min_value=100, value=800)
            hourly_rate = st.number_input("Hourly Rate", min_value=30, value=60)
            monthly_rate = st.number_input("Monthly Rate", min_value=2000, value=15000)
            percent_salary_hike = st.slider("Percent Salary Hike", 10, 25, 12)
            stock_option_level = st.slider("Stock Option Level", 0, 3, 0)
            
        st.markdown("---")
        st.subheader("Work History & Ratings")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            num_companies = st.number_input("Num Companies Worked", 0, 10, 1)
            total_working_years = st.number_input("Total Working Years", 0, 40, 5)
            training_times = st.number_input("Training Times Last Year", 0, 6, 2)
            
        with col5:
            years_at_company = st.number_input("Years At Company", 0, 40, 3)
            years_in_curr_role = st.number_input("Years In Current Role", 0, 20, 2)
            years_since_promotion = st.number_input("Years Since Last Promotion", 0, 20, 1)
            years_curr_manager = st.number_input("Years With Curr Manager", 0, 20, 2)

        with col6:
            env_satisfaction = st.slider("Environment Satisfaction (1-4)", 1, 4, 3)
            job_involvement = st.slider("Job Involvement (1-4)", 1, 4, 3)
            job_satisfaction = st.slider("Job Satisfaction (1-4)", 1, 4, 3)
            relationship_satisfaction = st.slider("Relationship Satisfaction (1-4)", 1, 4, 3)
            work_life_balance = st.slider("Work Life Balance (1-4)", 1, 4, 3)
            performance_rating = st.slider("Performance Rating (3-4)", 3, 4, 3)

        submit_button = st.form_submit_button("Predict Attrition")

    if submit_button:
        # --- Preprocessing ---
        # 1. Define all columns expected by the model (derived from your pkl file structure)
        expected_columns = [
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

        # 2. Initialize input dataframe with 0s
        input_data = pd.DataFrame(0, index=[0], columns=expected_columns)

        # 3. Fill Numerical Data
        input_data['Age'] = age
        input_data['DailyRate'] = daily_rate
        input_data['DistanceFromHome'] = distance_home
        input_data['Education'] = education
        input_data['EnvironmentSatisfaction'] = env_satisfaction
        input_data['HourlyRate'] = hourly_rate
        input_data['JobInvolvement'] = job_involvement
        input_data['JobLevel'] = job_level
        input_data['JobSatisfaction'] = job_satisfaction
        input_data['MonthlyIncome'] = monthly_income
        input_data['MonthlyRate'] = monthly_rate
        input_data['NumCompaniesWorked'] = num_companies
        input_data['PercentSalaryHike'] = percent_salary_hike
        input_data['PerformanceRating'] = performance_rating
        input_data['RelationshipSatisfaction'] = relationship_satisfaction
        input_data['StockOptionLevel'] = stock_option_level
        input_data['TotalWorkingYears'] = total_working_years
        input_data['TrainingTimesLastYear'] = training_times
        input_data['WorkLifeBalance'] = work_life_balance
        input_data['YearsAtCompany'] = years_at_company
        input_data['YearsInCurrentRole'] = years_in_curr_role
        input_data['YearsSinceLastPromotion'] = years_since_promotion
        input_data['YearsWithCurrManager'] = years_curr_manager

        # 4. Fill Categorical Data (One-Hot Encoding Manual Mapping)
        
        # Business Travel
        if business_travel == "Travel_Frequently":
            input_data['BusinessTravel_Travel_Frequently'] = 1
        elif business_travel == "Travel_Rarely":
            input_data['BusinessTravel_Travel_Rarely'] = 1
        
        # Department
        if department == "Research & Development":
            input_data['Department_Research & Development'] = 1
        elif department == "Sales":
            input_data['Department_Sales'] = 1
            
        # Education Field
        if education_field in ['Life Sciences', 'Marketing', 'Medical', 'Other', 'Technical Degree']:
            input_data[f'EducationField_{education_field}'] = 1
            
        # Gender
        if gender == "Male":
            input_data['Gender_Male'] = 1
            
        # Job Role (Map user selection to column name)
        if job_role != "Healthcare Representative": # Healthcare Rep is the reference column (implied 0 for all others)
            role_col = f"JobRole_{job_role}"
            if role_col in input_data.columns:
                input_data[role_col] = 1

        # Marital Status
        if marital_status == "Married":
            input_data['MaritalStatus_Married'] = 1
        elif marital_status == "Single":
            input_data['MaritalStatus_Single'] = 1
            
        # OverTime
        if over_time == "Yes":
            input_data['OverTime_Yes'] = 1

        # --- Prediction ---
        try:
            prediction = model.predict(input_data)
            prediction_prob = model.predict_proba(input_data)
            
            st.markdown("### Prediction Result")
            if prediction[0] == 1:
                st.error(f"⚠️ High Risk of Attrition (Probability: {prediction_prob[0][1]:.2f})")
                st.write("This employee is likely to leave the company.")
            else:
                st.success(f"✅ Low Risk of Attrition (Probability: {prediction_prob[0][1]:.2f})")
                st.write("This employee is likely to stay.")
                
            with st.expander("See Input Data sent to Model"):
                st.dataframe(input_data)
                
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")

else:
    st.warning("Model is not loaded. Please check the file path.")
