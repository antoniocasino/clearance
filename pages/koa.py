import streamlit as st
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
                height: 50px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )   
    
    qb = st.number_input(
        "Blood flow rate (ml/min)",           
        value=300,
        min_value=100,
        max_value=450,
        step=1        
    )
    qd = st.number_input(
        "Dialysate flow rate (ml/min)",              
        value=500,    
        max_value=500,    
        step=1        
    )
    qf = st.number_input(
        "Ultrafiltration rate (ml/min)",        
        value=10,
        max_value=10,     
        step=1        
    )
    kd = st.number_input(
        "Dialyzer Urea clearance (ml/min)",            
        value=250,
        max_value=250,
        step=1        
    )

    koa_button = st.button(key="koa", label="Calculate")

    if koa_button:
        with st.spinner("Extracting... it takes time..."): 
    
            kdif_result, koa_result = koa(qb=qb,qd=qd,qf=qf,kd=kd)
            if kdif_result is not None and koa_result is not None:
                st.markdown(f"<span class='font-bigger'>Diffusive Kd  (ml/min) <strong>{round(kdif_result, 1)}</strong></span>" , unsafe_allow_html=True)
                st.markdown(f"<span class='font-bigger'>KoA of the dialyzer in vitro  (ml/min) <strong>{round(koa_result, 1)}</strong></span>" , unsafe_allow_html=True)
                