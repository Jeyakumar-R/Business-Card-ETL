from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import difflib
import easyocr
import json
import cv2
import re
import io

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=st.secrets.sql.password,
    database="bizcardx"
)

cursor = conn.cursor()

def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            designation VARCHAR(255),
            company_name VARCHAR(255),
            mobile_number VARCHAR(255),
            email VARCHAR(255),
            website VARCHAR(255),
            address VARCHAR(255),
            city VARCHAR(255),
            state VARCHAR(255),
            pincode VARCHAR(255),
            image LONGBLOB,
            UNIQUE KEY unique_card (name, designation, company_name)
        )
    """)
    conn.commit()

def extract_information(image):
    
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    

    extracted_info = {
        'name': '',
        'designation': '',
        'company_name': '',
        'mobile_number': '',
        'email': '',
        'website': '',
        'address': '',
        'city': '',
        'state': '',
        'pincode': ''
    }

    extracted_lines = [text[1] for text in result]
    
    # Extract name
    if extracted_lines:
        extracted_info['name'] = extracted_lines.pop(0).title()

    # Keywords for designation
    keywords = ['engineer', 'manager', 'director', 'executive', 'ceo', 'cto','designer', 'stylist', 'cfo', 'coo', 'vp', 'president', 'chairman', 'founder', 'partner', 'consultant']

    # Extract designation
    for line in extracted_lines:
        for keyword in keywords:
            if keyword in line.lower():
                extracted_info['designation'] = line.title()
                extracted_lines.remove(line)
                break

     # Extract mobile number
    for line in extracted_lines:
        mobile_number = re.search(r'(\+?\d{1,4}\s?)?(\d{1,4}-\d{1,4}-\d{1,4}|\d{9,12})', line)
        if mobile_number:
            extracted_info['mobile_number'] = line
            extracted_lines.remove(line)
            break

    # Extract email
    for line in extracted_lines:
        email = re.search(r'[\w\.-]+@[\w\.-]+', line)
        if email:
            extracted_info['email'] = email.group()
            extracted_lines.remove(line)
            break

    # Extract website
    for line in extracted_lines:
        website = re.search(r'((https?://)?([wW]{3}([\. ]))?\S+\.\S+)', line)
        if website:
            website_text = website.group(0)
            if 'www' in website_text.lower() and 'www.' not in website_text.lower() and website_text.count('.') == 1:
                website_text = website_text.replace('www', 'www.').replace('WWW', 'www.')
                website_text = website_text.replace('www. ', 'www.')
            
            elif 'www' not in website_text.lower():
                website_text = 'www.' + website_text
                
            extracted_info['website'] = website_text
            extracted_lines.remove(line)

    # Extract address
    for line in extracted_lines:
        address_match = re.search(r'(\d+\s+[A-Za-z]+(?:\s+[A-Za-z]+)*)(?:\s+(?:st|ST|sT|St|street|Street|Road|road)\b(.+))?', line)
        if address_match:
            address = address_match.group(1)
            remaining_content = line.replace(address, "").strip()
            extracted_info['address'] = address.strip()
            if remaining_content:
                extracted_lines[extracted_lines.index(line)] = remaining_content
            else:
                extracted_lines.remove(line)
            break
    
    for line in extracted_lines:
        if line == 'St ,':
            extracted_lines.remove(line)

    state_names = [
                    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
                    'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
                    'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
                    'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
                    'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Ladakh', 'Lakshadweep', 'Puducherry'
                    ]
    
    for i, line in enumerate(extracted_lines):
        state_match = difflib.get_close_matches(line.lower(), state_names, n=1, cutoff=0.5)
        if state_match:
            extracted_info['state'] = state_match[0].strip()
            extracted_lines[i] = line.replace('TamilNadu', '')
            break
               
    # Extract pincode
    pincode_patterns = [
                        r'(?<!\S)\d{6,7}\b'
                        ]
    
    for pattern in pincode_patterns:
        for line in extracted_lines:
            pincode_match = re.search(pattern, line)
            if pincode_match:
                extracted_info['pincode'] = pincode_match.group(0)
                extracted_lines.remove(line)
                break
    
    keywords = ['electricals', 'medicals', 'chemicals', 'digitals', 'designs', 'insurance', 'airlines', 'solutions', 'restaurant', 'hotel', 'pharmacy', 'mechanicals', 'automobiles', 'constructions', 'finance', 'tech', 'supermarket', 'hospital', 'school', 'logistics', 'telecommunications', 'telecom']

    # Extract company name
    removal_indices = []
    for i, line in enumerate(extracted_lines):
        for keyword in keywords:
            if keyword.lower() in line.lower() and keyword.lower() != 'electricals':
                if i > 0:
                    previous_line = extracted_lines[i-1].strip()
                    extracted_info['company_name'] = (previous_line + ' ' + line.strip()).title()
                    removal_indices.extend([i-1, i])
                break
            elif keyword.lower() in line.lower() and keyword.lower() == 'electricals':
                if i > 0:
                    extracted_info['company_name'] = (line.strip()).title()
                    removal_indices.extend([i])
                break

    # Remove lines from extracted_lines list
    
    for index in sorted(removal_indices, reverse=True):
        extracted_lines.pop(index)

    # Extract remaining lines as city
    
    city_line = extracted_lines[-1].strip()
    city_line = re.sub(r'[^\w\s]', '', city_line)
    city_words = city_line.split()
    extracted_info['city'] = city_words[-1] if city_words else ''
    extracted_lines.remove(extracted_lines[-1])
    return extracted_info

def insert_data(data):
    image_data = data.pop('image')
    values = tuple(data.values()) + (image_data,)

    cursor.execute("""
        INSERT IGNORE INTO business_cards (name, designation, company_name, mobile_number, email, website, address, city, state, pincode, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, values)
    conn.commit()

