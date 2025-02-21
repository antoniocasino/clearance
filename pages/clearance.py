import streamlit as st
import datetime
import pandas as pd
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
            .stFormSubmitButton > button {
                font-size: 20px;                
                color: black;
                margin: 0 auto;
                height: 2rem;
                width: 10rem;
            }    
            </style>
                """,
                unsafe_allow_html=True
            )      

    with st.form("clearance_form"):
        
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
            step=1
        )
        uf = st.number_input(
            "Expected intradialysis weight loss (L)",
            min_value=0.1,
            max_value=5.0,            
            step=0.1,            
            format="%.1f"
        )  
        
        koavitro = st.number_input(
            "In vitro KOA of the dialyzer (ml/min)",
            min_value=600,
            max_value=2000,            
            step=1,            
        )                       
        hdfpre = st.number_input(
            "HDFPRE (ml/min)",
            min_value=0,
            max_value=150,            
            step=1
        )  
        hdfpost = st.number_input(
            "HDFPOST (ml/min)",
            min_value=0,
            max_value=150,                        
            step=1
        )
        qd = st.number_input(
            "Diaysate Flow rate (ml/min)",
            min_value=301,
            max_value=800,                  
            step=1
        )
        t = st.number_input(
            "Session length (min)",
            min_value=60,
            max_value=480,              
            step=1
        )
        ekvt = st.number_input(
            "eKt/V target",
            min_value=0.3,
            max_value=2.0,            
            step=0.1,            
            format="%.1f"
        )   
    
        col1, col2 = st.columns([1,1]) # to arrange buttons horizontally
        with col1:
            submit = st.form_submit_button("Submit")
        with col2:
            reset = st.form_submit_button("Reset", on_click=lambda: st.session_state.clear()) 
   
        #clearnace_button = st.button(key="clearance", label="Calculate")
        
    if submit:
        with st.spinner("Extracting... it takes time..."):            

            results = calculate_kdn_qbwn(vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt)            
            
            if isinstance(results, dict):
                
                for key,value in results.items():
                    if isinstance(value, float):
                        results[key]=round(value,2) 

                input_data = {
                    '#': [1, 2],
                    'Output': ["Dialyzer urea clearance needed","Blood flow rate needed "],                    
                    'Units': ["ml/min","ml/min"],                    
                    'Result': [round(results['kdn'], 1),round(results['qbn'], 1)]
                }
                df_input = pd.DataFrame(input_data)                
                st.dataframe(df_input,hide_index=True)       

                if results["qbn"] > 400:
                    st.error("""Blood flow requirement too high. It is recommended to increase KOA and/or reduce eKt/V""")
                
                pdf = create_pdf(
                    input_data={
                    "Patient id":patient_id,"Date":date.strftime("%d/%m/%Y"),"Patient's urea volume (L)":vdp, "Expected intradialysis weight loss (L)":uf, 
                    "In vitro KOA of the dialyzer":koavitro, "HDFPRE (ml/min)":hdfpre, "HDFPOST (ml/min)":hdfpost,
                    "Diaysate Flow rate (ml/min) ":qd, "Session length (min)":t, 
                    "eKt/V target":ekvt},
                    output_data={"Patient id":patient_id,"Dialyzer urea clearance needed (ml/min)":round(results["kdn"], 1),"Blood flow rate needed": round(results["qbn"], 1)}
                )

                # Provide download button
                st.download_button(
                    label="Download PDF",
                    data=pdf,
                    file_name=f"{patient_id}_{date}_clearance_data.pdf",
                    mime="application/pdf"
                )
            else:
                st.write(results)  # Print the error message
                                    