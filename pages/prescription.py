import streamlit as st
import pandas as pd
from components.prescription_calculator import prescription_calculation
from components.pdf_builder import create_pdf

def prescription_page():    
    st.title("eKt/V") 
    st.markdown("""
         <style>
            [data-testid="stWidgetLabel"] > div {
                font-size: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    def PIDI_min():
        if NHDWK ==1:
            return 7
        elif NHDWK ==2:
            return 3
        elif NHDWK ==3:
            return 2    
    def PIDI_max():
        if NHDWK ==1:
            return 7
        elif NHDWK ==2:
            return 4
        elif NHDWK ==3:
            return 3  
           
    with st.form("prescription_form"):
        patient_id = st.text_input(
            "Patient Identifier", 
            key="prescription_id",
            value=None,)
        NHDWK = st.number_input(
            "Number of HD per week",                       
            min_value=1,
            max_value=3,
            value=None,
            step=1        
        )
        KRUN = st.number_input(
            "Normalised Kru", 
            min_value=0,                         
            max_value=7,  
            value=None,  
            step=1
        )       
        PIDI = st.number_input(
            "Preceding interdialytic interval", 
            min_value=PIDI_min(),
            max_value=PIDI_max(),
            step=1,
            value=PIDI_min(),      
        )
        IDWG = st.number_input(
            "Weight gain during PIDI",                    
            min_value=0,                         
            max_value=5,  
            value=None,   
            step=1        
        )
        col1, col2 = st.columns([1,1]) # to arrange buttons horizontally
        with col1:
            submit = st.form_submit_button("Submit")
        with col2:
            reset = st.form_submit_button("Reset", on_click=lambda: st.session_state.clear()) 
          
    if submit:
        with st.spinner("Extracting... it takes time..."): 
            validation_inputs = {"Patient Identifier":patient_id,"Number of HD per week":NHDWK,
                      "Normalised Kru":KRUN,"Preceding interdialytic interval":PIDI,"Weight gain during PIDI":IDWG}
            none_values = [key for key, value in validation_inputs.items() if value is None]  # List of input names with None values
            if none_values:
                ol_string = "<ul>\n"  # Start the ordered list                
                ol_string += "".join(f"  <li>{item}</li>\n" for item in none_values)  # Add each item as a list item
                ol_string += "</ul>\n"  
                st.markdown(f"<div style='background-color:lightgoldenrodyellow; color:#926c05;'>The following fields are missing: {ol_string}</div>",unsafe_allow_html=True)                  
            else:                
                results = prescription_calculation({"nhdwk":NHDWK,"krun":KRUN,"pidi":PIDI,"idwg":IDWG})

                if isinstance(results, dict):
                    st.header("Output Data")

                    for key,value in results.items():
                        if isinstance(value, float):
                            results[key]=round(value,2)
                        else:                         
                            results[key] = value

                    def format_float(val):
                        if isinstance(val, float):
                            return f"{val:.2f}"  # Format to 2 decimal place
                        return val              

                    output_data = {        
                        '#': [1,2,3],              
                        'Output': ["Weekly net Ultrafiltration","eKtV to get EKRUN = 12 - KRUN","eKtV to get stdKt/V = 2.3"],
                        'Symbols':["UFwk","stdKt/V","stdKt/V"],
                        'Units': ["l","dimensionless","dimensionless"],
                        'Result': [results['ufwk'],results['ektv_ekru'],results['ektv_stdktv']]
                    }

                    df_output = pd.DataFrame(output_data)                
                    st.dataframe(df_output.style.format(format_float), 
                                column_config={"Output": st.column_config.Column(width="large")},
                                hide_index=True) # Set the table width to 100%                
                
                    pdf = create_pdf(
                        input_data ={
                        "Patient Identifier":patient_id,
                        "Number of HD per week":NHDWK,
                        "Normalised Kru":KRUN,                        
                        "Preceding inter-dialytic interval":PIDI, 
                        "Weight gain during PIDI":IDWG},
                        output_data={"Patient Identifier":patient_id,
                                    "Weekly net Ultrafiltration":results['ufwk'],
                                    "eKtV to get EKRUN = 12 - KRUN":results['ektv_ekru'],
                                    "eKtV to get stdKt/V = 2.3":results['ektv_stdktv']                                    
                                    },
                        pageBreak=True
                    )
                    # Provide download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name=f"{patient_id}-prescription.pdf",
                        mime="application/pdf"
                    )                    
                else:
                    st.write(results) 