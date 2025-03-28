import streamlit as st
import pandas as pd
import os
from datetime import datetime

EMPLOYEE_FILE = "employees.csv"
FEEDBACK_FILE = "feedback.csv"
ADMIN_FILE = "admins.csv"

st.set_page_config(page_title="Employee Feedback System", layout="wide")

# Loaders
def load_admins():
    if os.path.exists(ADMIN_FILE):
        try:
            return pd.read_csv(ADMIN_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["Name", "Email", "Password"])
    return pd.DataFrame(columns=["Name", "Email", "Password"])

def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        try:
            return pd.read_csv(EMPLOYEE_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["Name", "Email", "Password", "Department", "SubDepartment"])
    return pd.DataFrame(columns=["Name", "Email", "Password", "Department", "SubDepartment"])

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["From", "To", "Good", "Bad", "Improve", "Timestamp"])
    return pd.DataFrame(columns=["From", "To", "Good", "Bad", "Improve", "Timestamp"])

# Savers
def save_employee(name, email, password, dept, sub_dept):
    df = load_employees()
    df = df[df.Email != email]
    new_row = pd.DataFrame([[name, email, password, dept, sub_dept]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(EMPLOYEE_FILE, index=False)

def update_password(email, new_password):
    emp_df = load_employees()
    if email in emp_df.Email.values:
        emp_df.loc[emp_df.Email == email, 'Password'] = new_password
        emp_df.to_csv(EMPLOYEE_FILE, index=False)
    else:
        admin_df = load_admins()
        admin_df.loc[admin_df.Email == email, 'Password'] = new_password
        admin_df.to_csv(ADMIN_FILE, index=False)

def save_feedback(sender, receiver, good, bad, improve):
    df = load_feedback()
    new_row = pd.DataFrame([[sender, receiver, good, bad, improve, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)

# Session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_type" not in st.session_state:
    st.session_state.user_type = None

# ---------------------- LOGIN SCREEN ---------------------- #
if not st.session_state.authenticated:
    st.markdown("""
        <style>
            .login-container {
                display: flex;
                justify-content: center;
                align-items: center;
                padding-top: 10vh;
                min-height: 100vh;
            }
            .login-box {
                width: 100%;
                max-width: 400px;
                margin: auto;
            }
        </style>
        <div class='login-container'>
            <div class='login-box'>
    """, unsafe_allow_html=True)

    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        admins = load_admins()
        employees = load_employees()
        if not admins[admins.Email == email].empty and (admins[admins.Email == email].Password.values[0] == password):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_type = "Admin"
        elif not employees[employees.Email == email].empty and (employees[employees.Email == email].Password.values[0] == password):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_type = "Employee"
        else:
            st.error("Invalid credentials")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------------- AUTHENTICATED ---------------------- #
if st.session_state.authenticated:
    employees = load_employees()

    if st.session_state.user_type == "Employee":
        user_match = employees[employees.Email == st.session_state.user_email]
        if not user_match.empty:
            user_info = user_match.iloc[0]
        else:
            st.error("User data not found. Please contact admin.")
            st.stop()

    st.sidebar.title("📂 Navigation")

    # ---------------------- ADMIN VIEW ---------------------- #
    if st.session_state.user_type == "Admin":
        tab = st.sidebar.radio("Admin Panel", ["➕ Add Employee", "👥 View/Edit Employees", "🔐 Profile"])

        if tab == "➕ Add Employee":
            st.title("Add New Employee")
            with st.form("add_emp_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
                dept = st.text_input("Department")
                sub = st.text_input("Sub-department")
                submit = st.form_submit_button("Add")
                if submit:
                    save_employee(name, email, pwd, dept, sub)
                    st.success(f"{name} added.")

        elif tab == "👥 View/Edit Employees":
            st.title("All Employees")
            feedback_df = load_feedback()

            for _, row in employees.iterrows():
                with st.expander(f"{row['Name']} ({row['Email']})"):
                    st.subheader("✏️ Update Info")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Name", row['Name'], key=f"name_{row.Email}")
                        new_dept = st.text_input("Department", row['Department'], key=f"dept_{row.Email}")
                    with col2:
                        new_subdept = st.text_input("Sub-department", row['SubDepartment'], key=f"sub_{row.Email}")

                    if st.button(f"Update {row.Email}", key=f"update_{row.Email}"):
                        employees.loc[employees.Email == row['Email'], ['Name', 'Department', 'SubDepartment']] = [new_name, new_dept, new_subdept]
                        employees.to_csv(EMPLOYEE_FILE, index=False)
                        st.success("Employee info updated!")

                    st.divider()
                    st.subheader("📥 Feedback Received")
                    emp_feedback = feedback_df[feedback_df['To'] == row['Name']]
                    if emp_feedback.empty:
                        st.info("No feedback received.")
                    else:
                        dates = emp_feedback['Timestamp'].str[:10].unique()
                        selected_date = st.selectbox(f"Select date for {row['Name']}", dates, key=f"date_{row.Email}")
                        for _, f in emp_feedback[emp_feedback['Timestamp'].str.startswith(selected_date)].iterrows():
                            st.markdown(f"### From: {f['From']} ({f['Timestamp']})")
                            st.markdown(f"✅ **Good**: {f['Good']}")
                            st.markdown(f"❌ **Bad**: {f['Bad']}")
                            st.markdown(f"💡 **Improve**: {f['Improve']}")
                            st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("Admin Profile")
            new_pwd = st.text_input("New Password", type="password")
            if st.button("Change Password"):
                update_password(st.session_state.user_email, new_pwd)
                st.success("Password updated.")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()

    # ---------------------- EMPLOYEE VIEW ---------------------- #
    elif st.session_state.user_type == "Employee":
        tab = st.sidebar.radio("Menu", ["📝 Submit Feedback", "📊 Feedback History", "🔐 Profile"])

        if tab == "📝 Submit Feedback":
            st.title("Submit Feedback")
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Name", user_info['Name'], disabled=True)
                    st.text_input("Department", user_info['Department'], disabled=True)
                with col2:
                    st.text_input("Sub-department", user_info['SubDepartment'], disabled=True)

            others = employees[employees.Email != user_info.Email]
            feedback_inputs = []

            for _, row in others.iterrows():
                st.subheader(f"Feedback for {row['Name']}")
                good = st.text_area(f"✅ What did {row['Name']} do well?", key=f"g{row.Email}")
                bad = st.text_area(f"❌ What did {row['Name']} not do well?", key=f"b{row.Email}")
                improve = st.text_area(f"💡 What can {row['Name']} do better?", key=f"i{row.Email}")
                feedback_inputs.append((row['Name'], good, bad, improve))

            if st.button("Submit All Feedback"):
                for to_name, good, bad, improve in feedback_inputs:
                    save_feedback(user_info['Name'], to_name, good, bad, improve)
                st.success("All feedback submitted!")

        elif tab == "📊 Feedback History":
            st.title("Your Feedback History")
            fb = load_feedback()
            received = fb[fb['To'] == user_info['Name']]
            if received.empty:
                st.info("No feedback received.")
            else:
                dates = received['Timestamp'].str[:10].unique()
                sel_date = st.selectbox("Select Date", dates)
                for _, row in received[received['Timestamp'].str.startswith(sel_date)].iterrows():
                    st.markdown(f"**From:** {row['From']} ({row['Timestamp']})")
                    st.markdown(f"✅ {row['Good']}")
                    st.markdown(f"❌ {row['Bad']}")
                    st.markdown(f"💡 {row['Improve']}")
                    st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("My Profile")
            new_pwd = st.text_input("New Password", type="password")
            if st.button("Change Password"):
                update_password(st.session_state.user_email, new_pwd)
                st.success("Password updated.")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
