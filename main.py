import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

# Load credentials from the JSON file
with open('streamlit.json') as f:
    creds_data = json.load(f)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
client = gspread.authorize(creds)

# Open the Google Sheet by URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1HE-4rLM4eTXs5YDWPF_VqgH7JT6JEGYYXRnP7yd2p_8"
sheet = client.open_by_url(spreadsheet_url).sheet1  # gid=0 usually refers to the first sheet

# Read data from Google Sheet
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Streamlit app
st.subheader("Hanieh Salehi")
st.write("Private shared Google Sheet.")

# Display data
st.dataframe(df)

# Form for adding a new contact
st.write("Add a new contact")
with st.form("add_contact"):
    name = st.text_input("Name")
    family = st.text_input("Family")
    age = st.number_input("Age", min_value=0)
    city = st.text_input("City")
    submitted = st.form_submit_button("Add Contact")
    if submitted:
        new_row = [name, family, age, city]
        sheet.append_row(new_row)
        st.success("Contact added successfully!")

# Form for editing an existing contact
st.write("Edit an existing contact")
contact_options = df.apply(lambda row: f"{row['Name']} {row['Family']}", axis=1).tolist()
selected_contact = st.selectbox("Select contact to edit", options=contact_options)
selected_row = df[df.apply(lambda row: f"{row['Name']} {row['Family']}", axis=1) == selected_contact].iloc[0]

with st.form("edit_contact"):
    new_name = st.text_input("Name", value=selected_row["Name"])
    new_family = st.text_input("Family", value=selected_row["Family"])
    new_age = st.number_input("Age", min_value=0, value=selected_row["Age"])
    new_city = st.text_input("City", value=selected_row["City"])
    submitted = st.form_submit_button("Edit Contact")
    if submitted:
        # Find the row index and update the row
        row_index = df.index[df.apply(lambda row: f"{row['Name']} {row['Family']}", axis=1) == selected_contact].tolist()[0] + 2
        sheet.update_cell(row_index, 1, new_name)
        sheet.update_cell(row_index, 2, new_family)
        sheet.update_cell(row_index, 3, new_age)
        sheet.update_cell(row_index, 4, new_city)
        st.success("Contact updated successfully!")

# Form for deleting a contact
st.write("Delete a contact")
selected_contact_delete = st.selectbox("Select contact to delete", options=contact_options)
if st.button("Delete Contact"):
    row_index = df.index[df.apply(lambda row: f"{row['Name']} {row['Family']}", axis=1) == selected_contact_delete].tolist()[0] + 2
    sheet.delete_row(row_index)
    st.success("Contact deleted successfully!")

# Print results using a loop
st.write("Use [FOR command] to show data:")
for row in df.itertuples():
    st.write(f"Name : {row.Name} , Family: {row.Family} , Age: {row.Age}, City: {row.City}")
