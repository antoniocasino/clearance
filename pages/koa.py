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
        min_value=0.01,
        max_value=1.0,        
        value=0.25,     
        step=0.01,
        format="%.2f"
    )
    qd = st.number_input(
        "qd",
        min_value=0.01,
        max_value=1.0,           
        value=0.50,     
        step=0.01,
        format="%.2f"
    )
    qf = st.number_input(
        "qf",
        min_value=0.01,
        max_value=1.0,       
        value=0.75,     
        step=0.01,
        format="%.2f"
    )
    kd = st.number_input(
        "kd",
        min_value=0.01,
        max_value=1.0,       
        value=0.1,     
        step=0.01,
        format="%.2f"
    )    
    koa_button = st.button(key="koa", label="Calculate")

    if koa_button:
        with st.spinner("Extracting... it takes time..."): 
    
            kdif_result, koa_result = koa(qd,qb,qf,kd)            
            if kdif_result is not None and koa_result is not None:
                st.write(f"Kdif: {round(kdif_result, 2)}")
                st.write(f"KoA: {round(koa_result, 2)}")