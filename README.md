# Business Card Extraction web app

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://business-card-extraction.streamlit.app/)

This is a simple but handy Business Card Management Web Application that allows users to extract information from business cards, store the extracted data in local MySQL database (In cloud, I have used Mongo DB), perform operations such as updating, deleting, and retrieving the data, and also provides options to export the data in CSV, JSON, or Excel formats.

## Prerequisites

Before you begin, you will need to have a few tools installed on your machine:

* Python 3.7 or higher.
    [Note: Streamlit only supports .py files as of now. So, notebook(.ipynb) files are not recommended]
* MySQL Workbench software.
* The re, difflib, easyocr, numpy, pandas and streamlit, mysql-connector libraries and OpenCV or any other image handling package.

#### Python

Python is the programming language used to develop this project. It is a popular high-level programming language known for its readability and versatility. It is widely used for web development, data analysis, and machine learning.

#### MySQL

MySQL is an open-source relational database management system. We used it here to store and manage the cleaned and processed data. It provides a scalable and secure solution for managing large amounts of data.

#### Streamlit

Streamlit is an open-source Python library that makes it easy to create and share custom web apps for machine learning and data science. We used it here to deploy our project as a web app. It made it easy to create an interactive user interface for exploring and visualizing the raw image and extrated data and to provide great user interface to get user input.

#### EasyOCR

Easyocr is a Python library for optical character recognition (OCR). It simplifies the process of extracting text from images by providing an interface to pre-trained OCR models. We used it here to extract text from business card images, enabling the automated extraction of information such as name, designation, company name, etc.

#### Regex

re is the in-built regular expression library in Python. It provides functions and patterns for pattern matching and text manipulation. In this project, we used it for pattern matching and searching tasks, such as extracting phone numbers or email addresses from the extracted text.

#### Difflib

Difflib is a library that provides classes and functions for comparing sequences and calculating differences between them. It uses distance algorithms like levenshtein distance. In this project, we used it to compare and find similarities between different state names list and the name of state in business cards.

#### Pandas

Pandas is a popular Python library used for data manipulation and analysis. We used pandas to convert extracted info stored in database into dataframe inorder to display and to convert dataframe into .csv, .json and .dict formats.

#### Numpy

Numpy is a fundamental library for scientific computing in Python. It provides high-performance arrays and mathematical functions that can be used for various calculations and computations. We used it here to handle converted image data.

## Ethical perspective of using business card details

Ethical perspectives of using business card details require careful consideration of privacy concerns. Respecting individuals' privacy rights, obtaining consent, and implementing robust data security measures are crucial in maintaining ethical practices. Striking a balance between utilizing the information for intended purposes and safeguarding individuals' data control is essential in upholding ethical standards.

## Features

* ##### Image Extraction: Utilizes EasyOCR library to extract text information such as name, designation, company name, contact information, and address from business card images.
* ##### Data Storage and Retrieval: Utilizes your MySQL database to store extracted business card data securely and enables efficient retrieval and querying of stored data for further processing and analysis.

* ##### Data Updation: Provides functionality to update and modify the extracted business card data by allowing users to modify individual fields such as name, designation, company name, contact information, and address.

* ##### Data Deletion: Enables the removal of specific business card data from the database by getting user input for person name and company name.

* ##### Data Export: Offers options to export the business card data in various formats such as CSV, JSON, and Excel.

