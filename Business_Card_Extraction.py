from streamlit_extras.add_vertical_space import add_vertical_space 
from streamlit_lottie import st_lottie
import mysql.connector # type: ignore
import streamlit as st
import pandas as pd
import numpy as np
import difflib
import easyocr
import json
import cv2
import re
import io

# Connect to MySQL database
conn = mysql.connector.connect(
    host=st.secrets["mysql_db"]["host"],
    user=st.secrets["mysql_db"]["user"],
    password=st.secrets["mysql_db"]["password"],
    database=st.secrets["mysql_db"]["database"]
)
cursor = conn.cursor()

# Create table if it doesn't exist
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
        pincode VARCHAR(20)
    )
""")


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
    if extracted_lines:
        extracted_info['name'] = extracted_lines.pop(0).title()

    keywords = ['engineer', 'manager', 'director', 'executive', 'ceo', 'cto', 'designer', 'stylist', 'cfo', 'coo', 'vp', 'president', 'chairman', 'founder', 'partner', 'consultant']

    for line in extracted_lines:
        for keyword in keywords:
            if keyword in line.lower():
                extracted_info['designation'] = line.title()
                extracted_lines.remove(line)
                break

    for line in extracted_lines:
        mobile_number = re.search(r'(\+?\d{1,4}\s?)?(\d{1,4}-\d{1,4}-\d{1,4}|\d{9,12})', line)
        if mobile_number:
            extracted_info['mobile_number'] = line
            extracted_lines.remove(line)
            break

    for line in extracted_lines:
        email = re.search(r'[\w\.-]+@[\w\.-]+', line)
        if email:
            extracted_info['email'] = email.group(0)
            extracted_lines.remove(line)
            break

    for line in extracted_lines:
        website = re.search(r'((https?://)?([wW]{3}([\. ]))?\S+\.\S+)', line)
        if website:
            website_text = website.group(0)
            if 'www' not in website_text.lower():
                website_text = 'www.' + website_text
            extracted_info['website'] = website_text
            extracted_lines.remove(line)

    for line in extracted_lines:
        address_match = re.search(r'(\d+\s+[A-Za-z]+(?:\s+[A-Za-z]+)*)(?:\s+(?:st|ST|sT|St|street|Street|Road|road)\b(.+))?', line)
        if address_match:
            extracted_info['address'] = address_match.group(1)
            extracted_lines.remove(line)
            break

    state_names = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana',
                   'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
                   'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
                   'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
                   'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Ladakh', 'Lakshadweep', 'Puducherry']

    for line in extracted_lines:
        state_match = difflib.get_close_matches(line, state_names, n=1, cutoff=0.5)
        if state_match:
            extracted_info['state'] = state_match[0]
            extracted_lines.remove(line)
            break

    for line in extracted_lines:
        pincode_match = re.search(r'\b\d{6,7}\b', line)
        if pincode_match:
            extracted_info['pincode'] = pincode_match.group(0)
            extracted_lines.remove(line)
            break

    keywords = ['electricals', 'medicals', 'chemicals', 'digitals', 'designs', 'insurance', 'airlines', 'solutions', 'restaurant', 'hotel', 'pharmacy', 'mechanicals', 'automobiles', 'constructions', 'finance', 'tech', 'supermarket', 'hospital', 'school', 'logistics', 'telecommunications', 'telecom']

    for line in extracted_lines:
        for keyword in keywords:
            if keyword in line.lower():
                extracted_info['company_name'] = line.title()
                extracted_lines.remove(line)
                break

    if extracted_lines:
        extracted_info['city'] = extracted_lines[-1]
        extracted_lines.pop()

    return extracted_info


def insert_data(data):
    cursor.execute("""
        INSERT INTO business_cards (name, designation, company_name, mobile_number, email, website, address, city, state, pincode)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            designation=VALUES(designation),
            mobile_number=VALUES(mobile_number),
            email=VALUES(email),
            website=VALUES(website),
            address=VALUES(address),
            city=VALUES(city),
            state=VALUES(state),
            pincode=VALUES(pincode)
    """, (data['name'], data['designation'], data['company_name'], data['mobile_number'], data['email'], data['website'], data['address'], data['city'], data['state'], data['pincode']))
    conn.commit()


def get_unique_company_names():
    cursor.execute("SELECT DISTINCT company_name FROM business_cards")
    return [row[0] for row in cursor.fetchall()]


def get_person_names(company_name):
    cursor.execute("SELECT name FROM business_cards WHERE company_name = %s", (company_name,))
    return [row[0] for row in cursor.fetchall()]


def get_person_data(company_name, person_name):
    cursor.execute("SELECT * FROM business_cards WHERE company_name = %s AND name = %s", (company_name, person_name))
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else {}


def update_field(company_name, person_name, field, value):
    cursor.execute(f"UPDATE business_cards SET {field} = %s WHERE company_name = %s AND name = %s", (value, company_name, person_name))
    conn.commit()


def delete_card(company_name, person_name):
    cursor.execute("DELETE FROM business_cards WHERE company_name = %s AND name = %s", (company_name, person_name))
    conn.commit()


def get_data():
    cursor.execute("SELECT * FROM business_cards")
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main():
    st.set_page_config(page_title='BizCardX', page_icon='Related Images and Videos/card.png', layout='wide')
    
    st.title('Business Card Extractor')

    uploaded_file = st.file_uploader("Upload an image of the business card", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
        st.image(image, width=400)

    if st.button('Extract and Upload'):
        extracted_info = extract_information(image)
        st.subheader("Extracted Information")
        df = pd.DataFrame.from_dict(extracted_info, orient="index", columns=["Value"])
        st.dataframe(df)
        insert_data(extracted_info)
        st.success("Business card saved successfully!")

    if st.button('View All Data'):
        data = get_data()
        df = pd.DataFrame(data)
        st.dataframe(df)

if __name__ == "__main__":
    main()