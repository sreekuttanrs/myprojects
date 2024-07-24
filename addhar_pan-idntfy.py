import cv2
import pytesseract
import re

# Path to the Tesseract executable (Linux path)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def extract_text_from_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Failed to load image from path: {image_path}")
        return ""

    # Convert the image to grayscale (optional, but can improve OCR accuracy)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(gray)

    return text

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
    data['Date of Birth'] = dob
    data['Adhaar Number'] = adh
    data['Sex'] = sex
    data['ID Type'] = "Adhaar"
    return data

def pan_read_data(text):
    res = text.split()
    name = None
    pan_number = None
    dob = None
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
    data['Date of Birth'] = dob
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

if __name__ == "__main__":
    image_path = '/home/sree/myproject/page_1.jpg'  # Replace with your image path
    extracted_text = extract_text_from_image(image_path)
    print("Extracted Text:")
    print(extracted_text)
    
    id_data = identify_id_type(extracted_text)
    print("\nExtracted ID Data:")
    for key, value in id_data.items():
        print(f"{key}: {value}")
