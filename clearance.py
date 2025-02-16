import streamlit as st
import time
import datetime
from utils import calculate_kdn_qbwn
from pdf_builder import create_pdf

def clearance_page():    
    st.title("Dialyzer clearance and blood flow rate needed to reach the target value of eKt/V") 
          
    
    
    patient_id = st.text_input("Patient Identifier", key="id", value="001")
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
        format="%.1f"
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
                   
   
    extract_button = st.button("Calculate Kdn")
    
    if extract_button:
        with st.spinner("Extracting... it takes time..."):            

            results = calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)            
            
            if isinstance(results, dict):
                st.write("Kdn (mL/min)", round(results["kdn"], 1))
                st.write("Blood flow rate needed (ml/min)", round(results["qbn"], 1))
                if results["qbn"] > 400:
                    st.warning("""Blood flow requirement too high. It is recommended to increase KOA and/or reduce eKt/V""")
                
                pdf = create_pdf({
                    "Patient id":patient_id,"Date":date.strftime("%d/%m/%Y"),"Patient's urea volume (L)":vdp, "Expected intradialysis weight loss (L)":uf, 
                    "In vitro KOA of the dialyzer":koavitro, "HDFPRE (ml/min)":hdfpre, "HDFPOST (ml/min)":hdfpost,
                    "Diaysate Flow rate (ml/min) ":qd, "Session length (min)":t, 
                    "EKt/V target":ekvt,"Kdn (mL/min)":round(results["kdn"], 1),"Blood flow rate needed": round(results["qbn"], 1)
                })

                # Provide download button
                st.download_button(
                    label="Download PDF",
                    data=pdf,
                    file_name=f"{patient_id}_{date}_clearance_data.pdf",
                    mime="application/pdf"
                )
            else:
                st.write(results)  # Print the error message
                                   