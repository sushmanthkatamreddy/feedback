import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

EMPLOYEE_FILE = "employees.csv"
ADMIN_FILE = "admins.csv"
FEEDBACK_FILE = "feedback.csv"

st.set_page_config(page_title="Employee Feedback System", layout="wide")

DEPARTMENTS = ["Accounts", "Human Resources", "Operations", "Marketing", "Management", "Sales"]
SUB_DEPARTMENTS = ["Design & Engineering", "PPC", "Production", "Project Management", "Quality Assurance", "Quality Control", "SCM", "NA"]
LOCATIONS = ["HO - Hyderabad", "Riyadh KSA", "Unit 1 & 2 Hyderabad"]

def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        try:
            df = pd.read_csv(EMPLOYEE_FILE)
            if "UID" not in df.columns:
                df["UID"] = [str(uuid.uuid4()) for _ in range(len(df))]
                df.to_csv(EMPLOYEE_FILE, index=False)
            return df
        except:
            return pd.DataFrame(columns=["UID", "Name", "Email", "Password", "Department", "SubDepartment", "Location"])
    return pd.DataFrame(columns=["UID", "Name", "Email", "Password", "Department", "SubDepartment", "Location"])

def save_employees(df):
    df.to_csv(EMPLOYEE_FILE, index=False)

def load_admins():
    if os.path.exists(ADMIN_FILE):
        try:
            return pd.read_csv(ADMIN_FILE)
        except:
            return pd.DataFrame(columns=["Name", "Email", "Password"])
    return pd.DataFrame(columns=["Name", "Email", "Password"])

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except:
            return pd.DataFrame(columns=["From", "To", "Good", "Bad", "Improve", "Timestamp"])
    return pd.DataFrame(columns=["From", "To", "Good", "Bad", "Improve", "Timestamp"])

def save_admins(df):
    df.to_csv(ADMIN_FILE, index=False)

