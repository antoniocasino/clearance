import streamlit as st
import streamlit.components.v1 as components

from components.kdn_calculator import calculate_kdn_qbwn
from pages.clearance import clearance_page 
from pages.home import home_page
from pages.koa import koa_page

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
    tabs = ["Home", "Clearance", "KoA"]    
    tab1, tab2, tab3 = st.tabs(tabs)
    
    with tab1:
        home_page()
    with tab2:
        clearance_page()
    with tab3:
        koa_page()
   
        
   
#Invoking main function
if __name__ == '__main__':
    main()