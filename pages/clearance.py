import streamlit as st
import datetime
import pandas as pd
from components.kdn_calculator import calculate_kdn_qbwn
from components.pdf_builder import create_pdf


def clearance_page():
    # Load the data from the CSV file
    # This will load the data only once, improving performance
    if "df_dialyzers" not in st.session_state:
        df = pd.read_csv('Table_of_Dialyzers.csv', delimiter=';')
        df['KoA'] = pd.to_numeric(df['KoA'], errors='coerce')
        df.dropna(subset=['KoA'], inplace=True)
        st.session_state.df_dialyzers = df

    st.title("Dialyzer clearance and blood flow rate needed to reach the target value of eKt/V") 
    st.markdown("""
        <style>
            [data-testid="stWidgetLabel"] > div {
                height: 40px !important;
                font-size: 16px
            }
            [data-testid="stNumberInputField"] {
                font-size: 20px !important;
                height: 40px !important;
            }
            .font-bigger{
                font-size: 20px
            }
            .stButton > button {
                font-size: 16px;                
                color: black;
                margin: 0 auto;
                height: 2rem;
                width: 12rem;
            }               
            </style>
                """,
                unsafe_allow_html=True
            )      
    def clear_inputs():
        """Iterates over the predefined list of keys and clears the corresponding session state values."""
        for key in INPUT_KEYS:
            if key in st.session_state:
                st.session_state[key] = None
                   
    patient_id = st.text_input("Patient Identifier",
                                key="id",
                                value=None,)
    date = st.date_input(
        "Select a date (dd/mm/yyyy)",            
        format="DD/MM/YYYY",
        value=None,
        key="cle_date"
    )
    vdp = st.number_input(
        "Patient's urea volume (L)",
        min_value=20,
        max_value=50,
        value=None,
        key="vdp",
        step=1
    )
    uf = st.number_input(
        "Expected intradialysis weight loss (L)",
        min_value=0.1,
        max_value=5.0,
        value=None,
        step=0.1,  
        key="uf",          
        format="%.1f"
    )  
    
    # NOTE: Place combo boxes inside st.expander for a group/legend
    with st.expander("Dialyzer Urea KoA in vitro"):
        manufacturers = st.session_state.df_dialyzers['Manufacturer'].unique()
        selected_manufacturer = st.selectbox(
            "Manufacturer",
            manufacturers,
            key='manufacturer_select.clearance'
        )
        
        models = st.session_state.df_dialyzers[st.session_state.df_dialyzers['Manufacturer'] == selected_manufacturer]['Model'].unique()
        selected_model = st.selectbox(
            "Model",
            models,
            key='model_select.clearance',
            index=None
        )

        selected_koa = None
        koavitro = None
        if selected_model:
            # NOTE: Added int() cast here
            selected_koa = int(st.session_state.df_dialyzers[
                (st.session_state.df_dialyzers['Manufacturer'] == selected_manufacturer) &
                (st.session_state.df_dialyzers['Model'] == selected_model)
            ]['KoA'].iloc[0]) 

            koavitro = st.number_input(
                "In vitro KOA of the dialyzer (ml/min)",
                min_value=500,
                max_value=2400,
                value=selected_koa,
                key="koavitro", 
                step=1
            )        

    hdfpre = st.number_input(
        "HDFPRE (ml/min)",
        min_value=0,
        max_value=150,
        value=None,
        key="hdfpre", 
        step=1
    )  
    hdfpost = st.number_input(
        "HDFPOST (ml/min)",
        min_value=0,
        max_value=150,
        value=None,
        key="hdfpost",
        step=1
    )
    qd = st.number_input(
        "Diaysate Flow rate (ml/min)",
        min_value=301,
        max_value=800, 
        value=None,
        key="qd",
        step=1
    )
    t = st.number_input(
        "Session length (min)",
        min_value=60,
        max_value=480,
        value=None,
        key="session_time",
        step=1
    )
    ekvt = st.number_input(
        "eKt/V target",
        min_value=0.3,
        max_value=2.0,
        value=None,
        step=0.1,
        key="ekvt",            
        format="%.1f"
    )   
    
    col1, col2 = st.columns([1,1]) # to arrange buttons horizontally
    with col1:
        submit = st.button("Submit", key="clearance_submit")
    with col2:
        reset = st.button("Reset", on_click=clear_inputs, key="clearance_reset")  
   
        #clearnace_button = st.button(key="clearance", label="Calculate")
    INPUT_KEYS = [
        "id", "cle_date", "vdp", "uf", "manufacturer_select.clearance", "model_select.clearance",
        "koavitro", "hdfpre", "hdfpost", "qd", "session_time", "ekvt"
    ]

    if submit:
        with st.spinner("Extracting... it takes time..."):            
            validation_inputs = {
                    "Patient id":patient_id,"Date":date,"Patient's urea volume (L)":vdp, "Expected intradialysis weight loss (L)":uf, 
                    "In vitro KOA of the dialyzer":koavitro, "HDFPRE (ml/min)":hdfpre, "HDFPOST (ml/min)":hdfpost,
                    "Diaysate Flow rate (ml/min) ":qd, "Session length (min)":t, 
                    "eKt/V target":ekvt}
            
            none_values = [key for key, value in validation_inputs.items() if value is None]  # List of input names with None values
            if none_values:                
                ol_string = "<ul>\n"  # Start the ordered list                
                ol_string += "".join(f"  <li>{item}</li>\n" for item in none_values)  # Add each item as a list item
                ol_string += "</ul>\n"             
                st.markdown(f"<div style='background-color:lightgoldenrodyellow; color:#926c05;'>The following fields are missing: {ol_string}</div>",unsafe_allow_html=True)                  
            else:
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
                                        