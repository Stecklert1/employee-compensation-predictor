import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

# Set page title and layout
st.set_page_config(page_title="Employee Compensation & Role Predictor", layout="centered")

st.title("Δ Employee Compensation & Job Role Predictor")
st.markdown("""
Predict expected annual base salary, total compensation options, and most likely Job Role (Pay Grade) based on organizational and demographic parameters.
""")

# Load classification model if it exists
model_path = "job_predictor_model.pkl"
class_model = None
if os.path.exists(model_path):
    try:
        with open(model_path, "rb") as f:
            class_model = pickle.load(f)
    except Exception as e:
        st.warning(f"Could not load job predictor model: {e}")

# --- Form inputs ---
with st.form("prediction_form"):
    st.subheader("Employee Demographics & Job Specifications")

    col_left, col_right = st.columns(2)
    
    with col_left:
        department = st.selectbox("Department Name", [
            "Police", "Fire", "Houston Public Works", "Houston Airport System",
            "Health & Human Services", "Parks & Recreation", "Human Resources",
            "Library", "Admin. & Regulatory Affairs", "Solid Waste Management", "Other"
        ])
        flsa_status = st.selectbox("FLSA Status", ["Exempt", "Non-Exempt"])
        gender = st.selectbox("Gender", ["Male", "Female"])
        race = st.selectbox("Race", [
            "Black or African American", "Hispanic/Latino", "White", 
            "Asian", "American Indian or Alaskan Native", "Others"
        ])

    with col_right:
        pay_grade = st.selectbox("Simplified Pay Grade (for Compensation predictions)", [
            "Grade_3", "Grade_4", "Grade_6", "Grade_10", "Grade_13",
            "Grade_16", "Grade_17", "Grade_18", "Grade_20", "Grade_22", "Grade_26", "Other"
        ])
        years_experience = st.slider("Years Since Position Began (Experience)", min_value=0, max_value=40, value=5)
        age = st.slider("Age", min_value=18, max_value=80, value=35)

    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        btn_base = st.form_submit_button("Predict Salary & Comp")
    with col2:
        btn_role = st.form_submit_button("Predict Likely Job Role")
    with col3:
        btn_reset = st.form_submit_button("Reset Fields")

# --- Prediction Calculations (Compensation) ---
base_salary_intercept = 34500.0
grade_premiums = {
    "Grade_3": -5000.0, "Grade_4": -1500.0, "Grade_6": 4000.0, "Grade_10": 10000.0,
    "Grade_13": 15000.0, "Grade_16": 25000.0, "Grade_17": 30000.0, "Grade_18": 35000.0,
    "Grade_20": 42000.0, "Grade_22": 55000.0, "Grade_26": 75000.0, "Other": 12000.0
}
dept_premiums = {
    "Police": 15000.0, "Fire": 12000.0, "Houston Public Works": 2000.0,
    "Solid Waste Management": -1000.0, "Human Resources": -3000.0, "Library": -4500.0,
    "Parks & Recreation": -5000.0, "Other": 0.0
}

experience_impact = years_experience * 277.20
flsa_impact = -12000.0 if flsa_status == "Non-Exempt" else 0.0

calculated_base = max(30000.0, base_salary_intercept + grade_premiums.get(pay_grade, 12000.0) + dept_premiums.get(department, 0.0) + experience_impact + flsa_impact)
potential_overtime = 0.0
if department == "Fire":
    potential_overtime = calculated_base * 0.15
elif department == "Solid Waste Management":
    potential_overtime = calculated_base * 0.12
elif department == "Police":
    potential_overtime = calculated_base * 0.06

other_allowances = calculated_base * 0.04
calculated_total = calculated_base + potential_overtime + other_allowances

# --- Handle Button Outputs ---
if btn_base:
    st.subheader("💰 Compensation Prediction Results")
    st.success(f"✅ Predicted Base Salary: ${calculated_base:,.2f}")
    st.success(f"✅ Predicted Total Compensation: ${calculated_total:,.2f}")
    st.markdown(f"""
    * **Estimated Base Salary:** ${calculated_base:,.2f}
    * **Projected Overtime Pay:** ${potential_overtime:,.2f}
    * **Estimated Allowances & Other Pay:** ${other_allowances:,.2f}
    """)

elif btn_role:
    st.subheader("💼 Job Role / Pay Grade Prediction")
    if class_model is not None:
        # Construct input DataFrame matching original training features exactly
        input_data = pd.DataFrame([{
            'Age': age,
            'Years Since Position Began': years_experience,
            'Gender': gender,
            'Race': race,
            'Department Name': department
        }])
        
        # Features mapping/one-hot encoding wrapper logic to match training columns
        try:
            # Align to the classification model columns
            # Note: Category encoder or get_dummies alignment is required.
            # Let's construct a compatible schema if classification_artifacts exist.
            # Since we have the classification_artifacts in our context, we structure the dummy columns:
            all_features = [
                'Age', 'Years Since Position Began', 'Gender_Male', 'Race_Asian',
                'Race_Asian/Pacific Islander', 'Race_Black or African American',
                'Race_Hispanic/Latino', 'Race_Native Hawaiian or Other Pacific Islander',
                'Race_Others', 'Race_Two or More Races', 'Race_White'
            ] + [f"Department Name_{d}" for d in [
                'Business Opportunity', 'City Council', 'City Secretary', 'Controllers',
                'Department of Neighborhoods', 'Finance', 'Fire', 'Fleet Management',
                'General Services', 'Health & Human Services', 'Housing & Community Devlpmnt.',
                'Houston Airport System', 'Houston Emergency Center', 'Houston Public Works',
                'Human Resources', 'Information Technology', 'Legal', 'Library',
                'Mayor\'s Office', 'Municipal Courts', 'Parks & Recreation', 'Planning & Development',
                'Police', 'Solid Waste Management'
            ]]
            
            model_input = pd.DataFrame(0, index=[0], columns=all_features)
            model_input['Age'] = age
            model_input['Years Since Position Began'] = years_experience
            if gender == "Male":
                model_input['Gender_Male'] = 1
            if f"Race_{race}" in model_input.columns:
                model_input[f"Race_{race}"] = 1
            if f"Department Name_{department}" in model_input.columns:
                model_input[f"Department Name_{department}"] = 1
                
            predicted_grade = class_model.predict(model_input)[0]
            st.success(f"✨ Most Likely Pay Grade Class: **{predicted_grade}**")
            st.markdown("This represents the predicted tier based on your demographic profiles and selected organizational parameters.")
        except Exception as e:
            st.error(f"Error processing inputs for classification: {e}")
    else:
        st.info("No pre-trained model file found. Please save your trained Classifier Model as `job_predictor_model.pkl` in this directory to enable this feature!")

elif btn_reset:
    st.rerun()
