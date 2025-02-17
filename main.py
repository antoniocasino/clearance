import streamlit as st
import streamlit.components.v1 as components
import time
import datetime
from components.kdn_calculator import calculate_kdn_qbwn
from pages.clearance import clearance_page 
from pages.home import home_page
from pages.contacts import contacts_page

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