import streamlit as st
import streamlit.components.v1 as components

from pages.clearance import clearance_page 
from pages.home import home_page
from pages.key_information import key_information_page
from pages.koa import koa_page
from pages.adequacy import adequacy_page
from pages.assessment import assessment_page
from pages.prescription import prescription_page

def main():
    st.set_page_config(page_title="Clearance Calculator")            
    st.markdown("""
        <style>
         [data-baseweb="tab"]>div {
            font-size: large;
         }
        </style>
        """,
        unsafe_allow_html=True
    )      
    tabs = ["Home","Key Information" ,"Adequacy", "stdKt/V & EKRU", "Dose Calculator", "Kd&Qb", "KoA"]    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs)
    
    with tab1:
        home_page()
    with tab2:
        key_information_page()
    with tab3:
        adequacy_page()
    with tab4:
        assessment_page()
    with tab5:
        prescription_page()
    with tab6:
        clearance_page()
    with tab7:
        koa_page()              
   
#Invoking main function
if __name__ == '__main__':
    main()