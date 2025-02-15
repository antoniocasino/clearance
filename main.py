import streamlit as st
import time
import datetime
from utils import calculate_kdn_qbwn, create_pdf
from clearance import clearance_page 
def home_page():
    st.header("Home Page")
    st.write("Welcome to the home page!")

def contacts_page():
    st.header("Contacts Page")
    st.write("Welcome to the contacts page!")

def main():
    st.set_page_config(page_title="Clearance Calculator")            

    tabs = ["Home", "Clearance", "Contacts"]    
    tab1, tab2, tab3 = st.tabs(tabs)
    
    with tab1:
        home_page()
    with tab2:
        clearance_page()
    with tab3:
        contacts_page()
   
        
   
#Invoking main function
if __name__ == '__main__':
    main()