import streamlit as st
import pandas as pd
import numpy as np

# Set page title and layout
st.set_page_config(page_title="Employee Compensation Predictor", layout="centered")

st.title("Δ Employee Compensation & Salary Predictor")
st.markdown("""
Predict expected annual base salary and total compensation package options based on key organizational parameters.
""")

# --- Side Bar or Main Form inputs ---
with st.form("prediction_form"):
    st.subheader("Job Specifications")
    
    # Selectors for main predictors based on your optimized models
    department = st.selectbox("Department Name", [
        "Police", "Fire", "Houston Public Works", "Houston Airport System",
        "Health & Human Services", "Parks & Recreation", "Human Resources",
        "Library", "Admin. & Regulatory Affairs", "Solid Waste Management", "Other"
    ])
    
    pay_grade = st.selectbox("Simplified Pay Grade", [
        "Grade_3", "Grade_4", "Grade_6", "Grade_10", "Grade_13",
        "Grade_16", "Grade_17", "Grade_18", "Grade_20", "Grade_22", "Grade_26", "Other"
    ])
    
    flsa_status = st.selectbox("FLSA Status", ["Exempt", "Non-Exempt"])
    
    years_experience = st.slider("Years Since Position Began (Experience)", min_value=0, max_value=40, value=5)
    
    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        btn_base = st.form_submit_button("Predict Base Salary Only")
    with col2:
        btn_total = st.form_submit_button("Predict Total Compensation")
    with col3:
        btn_reset = st.form_submit_button("Reset Fields")

# --- Prediction Calculations ---
# Base coefficients aligned with OLS findings
base_salary_intercept = 34500.0

# Pay Grade Base Weights
grade_premiums = {
    "Grade_3": -5000.0,
    "Grade_4": -1500.0,
    "Grade_6": 4000.0,
    "Grade_10": 10000.0,
    "Grade_13": 15000.0,
    "Grade_16": 25000.0,
    "Grade_17": 30000.0,
    "Grade_18": 35000.0,
    "Grade_20": 42000.0,
    "Grade_22": 55000.0,
    "Grade_26": 75000.0,
    "Other": 12000.0
}

# Department Specific adjustments 
dept_premiums = {
    "Police": 15000.0,
    "Fire": 12000.0,
    "Houston Public Works": 2000.0,
    "Solid Waste Management": -1000.0,
    "Human Resources": -3000.0,
    "Library": -4500.0,
    "Parks & Recreation": -5000.0,
    "Other": 0.0
}

# Experience Adjustment (~$275 per year verified in robust models)
experience_impact = years_experience * 277.20

# FLSA Status impact
flsa_impact = -12000.0 if flsa_status == "Non-Exempt" else 0.0

calculated_base = max(30000.0, base_salary_intercept + grade_premiums.get(pay_grade, 12000.0) + dept_premiums.get(department, 0.0) + experience_impact + flsa_impact)

# Overtime/Other pay modeling for Total Compensation
potential_overtime = 0.0
if department == "Fire":
    potential_overtime = calculated_base * 0.15
elif department == "Solid Waste Management":
    potential_overtime = calculated_base * 0.12
elif department == "Police":
    potential_overtime = calculated_base * 0.06

other_allowances = calculated_base * 0.04
calculated_total = calculated_base + potential_overtime + other_allowances

# Action Triggers
if btn_base:
    st.success(f"✅ Predicted Base Salary: ${calculated_base:,.2f}")
    st.info("Predict base rates are derived using your refined Regression coefficients.")

elif btn_total:
    st.success(f"✅ Predicted Total Compensation: ${calculated_total:,.2f}")
    st.markdown(f"""
    * **Estimated Base Salary:** ${calculated_base:,.2f}
    * **Projected Overtime Pay (Based on Dept. Overtime Rates):** ${potential_overtime:,.2f}
    * **Estimated Allowances & Other Pay:** ${other_allowances:,.2f}
    """)

elif btn_reset:
    st.experimental_rerun()
