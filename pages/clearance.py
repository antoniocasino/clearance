import streamlit as st
import datetime
from components.kdn_calculator import calculate_kdn_qbwn
from components.pdf_builder import create_pdf

def clearance_page():    
    st.title("Dialyzer clearance and blood flow rate needed to reach the target value of eKt/V") 
    st.markdown("""
        <style>
            [data-testid="stWidgetLabel"] > div {
                height: 40px !important;
                font-size: 20px
            }
            [data-testid="stNumberInputField"] {
                font-size: 24px !important;
                height: 40px !important;
            }
            .font-bigger{
                font-size: 20px
            }
        </style>
        """,
        unsafe_allow_html=True
    )      
        
    patient_id = st.text_input("Patient Identifier", key="id", value="001")
    date = st.date_input(
        "Select a date (dd/mm/yyyy)",
        value=datetime.datetime.now(),
        format="DD/MM/YYYY",
    )
    vdp = st.number_input(
        "Patient's urea volume (L)",
        min_value=20,
        max_value=50,       
        value=35,     
        step=1
    )
    uf = st.number_input(
        "Expected intradialysis weight loss (L)",
        min_value=0.1,
        max_value=5.0,            
        step=0.1,
        value=2.0,
        format="%.1f"
    )  
    
    koavitro = st.number_input(
        "In vitro KOA of the dialyzer (ml/min)",
        min_value=600,
        max_value=2000,            
        step=1,
        value=1200,
    )                       
    hdfpre = st.number_input(
        "HDFPRE (ml/min)",
        min_value=0,
        max_value=150,
        value=0,            
        step=1
    )  
    hdfpost = st.number_input(
        "HDFPOST (ml/min)",
        min_value=0,
        max_value=150,            
        value=0,
        step=1
    )
    qd = st.number_input(
        "Diaysate Flow rate (ml/min)",
        min_value=300,
        max_value=800, 
        value=500,           
        step=1
    )
    t = st.number_input(
        "Session length (min)",
        min_value=60,
        max_value=480,  
        value=240,          
        step=1
    )
    ekvt = st.number_input(
        "eKt/V target",
        min_value=0.3,
        max_value=2.0,            
        step=0.1,
        value=1.4,
        format="%.1f"
    )   
                   
   
    clearnace_button = st.button(key="clearance", label="Calculate")
    
    if clearnace_button:
        with st.spinner("Extracting... it takes time..."):            

            results = calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)            
            
            if isinstance(results, dict):
                st.markdown(f"<span class='font-bigger'>Dialyzer urea clearance needed (ml/min) <strong>{round(results['kdn'], 1)}</strong></span>" , unsafe_allow_html=True)
                st.markdown(f"<span class='font-bigger'>Blood flow rate needed (ml/min) <strong>{round(results['qbn'], 1)}</strong></span>", unsafe_allow_html=True)
                if results["qbn"] > 400:
                    st.error("""Blood flow requirement too high. It is recommended to increase KOA and/or reduce eKt/V""")
                
                pdf = create_pdf({
                    "Patient id":patient_id,"Date":date.strftime("%d/%m/%Y"),"Patient's urea volume (L)":vdp, "Expected intradialysis weight loss (L)":uf, 
                    "In vitro KOA of the dialyzer":koavitro, "HDFPRE (ml/min)":hdfpre, "HDFPOST (ml/min)":hdfpost,
                    "Diaysate Flow rate (ml/min) ":qd, "Session length (min)":t, 
                    "eKt/V target":ekvt,"Dialyzer urea clearance needed (ml/min)":round(results["kdn"], 1),"Blood flow rate needed": round(results["qbn"], 1)
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
                                   