def save_feedback(sender, receiver, good, bad, improve):
    df = load_feedback()
    df.loc[len(df.index)] = [sender, receiver, good, bad, improve, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    df.to_csv(FEEDBACK_FILE, index=False)

def update_password(email, new_pwd):
    employees = load_employees()
    admins = load_admins()
    if email in employees.Email.values:
        employees.loc[employees.Email == email, "Password"] = new_pwd
        save_employees(employees)
    elif email in admins.Email.values:
        admins.loc[admins.Email == email, "Password"] = new_pwd
        save_admins(admins)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_type = ""

# ---------------------- LOGIN -----------------------
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

elif st.session_state.authenticated:
    employees = load_employees()
    feedback = load_feedback()

    st.sidebar.title("📂 Navigation")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

    if st.session_state.user_type == "Admin":
        tab = st.sidebar.radio("Admin Panel", ["➕ Add Employee", "👥 View/Edit Employees", "🔐 Profile"])

        if tab == "➕ Add Employee":
            st.title("Add New Employee")
            with st.form("add_employee_form", clear_on_submit=True):
                name = st.text_input("Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Add Employee")
                if submitted:
                    if email in employees.Email.values:
                        st.warning("Employee with this email already exists.")
                    else:
                        new_row = {
                            "UID": str(uuid.uuid4()),
                            "Name": name,
                            "Email": email,
                            "Password": password,
                            "Department": "",
                            "SubDepartment": "",
                            "Location": ""
                        }
                        employees = pd.concat([employees, pd.DataFrame([new_row])], ignore_index=True)
                        save_employees(employees)
                        st.success("Employee added successfully.")

        elif tab == "👥 View/Edit Employees":
            st.title("Edit Employees")
            employee_uids = load_employees()["UID"].tolist()

            for uid in employee_uids:
                emp_data = load_employees()
                emp = emp_data[emp_data.UID == uid].iloc[0]

                with st.expander(f"{emp['Name']} ({emp['Email']})"):
                    with st.form(f"form_{uid}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            name_input = st.text_input("Name", value=emp["Name"])
                            dept = st.selectbox("Department", DEPARTMENTS,
                                                index=DEPARTMENTS.index(emp["Department"]) if emp["Department"] in DEPARTMENTS else 0)
                        with col2:
                            if dept == "Operations":
                                sub = st.selectbox("Sub-department", SUB_DEPARTMENTS,
                                                   index=SUB_DEPARTMENTS.index(emp["SubDepartment"]) if emp["SubDepartment"] in SUB_DEPARTMENTS else 0)
                            else:
                                sub = ""
                            loc = st.selectbox("Location", LOCATIONS,
                                               index=LOCATIONS.index(emp["Location"]) if emp["Location"] in LOCATIONS else 0)

                        update_btn, delete_btn = st.columns(2)
                        if update_btn.form_submit_button("Update"):
                            emp_data.loc[emp_data.UID == uid, ["Name", "Department", "SubDepartment", "Location"]] = [name_input, dept, sub, loc]
                            save_employees(emp_data)
                            st.success("Updated successfully.")
                            st.rerun()

                        if delete_btn.form_submit_button("Delete"):
                            emp_data = emp_data[emp_data.UID != uid]
                            save_employees(emp_data)
                            st.success("Deleted successfully.")
                            st.rerun()

                    fb = load_feedback()
                    emp_feedback = fb[fb["To"] == emp["Name"]]
                    if not emp_feedback.empty:
                        st.subheader("Feedback Received")
                        for _, row in emp_feedback.iterrows():
                            st.markdown(f"**From:** {row['From']} ({row['Timestamp']})")
                            st.markdown(f"✅ {row['Good']}")
                            st.markdown(f"❌ {row['Bad']}")
                            st.markdown(f"💡 {row['Improve']}")
                            st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("Admin Profile")
            admin = load_admins()
            user = admin[admin.Email == st.session_state.user_email].iloc[0]
            st.markdown(f"**Name:** {user['Name']}")
            st.markdown(f"**Email:** {user['Email']}")
            new_pwd = st.text_input("New Password", type="password")
            if st.button("Change Password"):
                update_password(user.Email, new_pwd)
                st.success("Password updated.")
    elif st.session_state.user_type == "Employee":
        employees = load_employees()
        user = employees[employees.Email == st.session_state.user_email].iloc[0]
        others = employees[employees.Email != user.Email]

        tab = st.sidebar.radio("Menu", ["📝 Submit Feedback", "📊 Feedback History", "🔐 Profile"])

        if tab == "📝 Submit Feedback":
            st.title("Submit Feedback")
            feedback_inputs = []

            for _, peer in others.iterrows():
                st.subheader(f"Feedback for {peer['Name']}")
                good = st.text_area(f"What did {peer['Name']} do well?", key=f"g_{peer.UID}")
                bad = st.text_area(f"What didn’t {peer['Name']} do well?", key=f"b_{peer.UID}")
                improve = st.text_area(f"What could {peer['Name']} do better?", key=f"i_{peer.UID}")
                feedback_inputs.append((peer["Name"], good, bad, improve))

            if st.button("Submit All Feedback"):
                for to_name, good, bad, improve in feedback_inputs:
                    save_feedback(user["Name"], to_name, good, bad, improve)
                st.success("All feedback submitted!")
                st.rerun()

        elif tab == "📊 Feedback History":
            st.title("Your Feedback History")
            feedback = load_feedback()
            my_fb = feedback[feedback["To"] == user["Name"]]

            if my_fb.empty:
                st.info("No feedback received yet.")
            else:
                for _, row in my_fb.iterrows():
                    st.markdown(f"**From:** {row['From']} ({row['Timestamp']})")
                    st.markdown(f"✅ {row['Good']}")
                    st.markdown(f"❌ {row['Bad']}")
                    st.markdown(f"💡 {row['Improve']}")
                    st.markdown("---")

        elif tab == "🔐 Profile":
            st.title("My Profile")
            with st.expander("Personal Info", expanded=True):
                st.markdown(f"**Name:** {user['Name']}")
                st.markdown(f"**Email:** {user['Email']}")

                dept_index = DEPARTMENTS.index(user["Department"]) if user["Department"] in DEPARTMENTS else 0
                sub_index = SUB_DEPARTMENTS.index(user["SubDepartment"]) if user["SubDepartment"] in SUB_DEPARTMENTS else 0
                loc_index = LOCATIONS.index(user["Location"]) if user["Location"] in LOCATIONS else 0

                dept = st.selectbox("Department", DEPARTMENTS, index=dept_index)
                if dept == "Operations":
                    sub = st.selectbox("Sub-department", SUB_DEPARTMENTS, index=sub_index)
                else:
                    sub = ""
                loc = st.selectbox("Location", LOCATIONS, index=loc_index)

                if st.button("Update Info"):
                    employees.loc[employees.UID == user["UID"], ["Department", "SubDepartment", "Location"]] = [dept, sub, loc]
                    save_employees(employees)
                    st.success("Profile updated.")
                    st.rerun()

            with st.expander("Change Password"):
                new_pwd = st.text_input("New Password", type="password")
                if st.button("Change Password"):
                    update_password(user.Email, new_pwd)
                    st.success("Password updated.")