def get_unique_company_names():
    cursor.execute("SELECT DISTINCT company_name FROM business_cards")
    result = cursor.fetchall()
    return [row[0] for row in result]

def get_person_names(company_name):
    cursor.execute("SELECT name FROM business_cards WHERE company_name = %s", (company_name,))
    result = cursor.fetchall()
    return [row[0] for row in result]

def get_person_data(company_name, person_name):
    cursor.execute("SELECT * FROM business_cards WHERE name = %s AND company_name = %s", (person_name, company_name))
    result = cursor.fetchone()
    return result

def update_field(company_name, person_name, field, value):
    cursor.execute(f"UPDATE business_cards SET {field} = %s WHERE company_name = %s AND name = %s", (value, company_name, person_name))
    conn.commit()

def delete_card(company_name, person_name):
    cursor.execute("DELETE FROM business_cards WHERE company_name = %s AND name = %s", (company_name, person_name))
    conn.commit()

def get_data():
    cursor.execute("SELECT * FROM business_cards")
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in result]
    return data

def main():
    
    st.set_page_config(page_title = 'BizCardX', layout='wide', page_icon='Related Images and Videos/card.png')
    
    page_title, lottie, buff= st.columns([65, 37, 5])

    page_title.title('Business Card Extractor')

    with open (r"Related Images and Videos/Biz.json") as f:
        lottie_json = json.load(f)
    with lottie:
        st_lottie(lottie_json, height= 100, width=200)
    
    create_table()
    
    col, buff = st.columns([2, 1])
        
    uploaded_file = col.file_uploader("Upload an image of the business card", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        add_vertical_space(1)
        st.image(image, width = 400)
    
    add_vertical_space(1)    
    
    extract = st.button('Extract and Upload', key = 'ext')
    
    add_vertical_space(1)
    
    extracted_info = {}
    
    if uploaded_file and extract:
        
        extracted_info = extract_information(image)
        
        st.subheader("Extracted Information")
        df = pd.DataFrame.from_dict(extracted_info, orient="index", columns=["Value"])
        df.index = df.index.str.replace('_', ' ').str.title()
        st.data_editor(df, key = 'edit')
        
        image = image.dumps()
        extracted_info['image'] = image
        insert_data(extracted_info)        
        st.write(f"Business card saved successfully!")
        
        
    tab1, tab2, tab3 = st.tabs(["View and Update Data", "Delete Data", "Download Data"])
    
    with tab1:
        st.subheader("Update Data")
        
        col1, col2, buff = st.columns([2.5, 2.5, 3.5])
        
        company_names = get_unique_company_names()
        selected_company = col1.selectbox("Company", ["Select Company"] + company_names, key = 'company')

        if selected_company != "Select Company":
            person_names = get_person_names(selected_company)
            selected_person = col2.selectbox("Person", ["Select Person"] + person_names, key = 'person')

            if selected_person != "Select Person":
                person_data = get_person_data(selected_company, selected_person)

                df = pd.DataFrame([person_data], columns=['ID', 'Name', 'Designation', 'Company Name', 'Mobile Number', 'Email',
                                                        'Website', 'Address', 'City', 'State', 'Pincode', 'Image'])
                
                df = df.iloc[:, :-1]
                
                add_vertical_space(1)
                
                st.dataframe(df)
                
                col3, buff1, col4, buff2 = st.columns([2, 0.3, 3, 2])
                selected_field = col3.selectbox("Select a Field to Modify", ["Select Field"] + list(df.columns), key = 'field')
                
                if selected_field != "Select Field":
                    new_value = col4.text_input("Enter New Value", df[selected_field].iloc[0], key = 'value')
                    col5, col6 = st.columns([2, 1.7])
                    update_button = col6.button("Update Value")

                    if update_button:
                        selected_field = selected_field.lower().replace(' ', '_')
                        update_field(selected_company, selected_person, selected_field, new_value)
                        st.success(f"Updated {selected_field} of {selected_person} to {new_value}")
    with tab2:
        
        st.subheader("Delete Data")
        
        col7, col8, buff = st.columns([2.5, 2.5, 3.5])
        
        company_names = get_unique_company_names()
        selected_company = col7.selectbox("Company", ["Select Company"] + company_names, key = 'company_1')

        if selected_company != "Select Company":
            person_names = get_person_names(selected_company)
            selected_person = col8.selectbox("Person", ["Select Person"] + person_names, key = 'person_1')

            add_vertical_space(1)   
            
            if selected_person != "Select Person":
                
                person_data = get_person_data(selected_company, selected_person)

                df = pd.DataFrame([person_data], columns=['ID', 'Name', 'Designation', 'Company Name', 'Mobile Number', 'Email',
                                                        'Website', 'Address', 'City', 'State', 'Pincode', 'Image'])
                
                df = df.iloc[:, :-1]
                
                st.dataframe(df)
                
                delete_button = st.button("Delete Card")
                if delete_button:
                    delete_card(selected_company, selected_person)
                    st.success("Card data deleted successfully.")

    with tab3:
        
        st.subheader("Download Data")
        
        col1, col2, col3 = st.columns(3)
        
        data = get_data()

        data_without_image = [{key: value for key, value in record.items() if key != 'image' and key != 'id'} for record in data]

        df = pd.DataFrame(data_without_image)

        csv_bytes = df.to_csv(index=False).encode()
        col1.download_button("Download CSV file", data=csv_bytes,
                            file_name= "card_data.csv",
                            mime="text/csv")

        json_bytes = df.to_json(orient="records").encode()
        col2.download_button("Download JSON file", data=json_bytes,
                            file_name="card_data.json",
                            mime="application/json")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, engine ='xlsxwriter', index = False)
        excel_bytes = excel_buffer.getvalue()

        col3.download_button("Download Excel file", data = excel_bytes,
                            file_name = 'card_data.xlsx',
                            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            key = 'excel'
                            )

    cursor.close()
    conn.close()
    
    st.sidebar.image('Related Images and Videos/Biz.gif')
    add_vertical_space(2)
    st.sidebar.subheader("How can this app be handy?")
    st.sidebar.markdown("""
                        - Simplify the extraction, transformation, and loading of information from business cards.
                        - Capture and manage essential details like names, designations, contact information, and more.
                        - Stay organized, save time, and eliminate manual data entry with this BizcardX webapp.
                        """)

if __name__ == "__main__":
    main()