import streamlit as st
import time
import datetime
from utils import calculate_kdn_qbwn
def main():
    st.set_page_config(page_title="Clearance Calculator")    
    st.title("Dialyzer Clearance needed (Kdn) to reach the target value of eKt/V") 
          
    
    
    patient_id = st.text_input("Patient Identifier", key="id")
    date = st.date_input(
        "Select a date (dd/mm/yyyy)",
        value=datetime.datetime.now(),
        format="DD/MM/YYYY",
    )
    vdp = st.number_input(
        "patient's urea volume (L) (acceptable range of values: 20-50)",
        min_value=20,
        max_value=50,       
        value=35,     
        step=1
    )
    uf = st.number_input(
        "expected intradialysis weight loss (L) (acceptable range of values: 0.1-5)",
        min_value=0.1,
        max_value=5.0,            
        step=0.1,
        value=2.0,
        format="%.2f"
    )  
    koavitro = st.number_input(
        "In vitro KOA of the dialyzer (ml/min) (acceptable range of values: 600-2000)",
        min_value=600,
        max_value=2000,            
        step=1,
        value=1200,
    )                       
    hdfpre = st.number_input(
        "HDFPRE (ml/min) (acceptable range of values 0-150)",
        min_value=0,
        max_value=150,
        value=0,            
        step=1
    )  
    hdfpost = st.number_input(
        "HDFPOST (ml/min) (acceptable range of values 0-150)",
        min_value=0,
        max_value=150,            
        value=0,
        step=1
    )
    qd = st.number_input(
        "Diaysate Flow rate (ml/min)  (acceptable range of values: 300-800)",
        min_value=300,
        max_value=800, 
        value=500,           
        step=1
    )
    t = st.number_input(
        "Session length (min) (acceptable range of values: 60-480)",
        min_value=60,
        max_value=480,  
        value=240,          
        step=1
    )
    ekvt = st.number_input(
        "eKt/V target (acceptable range of values: 0.3-2.0)",
        min_value=0.3,
        max_value=2.0,            
        step=0.1,
        value=1.4,
        format="%.1f"
    )   
                   
   
    extract_button = st.button("Extract data...")
    
    if extract_button:
        with st.spinner("Extracting... it takes time..."):            

            results = calculate_kdn_qbwn(patient_id, vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)            
            
            if isinstance(results, dict):
                st.write("Kdn (mL/min)", round(results["kdn"], 2))
                st.write("Blood flow rate needed to achieve Kdn (Qbn, ml/min)", round(results["qbn"], 2))
            else:
                print(results)  # Print the error message
                                    
            st.success("Success!!")
            
    

#Invoking main function
if __name__ == '__main__':
    main()
