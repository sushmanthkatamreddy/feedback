# Updated app.py content including the admin feedback view under View/Edit Employees tab
# NOTE: Only the affected section is shown here for brevity. You should replace the entire
# "elif tab == '👥 View/Edit Employees':" section in your existing app.py with the block below.

elif tab == "👥 View/Edit Employees":
    st.title("All Employees")
    feedback_df = load_feedback()

    for _, row in employees.iterrows():
        with st.expander(f"{row['Name']} ({row['Email']})"):
            # Editable Info
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

            # Feedback Section
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