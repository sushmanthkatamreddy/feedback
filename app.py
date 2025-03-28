import streamlit as st
import pandas as pd
import os
from datetime import datetime

EMPLOYEE_FILE = "employees.csv"
FEEDBACK_FILE = "feedback.csv"
ADMIN_FILE = "admins.csv"

st.set_page_config(page_title="Employee Feedback System", layout="wide")

# Dropdown options
department_options = ["Accounts", "Human Resources", "Operations", "Marketing", "Management", "Sales"]
sub_dept_options = ["Design & Engineering", "PPC", "Production", "Project Management", "Quality Assurance", "Quality Control", "SCM", "NA"]
location_options = ["HO - Hyderabad", "Riyadh KSA", "Unit 1 & 2 Hyderabad"]

# Session init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_type = ""

# Loaders
def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        return pd.read_csv(EMPLOYEE_FILE)
    return pd.DataFrame(columns=["Name", "Email", "Password", "Department", "SubDepartment", "Location"])

def load_admins():
    if os.path.exists(ADMIN_FILE):
        return pd.read_csv(ADMIN_FILE)
    return pd.DataFrame(columns=["Name", "Email", "Password"])

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        return pd.read_csv(FEEDBACK_FILE)
    return pd.DataFrame(columns=["From", "To", "Good", "Bad", "Improve", "Timestamp"])

# Savers
def save_employee(name, email, pwd):
    df = load_employees()
    new_row = pd.DataFrame([[name, email, pwd, "", "", ""]], columns=df.columns)
    df = pd.concat([df[df.Email != email], new_row], ignore_index=True)
    df.to_csv(EMPLOYEE_FILE, index=False)