## User Guide

    1. Clone the repository to your local machine using the following command: `git clone [https://github.com/Nirmal-Data-Scientist/Business-Card-ETL.git]`.
    
    2. Install the required libraries by running the following command: pip install -r requirements.txt.
    
    3. Open a terminal window and navigate to the directory where the app is located using the following command: cd [.py file directory].
    
    4. Run the command [streamlit run Business_Card_Extraction.py] to start the app.
    
    5. The app should now be running on a local server. If it doesn't start automatically, you can access it by going to either 
        * Local URL: [http://localhost:8501] or * Network URL: [http://192.168.43.83:8501].
    
    6. Click on the "Upload" button in the webapp and select the image file containing the business card(s).
    
    7. Once the images are processed, review the extracted data displayed on the screen.
    
    8. Use selection boxes and input fields to manage and modify the extracted data.
    
    9. Select the company name and person's name from the dropdown lists and click "Delete" to remove data.
    
    10. Choose the export format (CSV, JSON, or Excel) and click "Export" to download all the extracted data.

To modify the app, you can:

    1. Add user authentication and authorization for secure access to the application.
    2. Implement advanced search and filtering options for efficient data retrieval.
    3. Add visualization capabilities by incorporating interactive charts and graphs.
    4. Integrate with email or contact management systems to synchronize and update contact information.

## Potential Applications

The Business Card ETL (Extract, Transform, Load) Web Application has several potential applications, including:

1. Business Networking: The app simplifies the process of digitizing and managing business card information. It allows users to quickly extract and store contact details, making it easier to connect and network with individuals and businesses.

2. Contact Management: The app serves as a digital repository for organizing and storing contact information. Users can easily update, search, and manage their contacts in one centralized location, eliminating the need for physical business cards or scattered contact lists.

3. Data Extraction and Analysis: The app's extraction capabilities allow for the automated extraction of relevant data from business cards, such as names, phone numbers, and email addresses. This data can be further analyzed and used for various purposes, such as lead generation, market research, or customer profiling.

4. Streamlined Business Processes: By automating the extraction and management of business card information, the app saves time and effort. It streamlines business processes, allowing users to focus on meaningful interactions and business activities rather than manual data entry and organization.


## Potential issues with the app

1. ##### Variability in Business Card Designs:

   The app relies on specific patterns and regular expressions to extract information from business cards. However, different card designs, fonts, font sizes, spacing, and structural variations can impact the accuracy of the extraction process. Users may need to customize or adapt the regular expressions to match their specific card layouts.

2. ##### Accuracy of OCR and Text Matching:

   EasyOCR accuracy and difflib accuracy can have limitations and may result in false matches or mismatches, affecting the overall performance of the app.

3. ##### Image Quality and Challenges:

   The quality of business card images can vary, and low-resolution or poorly captured images may lead to inaccurate OCR results. Users should ensure that they capture or scan clear and well-lit images for better extraction accuracy. Furthermore, complex card designs with intricate graphics or unconventional layouts may pose challenges for accurate data extraction.

4. ##### Limitations in Streamlit Cloud Environment:

   The app relies on a local database connection to store and retrieve business card data. However, Streamlit Cloud does not currently provide proper support for connecting to local databases from cloud-deployed applications and this is under development using st.experimental_connection() right now. As a result, this app won't work in a Streamlit Cloud environment without additional modifications or alternative cloud database hosting options. So, I have used MongoDB  atlas database for cloud version of the app.

## Web App Snap

![image](https://github.com/Nirmal-Data-Scientist/Business-Card-ETL/assets/123751119/5913276a-20fc-46db-aed4-feeea37919ec)

![image](https://github.com/Nirmal-Data-Scientist/Business-Card-ETL/assets/123751119/a7dc1ca2-442f-40be-a919-7716440e695b)

![image](https://github.com/Nirmal-Data-Scientist/Business-Card-ETL/assets/123751119/a846cf81-c980-4e95-acd2-e1b908350e2c)

![image](https://github.com/Nirmal-Data-Scientist/Business-Card-ETL/assets/123751119/a6da1c7e-cab8-4c0e-8185-0b1f9680050b)

## Web App Demo Video

<a href="https://www.linkedin.com/posts/nirmal-data-scientist_businesscardetl-productivity-automation-activity-7075964385311014912-IzcY?utm_source=share&utm_medium=member_desktop" target="_blank">Demo Video</a>

## Streamlit web URL

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://business-card-extraction.streamlit.app/)

## Disclaimer

This application is intended for educational and research purposes only and should not be used for any commercial or unethical activities.

## Contact

If you have any questions, comments, or suggestions for the app, please feel free to contact me at [nirmal.works@outlook.com] or raise an issue in GitHub.
