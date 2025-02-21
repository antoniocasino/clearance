import streamlit as st
import pandas as pd
from components.koa_calculator import koa
def koa_page():    
    st.title("Dialyzer's characteristics (KoA)") 
    st.markdown("""
         <style>
            [data-testid="stWidgetLabel"] > div {
                font-size: 20px;
            }            
            [data-baseweb="base-input"] > input{
                font-size: 24px !important;
                height: 40px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )   
    with st.form("koa_form"):
        qb = st.number_input(
            "Blood flow rate (ml/min)",                       
            min_value=100,
            max_value=300,
            step=1        
        )
        qd = st.number_input(
            "Dialysate flow rate (ml/min)", 
            min_value=100,                         
            max_value=1000,    
            step=1        
        )
        qf = st.number_input(
            "Ultrafiltration rate (ml/min)",                    
            min_value=0,                         
            max_value=30,     
            step=1        
        )
        kd = st.number_input(
            "Dialyzer Urea clearance (ml/min)",            
            value=250,
            min_value=100,
            max_value=350,
            step=1        
        )
        col1, col2 = st.columns([1,1]) # to arrange buttons horizontally
        with col1:
            submit = st.form_submit_button("Submit")
        with col2:
            reset = st.form_submit_button("Reset", on_click=lambda: st.session_state.clear()) 
   
    #koa_button = st.button(key="koa", label="Calculate")

    if submit:
        with st.spinner("Extracting... it takes time..."): 
    
            kdif_result, koa_result = koa(qb=qb,qd=qd,qf=qf,kd=kd)           

            if kdif_result is not None and koa_result is not None:
                input_data = {
                    '#': [1, 2],
                    'Output': ["Diffusive Kd","KoA of the dialyzer in vitro"],                    
                    'Units': ["ml/min","ml/min"],                    
                    'Result': [round(kdif_result, 1),round(koa_result, 1)]
                }
                df_input = pd.DataFrame(input_data)                
                st.dataframe(df_input,hide_index=True)                 
