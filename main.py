import streamlit as st
import streamlit.components.v1 as components
import time
import datetime
from utils import calculate_kdn_qbwn, create_pdf
from clearance import clearance_page 
import pandas as pd
def home_page():
    
    st.title("Dialysis Prescription Calculator")

    st.markdown("""
    <div class="section-title">Clearance Calculation</div>
    <p>The "Clearance" section is dedicated to prescription calculations.  By inputting the data shown in Table 1 and clicking "Calculate," the required dialyzer urea clearance (Kdn) to achieve the target eKt/V is determined.  The necessary blood flow rate (Qbn) to attain the calculated Kdn is also computed, considering the dialyzer's characteristics (KoA) and other operational parameters (QD, UF, HDFPRE, HDFPOST).</p>

    <p>The calculations are based on the same equations used in the "SPEEDY" software, as described by Casino and Basile in "A user-friendly tool for incremental haemodialysis prescription. Nephrol Dial Transplant. 2018;33(6): 1046-1053. <a href="https://doi.org/10.1093/ndt/gfx343" target="_blank">https://doi.org/10.1093/ndt/gfx343</a>"</p>
    """, unsafe_allow_html=True)



    input_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'Input': ["Patient ID", "Patient’s urea volume", "Expected intradialysis weight loss", "KoA in vitro of the dialyzer", "Pre-dialyzer infusion rate", "Post-dialyzer infusion rate", "Dialysate flow rate", "Session length", "eKt/V target of the current prescription"],
        'Symbol': ["PTID", "V", "UF", "KoA", "HDFPRE", "HDFPOST", "QD", "TD", "eKt/V"],
        'Units': ["", "L", "L or kg", "ml/min", "ml/min", "ml/min", "ml/min", "Min", "dimensionless"],
        'Min': ["", 20, 0.1, 600, 0, 0, 100, 60, 0.3],
        'Max': ["", 50, 5, 2000, 250, 150, 1000, 480, 2.0],
        'Example': ["PTID", 35, 2, 1200, 0, 0, 500, 240, 1.4]
    }
    df_input = pd.DataFrame(input_data)
    st.write("Input Data")  # Add a title for the input table
    st.dataframe(df_input,hide_index=True)  # or st.table(df_input) for a static table


    output_data = {
        '#': [10, 11],
        'Output': ["Dialyzer Urea Clearance needed to attain the eKt/V target *", "Blood flow rate needed to attain the required Kdn value *"],
        'Symbol': ["Kdn", "Qbn"],
        'Units': ["ml/min", "ml/min"],
        'Min': [100, 100],
        'Max': [300, 450],
        'Example': [239, 351]
    }

    df_output = pd.DataFrame(output_data)

    st.write("Output Data") # Add a title for the output table
    st.dataframe(df_output,hide_index=True) # or st.table(df_output) for a static table


    st.markdown("""
    <p>* The calculated values for Kdn and Qbn are theoretical estimates under ideal conditions. The actual values can be influenced by various factors, such as the measurement method used, variability of blood and dialysis flows, presence of vascular access recirculation, etc.</p>
    """, unsafe_allow_html=True)


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