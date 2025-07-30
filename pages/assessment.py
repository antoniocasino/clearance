import streamlit as st
import pandas as pd
from components.assessment_calculator import assessment_calculation
from components.pdf_builder import create_pdf

def assessment_page():    
    st.title("stdKt/V & EKRU") 
    st.markdown("""
         <style>
            [data-testid="stWidgetLabel"] > div {
                font-size: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    def PIDI_warning():
        if NHDWK==1 and PIDI!=0:
            return f"The only value allowed for Preceding interdialytic interval is 7"
        elif NHDWK==2 and PIDI!=3 and PIDI !=4:
            return f"Values allowed for Preceding interdialytic interval are 3 and 4"
        elif NHDWK==3 and PIDI!=2 and PIDI!=3:
            return f"Values allowed for Preceding interdialytic interval are 2 and 3"
        else:
            return ""
           
    with st.form("assessment_form"):
        patient_id = st.text_input(
            "Patient Identifier", 
            key="assessment_id",
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
        EKTV = st.number_input(
            "eKt/V",                    
            min_value=0.5,                         
            max_value=2.0,  
            value=None,   
            step=0.1        
        )
        PIDI = st.number_input(
            "Preceding interdialytic interval", 
            min_value=1,
            max_value=7,
            step=1,
            value=None,      
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
                      "Normalised Kru":KRUN,"eKt/V":EKTV,"Preceding interdialytic interval":PIDI,"Weight gain during PIDI":IDWG}
            none_values = [key for key, value in validation_inputs.items() if value is None]  # List of input names with None values
            if none_values or PIDI_warning() !="":
                ol_string = "<ul>\n"  # Start the ordered list                
                ol_string += "".join(f"  <li>{item}</li>\n" for item in none_values)  # Add each item as a list item
                if PIDI_warning() !="":
                    ol_string += f"  <li>{PIDI_warning()}</li>\n"
                ol_string += "</ul>\n"  
                st.markdown(f"<div style='background-color:lightgoldenrodyellow; color:#926c05;'>The following fields are missing: {ol_string}</div>",unsafe_allow_html=True)                  
            else:                
                results = assessment_calculation({"nhdwk":NHDWK,"krun":KRUN,"ektv":EKTV,"pidi":PIDI,"idwg":IDWG})

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
                        '#': [1,2,3,4,5],              
                        'Output': ["Weekly net Ultrafiltration","stdKt/V  (v/wk) ","EKRUN","EKRUN variable target=12-KRUN","EKRUN_min_adequate"],
                        'Symbols':["UFwk","stdKt/V","EKRUN","EKRUN_VTM","EKRUN_min"],
                        'Units': ["","","ml/min per 35 l V","ml/min per 35 l V","ml/min per 35 l V"],
                        'Result': [results['ufwk'],results['stdktv'],results['ekrun'],results['12_minus_krun'],results['10_minus_1.5_krun']]
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
                        "eKt/V":EKTV,
                        "Preceding inter-dialytic interval":PIDI, 
                        "Weight gain during PIDI":IDWG},
                        output_data={"Patient Identifier":patient_id,
                                    "Weekly net Ultrafiltration":results['ufwk'],
                                    "stdKt/V  (v/wk) ":results['stdktv'],
                                    "EKRUN":results['ekrun'],
                                    "EKRUN variable target=12-KRUN":results['12_minus_krun'],
                                    "EKRUN_min_adequate":results['10_minus_1.5_krun']                                    
                                    },
                        pageBreak=True
                    )
                    # Provide download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name=f"{patient_id}-assessment.pdf",
                        mime="application/pdf"
                    )                    
                else:
                    st.write(results) 