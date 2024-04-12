



import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3


def img_to_txt(path):

  input_img= Image.open(path)

  # convert img to array format
  image_array= np.array(input_img)

  reader= easyocr.Reader(['en'])
  text= reader.readtext(image_array, detail= 0)

  return text, input_img



def extracted_text(texts):

  extracted_dict= {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
                    "ADDRESS":[], "PINCODE":[]}

  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):

       extracted_dict ["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extracted_dict["EMAIL"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or 'wwW' in texts[i]:
      small = texts[i].lower()
      extracted_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extracted_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]',texts[i]):
      extracted_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,;]','',texts[i])
      extracted_dict["ADDRESS"].append(remove_colon)

  for key, value in extracted_dict.items():
    if len(value)>0:

      Concatenate= " ".join(value)
      extracted_dict[key] = [Concatenate]

    else:
      value = "NA"
      extracted_dict[key] = [value]

  return extracted_dict



#STREAMLIT PART

st.set_page_config(layout = "wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")

with st.sidebar:

  select= option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])

if select == "Home":

  image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-mnIkBDCJ8COUP5ihU51dyVCoDTC8YuTbug&usqp=CAU"
  
  # Display the icon image at the top
  st.sidebar.image(image, use_column_width=True)


  st.markdown(":black_large_square: **Project Title** : BizCardX: Extracting Business Card Data with OCR")

  technologies = "streamlit GUI, SQL, Data Extraction"
  st.markdown(f":black_large_square: **Technologies** : {technologies}")

  overview = "Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR."
  st.markdown(f":black_large_square: **Overview** : {overview}")
  icon_url = "https://png.pngitem.com/pimgs/s/30-304321_business-cards-png-business-card-mockup-png-transparent.png"
  st.image(icon_url,use_column_width=True) 

elif select == "Upload & Modifying":
  img = st.file_uploader("Upload the Image", type= ["png","jpg","jpeg"])

  if img is not None:
    st.image(img, width= 300)

    text_image, input_img= img_to_txt(img)

    text_dict = extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    df= pd.DataFrame(text_dict)

    Image_bytes = io.BytesIO()
    input_img.save(Image_bytes, format ="PNG")

    image_data = Image_bytes.getvalue()

    # creating dict
    data = {"IMAGE":[image_data]}

    df_1 = pd.DataFrame(data)

    concat_df = pd.concat([df,df_1],axis=1)

    st.dataframe(concat_df)

    button_1 = st.button("Save", use_container_width = True)

    if button_1:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      # Table creation

      create_table_query= '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(200),
                                                                        designation varchar(200),
                                                                        company_name varchar(200),
                                                                        contact varchar(200),
                                                                        email varchar(200),
                                                                        website text,
                                                                        address text,
                                                                        pincode varchar(200),
                                                                        image text)'''

      cursor.execute(create_table_query)
      mydb.commit()

      # Insert_Query

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact, email, website, address, pincode, image)

                                                                          values(?,?,?,?,?,?,?,?,?)'''

      datas = concat_df.values.tolist()[0]
      cursor.execute(insert_query,datas)
      mydb.commit()

      st.success("SAVED SUCCESSFULLY")

  method = st.radio("Select the Method",["None","Preview","Modify"])

  if method == "None":
    st.write("")

  if method =="Preview":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()


    # select query

    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns= ("NAME", "DESIGNATION", "COMPANY_NAME","CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    st.dataframe(table_df)

  elif method == "Modify":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns= ("NAME", "DESIGNATION", "COMPANY_NAME","CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))

    col1,col2 = st.columns(2)
    with col1:

      selected_name = st.selectbox("Select the name", table_df["NAME"])

    df_3 = table_df[table_df["NAME"] == selected_name]

    df_4 = df_3.copy()


    col1,col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("Name",df_3["NAME"].iloc[0])
      mo_desi = st.text_input("Designation",df_3["DESIGNATION"].iloc[0])
      mo_com_name = st.text_input("Company_name",df_3["COMPANY_NAME"].iloc[0])
      mo_cont = st.text_input("Contact",df_3["CONTACT"].iloc[0])
      mo_email = st.text_input("Email",df_3["EMAIL"].iloc[0])

      df_4["NAME"] = mo_name
      df_4["DESIGNATION"] = mo_desi
      df_4["COMPANY_NAME"] = mo_com_name
      df_4["CONTACT"] = mo_cont
      df_4["EMAIL"] = mo_email

    with col2:
      mo_website = st.text_input("Website",df_3["WEBSITE"].iloc[0])
      mo_address = st.text_input("Address",df_3["ADDRESS"].iloc[0])
      mo_pincode = st.text_input("Pincode",df_3["PINCODE"].iloc[0])
      mo_image = st.text_input("Image",df_3["IMAGE"].iloc[0])

      df_4["WEBSITE"] = mo_website
      df_4["ADDRESS"] = mo_address
      df_4["PINCODE"] = mo_pincode
      df_4["IMAGE"] = mo_image

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:
      button_3 = st.button("Modify", use_container_width = True)

    if button_3:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{selected_name}'")
      mydb.commit()

      # Insert_Query

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact, email, website, address, pincode, image)

                                                                          values(?,?,?,?,?,?,?,?,?)'''

      datas = df_4.values.tolist()[0]
      cursor.execute(insert_query,datas)
      mydb.commit()

      st.success("MODIFIED SUCCESSFULLY")





elif select == "Delete":
    
  mydb = sqlite3.connect("bizcardx.db")
  cursor = mydb.cursor()

  col1,col2 = st.columns(2)
  with col1:

    select_query = "SELECT NAME FROM bizcard_details"

    cursor.execute(select_query)
    table1 = cursor.fetchall()
    mydb.commit()

    names = []

    for i in table1:
      names.append(i[0])

    name_select = st.selectbox("Select the name", names)

  with col2:

    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"

    cursor.execute(select_query)
    table2 = cursor.fetchall()
    mydb.commit()

    designation = []

    for j in table2:
      designation.append(j[0])

    designation_select = st.selectbox("Select the designation", designation)


  if name_select and designation_select:
    col1,col2,col3 = st.columns(3)

    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Select Designation : {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("Delete", use_container_width= True)

      if remove:

        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        mydb.commit()

        st.warning("DELETED")