def save_feedback(sender, receiver, good, bad, improve):
    df = load_feedback()
    df.loc[len(df.index)] = [sender, receiver, good, bad, improve, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    df.to_csv(FEEDBACK_FILE, index=False)

def update_password(email, new_pwd):
    employees = load_employees()
    admins = load_admins()
    if email in employees.Email.values:
        employees.loc[employees.Email == email, "Password"] = new_pwd
        employees.to_csv(EMPLOYEE_FILE, index=False)
    elif email in admins.Email.values:
        admins.loc[admins.Email == email, "Password"] = new_pwd
        admins.to_csv(ADMIN_FILE, index=False)

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.authenticated:
    st.markdown("###\n###\n###")
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.markdown("<div style='max-width: 400px; width: 100%;'>", unsafe_allow_html=True)

    st.title("🔐 Login")
    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        admins = load_admins()
        employees = load_employees()
        if email in admins.Email.values and pwd == admins[admins.Email == email].Password.values[0]:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_type = "Admin"
            st.rerun()
        elif email in employees.Email.values and pwd == employees[employees.Email == email].Password.values[0]:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_type = "Employee"
            st.rerun()
        else:
            st.error("Invalid credentials.")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------- ADMIN PANEL ----------------
else:
    employees = load_employees()
    admins = load_admins()

    st.sidebar.title("📂 Navigation")

    if st.session_state.user_type == "Admin":
        tab = st.sidebar.radio("Admin Panel", ["➕ Add Employee", "👥 View/Edit Employees", "🔐 Profile"])
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

        if tab == "➕ Add Employee":
            st.title("Add Employee")
            with st.form("add_emp"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Add")
                if submitted:
                    save_employee(name, email, pwd)
                    st.success("Employee added.")
                    st.rerun()

        elif tab == "👥 View/Edit Employees":
            st.title("Edit Employees")
            feedback_df = load_feedback()

            for _, emp in employees.iterrows():
                with st.expander(f"{emp['Name']} ({emp['Email']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Name", emp['Name'], key=f"n{emp.Email}")
                        dept = st.selectbox("Department", department_options, index=department_options.index(emp["Department"]) if emp["Department"] in department_options else 0, key=f"d{emp.Email}")
                    with col2:
                        sub = st.selectbox("Sub-department", sub_dept_options, index=sub_dept_options.index(emp["SubDepartment"]) if emp["SubDepartment"] in sub_dept_options else 0, key=f"s{emp.Email}")
                        loc = st.selectbox("Location", location_options, index=location_options.index(emp["Location"]) if emp["Location"] in location_options else 0, key=f"l{emp.Email}")

                    if st.button("Update", key=f"u{emp.Email}"):
                        employees.loc[employees.Email == emp["Email"], ["Name", "Department", "SubDepartment", "Location"]] = [name, dept, sub, loc]
                        employees.to_csv(EMPLOYEE_FILE, index=False)
                        st.success("Employee updated.")
                        st.rerun()

                    if st.button("Delete", key=f"x{emp.Email}"):
                        employees = employees[employees.Email != emp.Email]
                        employees.to_csv(EMPLOYEE_FILE, index=False)
                        st.success("Deleted.")
                        st.rerun()

                    emp_fb = feedback_df[feedback_df["To"] == emp["Name"]]
                    if not emp_fb.empty:
                        st.subheader("Feedback Received")
                        for _, fb in emp_fb.iterrows():
                            st.markdown(f"**From:** {fb['From']} ({fb['Timestamp']})")
                            st.markdown(f"✅ {fb['Good']}")
                            st.markdown(f"❌ {fb['Bad']}")
                            st.markdown(f"💡 {fb['Improve']}")
                            st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("Admin Profile")
            admin_info = admins[admins.Email == st.session_state.user_email].iloc[0]
            st.markdown(f"**Name**: {admin_info['Name']}  \n**Email**: {admin_info['Email']}")
            new_pwd = st.text_input("New Password", type="password")
            if st.button("Change Password"):
                update_password(st.session_state.user_email, new_pwd)
                st.success("Password updated.")
    elif st.session_state.user_type == "Employee":
        user = employees[employees.Email == st.session_state.user_email].iloc[0]
        tab = st.sidebar.radio("Menu", ["📝 Submit Feedback", "📊 Feedback History", "🔐 Profile"])
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

        if tab == "📝 Submit Feedback":
            st.title("Submit Feedback")

            st.markdown("### Give Feedback to Your Colleagues")
            feedback_inputs = []
            others = employees[employees.Email != user.Email]

            for _, peer in others.iterrows():
                st.subheader(f"Feedback for {peer['Name']}")
                good = st.text_area(f"What did {peer['Name']} do well?", key=f"g_{peer.Email}")
                bad = st.text_area(f"What didn’t {peer['Name']} do well?", key=f"b_{peer.Email}")
                improve = st.text_area(f"What could {peer['Name']} do better?", key=f"i_{peer.Email}")
                feedback_inputs.append((peer["Name"], good, bad, improve))

            if st.button("Submit All Feedback"):
                for to_name, good, bad, improve in feedback_inputs:
                    save_feedback(user["Name"], to_name, good, bad, improve)
                st.success("Feedback submitted successfully!")
                st.rerun()

        elif tab == "📊 Feedback History":
            st.title("Feedback You Received")
            fb = load_feedback()
            my_fb = fb[fb["To"] == user["Name"]]

            if my_fb.empty:
                st.info("No feedback received yet.")
            else:
                dates = my_fb["Timestamp"].str[:10].unique()
                selected_date = st.selectbox("Select Date", dates)
                for _, row in my_fb[my_fb["Timestamp"].str.startswith(selected_date)].iterrows():
                    st.markdown(f"**From:** {row['From']} ({row['Timestamp']})")
                    st.markdown(f"✅ {row['Good']}")
                    st.markdown(f"❌ {row['Bad']}")
                    st.markdown(f"💡 {row['Improve']}")
                    st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("My Profile")

            with st.expander("👤 Personal Info", expanded=True):
                st.markdown(f"**Name:** {user['Name']}")
                st.markdown(f"**Email:** {user['Email']}")

                dept = st.selectbox("Department", department_options,
                    index=department_options.index(user["Department"]) if user["Department"] in department_options else 0,
                    key="prof_dept")

                subdept = st.selectbox("Sub-department", sub_dept_options,
                    index=sub_dept_options.index(user["SubDepartment"]) if user["SubDepartment"] in sub_dept_options else 0,
                    key="prof_sub")

                location = st.selectbox("Location", location_options,
                    index=location_options.index(user["Location"]) if user["Location"] in location_options else 0,
                    key="prof_loc")

                if st.button("Update Info"):
                    employees.loc[employees.Email == user.Email, ["Department", "SubDepartment", "Location"]] = [dept, subdept, location]
                    employees.to_csv(EMPLOYEE_FILE, index=False)
                    st.success("Profile info updated.")
                    st.rerun()

            with st.expander("🔒 Change Password"):
                new_pwd = st.text_input("New Password", type="password")
                if st.button("Change Password"):
                    update_password(st.session_state.user_email, new_pwd)
                    st.success("Password updated.")
