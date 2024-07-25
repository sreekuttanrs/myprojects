from flask import Flask, request, render_template
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os
import pytesseract
import cv2
import re
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/sree/myproject/uploads'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'userdata'
app.config['MYSQL_PASSWORD'] = 'userdata'
app.config['MYSQL_DATABASE'] = 'id_data_db'

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image from path: {image_path}")
        return ""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def format_date(date_str):
    try:
        # Assuming date format might be in the format of DD/MM/YYYY or similar
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")  # MySQL expects YYYY-MM-DD format
    except ValueError:
        return None

def adhaar_read_data(text):
    res = text.split()
    name = None
    dob = None
    adh = None
    sex = None
    text0 = []
    text1 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = s.replace('\n', '')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    if 'female' in text.lower():
        sex = "FEMALE"
    else:
        sex = "MALE"
    
    text1 = list(filter(None, text1))
    text0 = text1[:]
    
    try:
        # Cleaning first names
        name = text0[0]
        name = name.rstrip()
        name = name.lstrip()
        name = name.replace("8", "B")
        name = name.replace("0", "D")
        name = name.replace("6", "G")
        name = name.replace("1", "I")
        name = re.sub('[^a-zA-Z ]+', ' ', name)

        # Cleaning DOB
        dob = text0[1][-10:]
        dob = dob.rstrip()
        dob = dob.lstrip()
        dob = dob.replace('l', '/')
        dob = dob.replace('L', '/')
        dob = dob.replace('I', '/')
        dob = dob.replace('i', '/')
        dob = dob.replace('|', '/')
        dob = dob.replace('\"', '/1')
        dob = dob.replace(":", "")
        dob = dob.replace(" ", "")
        dob = format_date(dob)  # Format the date for MySQL

        # Cleaning Adhaar number details
        aadhar_number = ''
        for word in res:
            if len(word) == 4 and word.isdigit():
                aadhar_number = aadhar_number + word + ' '
        if len(aadhar_number) >= 14:
            print("Aadhar number is :" + aadhar_number)
        else:
            print("Aadhar number not read")
        adh = aadhar_number

    except:
        pass

    data = {}
    data['Name'] = name
    data['Date of Birth'] = dob if dob else '1970-01-01'  # Provide a default date if not found
    data['Adhaar Number'] = adh
    data['Sex'] = sex
    data['ID Type'] = "Adhaar"
    return data

def pan_read_data(text):
    res = text.split()
    name = None
    pan_number = None
    sex = None

    text0 = []
    text1 = []
    lines = text.split('\n')
    for lin in lines:
        s = lin.strip()
        s = s.replace('\n', '')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)

    if 'female' in text.lower():
        sex = "FEMALE"
    else:
        sex = "MALE"
    
    text1 = list(filter(None, text1))
    text0 = text1[:]
    
    try:
        # Cleaning names
        name = text0[0]
        name = name.rstrip()
        name = name.lstrip()
        name = re.sub('[^a-zA-Z ]+', ' ', name)

        # Cleaning PAN number
        pan_number = None
        for word in res:
            if len(word) == 10 and re.match(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', word):
                pan_number = word
                break

    except:
        pass

    data = {}
    data['Name'] = name
    data['Date of Birth'] = None
    data['PAN Number'] = pan_number
    data['Sex'] = sex
    data['ID Type'] = "PAN"
    return data

def identify_id_type(text):
    # Check for variations of the PAN card identifier text
    pan_keywords = [
        "INCOME TAX DEPARTMENT GOVT. OF INDIA",
        "INCOME AX DEPARTMENT GOVE. OF INDIA"
    ]
    if any(keyword in text.upper() for keyword in pan_keywords):
        return pan_read_data(text)
    else:
        return adhaar_read_data(text)

def save_to_database(data):
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        cursor = conn.cursor()
        if data['ID Type'] == 'Adhaar':
            query = """INSERT INTO adhaar_details (name, dob, aadhar_number, sex, address) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (data['Name'], data['Date of Birth'], data['Adhaar Number'], data['Sex'], ''))
        elif data['ID Type'] == 'PAN':
            query = """INSERT INTO pan_details (name, pan_number, sex) 
                       VALUES (%s, %s, %s)"""
            cursor.execute(query, (data['Name'], data['PAN Number'], data['Sex']))
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message="No file part")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', message="No selected file")

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            text = extract_text_from_image(file_path)
            id_data = identify_id_type(text)
            save_to_database(id_data)
            return render_template('index.html', details=id_data)

    return render_template('index.html', details={})

if __name__ == '__main__':
    app.run(debug=True)
