import streamlit as st
from components.koa_calculator import koa
def koa_page():    
    st.title("Dialyzer's characteristics (KoA)") 
    st.markdown("""
         <style>
        [data-testid="stWidgetLabel"] > div {
            font-size: large;
        }
        </style>
        """,
        unsafe_allow_html=True
    )   
    
    qb = st.number_input(
        "qb",           
        value=300,     
        step=1        
    )
    qd = st.number_input(
        "qd",              
        value=500,     
        step=1        
    )
    qf = st.number_input(
        "qf",        
        value=10,     
        step=1        
    )
    kd = st.number_input(
        "kd",            
        value=250,     
        step=1        
    )    
    koa_button = st.button(key="koa", label="Calculate")

    if koa_button:
        with st.spinner("Extracting... it takes time..."): 
    
            kdif_result, koa_result = koa(qb=qb,qd=qd,qf=qf,kd=kd)
            if kdif_result is not None and koa_result is not None:
                st.write(f"Kdif: {round(kdif_result, 1)}")
                st.write(f"KoA: {round(koa_result, 1)}")