import streamlit as st
import datetime
from components.adequacy import ihd_calculation
from components.pdf_builder import create_pdf
import pandas as pd

def adequacy_page():    
    st.title("Prescription of incremental HD based on urea kinetics") 
    st.markdown("""
        <style>
            [data-testid="stWidgetLabel"] > div {
                height: 40px !important;
                font-size: 16px;
            }
            [data-testid="stNumberInputField"] {
                font-size: 24px !important;
                height: 40px !important;
            }
            .font-bigger{
                font-size: 20px;
            }
            .stFormSubmitButton > button {
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
    def PIDI_warning():
        if NHDWK==1 and PIDI!=7:
            return f"The only value allowed for Preceding interdialytic interval is 7"
        elif NHDWK==2 and PIDI!=3 and PIDI !=4:
            return f"Values allowed for Preceding interdialytic interval are 3 and 4"
        elif NHDWK==3 and PIDI!=2 and PIDI!=3:
            return f"Values allowed for Preceding interdialytic interval are 2 and 3"
        else:
            return ""

    def CT_warning():
        if CT and C0 and CT<=C0:
            return f"Pre-dialysis Blood or Serum Urea Nitrogen must be less than Post-dialysis"
        else:
            return ""   
                
    def KRU_max():
        if UO and UUN and UO >0 and UUN >0:
            return 999
        else:
            return 7
        
    def KRU_min():
        if UO and UUN and UO >0 and UUN >0:
            return 999
        else:
            return 0  
          
    def KRU_value():
        if UO and UUN and UO >0 and UUN >0:
            return 999 
        else:
            return None              
                
    with st.form("adequacye_form"):
        patient_id = st.text_input(
            "Patient Identifier", 
            key="ihd_id",
            value=None,)
        date = st.date_input(
            "Lab Date (dd/mm/yy)",
            value=None,
            format="DD/MM/YYYY",
        )
        NHDWK = st.number_input(
            "Number of HD  sessions per week (1, 2, or 3)",
            min_value=1,
            max_value=3,
            value=None,
            step=1
        )   

        PIDI = st.number_input(
            "Preceding inter-dialytic interval (days: 2, 3, 4, or 7)",
            min_value=1,
            max_value=7,
            step=1,
            value=None,
        )  
        
        BW0 = st.number_input(
            "Pre-dialysis Body Weight (kg)",
            min_value=20,
            max_value=140,
            value=None,
            step=1,        
        )                       
        BWT = st.number_input(
            "Post-dialysis Body weight (kg)",
            min_value=20,
            max_value=140, 
            value=None,
            step=1
        )
        T = st.number_input(
            "Session length (min)",
            key="idh_time",
            min_value=60,
            max_value=480,
            value=None,
            step=1
        )  
        QB = st.number_input(
            "Blood Flow Rate (ml/min)",
            min_value=100,
            max_value=400,
            value=None,
            step=1
        )
        HDFPRE = st.number_input(
            "Pre-dilution infusion rate (ml/min)",
            min_value=0,
            max_value=250,
            value=None,
            step=1
        )
    
        HDFPOST = st.number_input(
            "Post-dilution infusion rate (ml/min)",
            min_value=0,
            max_value=150,
            value=None,
            step=1,        
        )   
        QD = st.number_input(
            "Dialysate flow rate (ml/min)",
            min_value=300,
            max_value=800,
            value=None,
            step=1
        )
        KOAvitro = st.number_input(
            "Dialyzer Urea KoA in vitro (ml/min)",
            min_value=600,
            max_value=2000,
            value=None,
            step=1
        )   
        C0 = st.number_input(
            "Pre-dialysis Blood or Serum Urea Nitrogen (mg/dl)",
            min_value=20.0,
            max_value=200.0,
            value=None,
            step=0.1,        
        )
        # Update session state for C0
        CT = st.number_input(
            "Post-dialysis Blood or Serum Urea Nitrogen (mg/dl)",
            min_value=5.0,
            max_value=199.0,
            value=None,
            step=0.1
        )  
        
        UO = st.number_input(
            "Urinary Output ( ml/24 h)",
            min_value=0,
            max_value=4000,  
            value=None,   
            step=1
        )   
        UUN = st.number_input(
            "Urinary Urea Nitrogen (UUN, mg/dl)",
            min_value=0.0,
            max_value=1000.0,
            value=None,
            step=0.1,         
        ) 
        KRUw = st.number_input(
            "Renal urea clearance (ml/min)",
            min_value=KRU_min(),
            max_value=KRU_max(),            
            value=KRU_value(),
            step=1
        )
        col1, col2 = st.columns([1,1]) # to arrange buttons horizontally
        with col1:
            submit = st.form_submit_button("Submit")
        with col2:
            reset = st.form_submit_button("Reset", on_click=lambda: st.session_state.clear())  

    
    #ihd_button = st.button(key="ihd", label="Calculate")
    
    if submit:
        with st.spinner("Extracting... it takes time..."):
            validation_inputs = {"Patient Identifier":patient_id,"Lab Date":date, "Number of Hemodialysis sessions per week":NHDWK,
                                  "Preceding inter-dialytic interval":PIDI, 
                                     "Pre-dialysis Body Weight":BW0,
                                     "Post-dialysis Body weight":BWT,
                                     "Session length":T,"Blood Flow Rate":QB,
                                     "Pre-dilution infusion rate":HDFPRE,
                                     "Post-dilution infusion rate":HDFPOST,
                                     "Dialysate flow rate":QD,
                                     "Dialyzer Urea KoA in vitro":KOAvitro,
                                     "Pre-dialysis Blood or Serum Urea Nitrogen":C0,
                                     "Post-dialysis Blood or Serum Urea Nitrogen":CT,
                                     "KRUw":KRUw, "Urinary Output":UO,"Urinary Urea Nitrogen":UUN}
            none_values = [key for key, value in validation_inputs.items() if value is None]  # List of input names with None values
            
            if none_values or PIDI_warning() !="" or CT_warning() !="":
                ol_string = "<ul>\n"  # Start the ordered list                
                ol_string += "".join(f"  <li>{item}</li>\n" for item in none_values)  # Add each item as a list item
                if PIDI_warning() !="":
                    ol_string += f"  <li>{PIDI_warning()}</li>\n"
                if CT_warning() !="":
                    ol_string += f"  <li>{CT_warning()}</li>\n"
                ol_string += "</ul>\n"                    
                st.markdown(f"<div style='background-color:lightgoldenrodyellow; color:#926c05;'>The following fields are missing: {ol_string}</div>",unsafe_allow_html=True)
            else:
                inputs = {"PTID":patient_id,"LABDATE":date, "NHDWK":NHDWK, "PIDI":PIDI, 
                                     "BW0":BW0,"BWT":BWT,"T":T,"QB":QB,"HDFPRE":HDFPRE,
                                     "HDFPOST":HDFPOST, "QD":QD,"KOAvitro":KOAvitro,
                                     "C0":C0,"CT":CT,"KRUw":KRUw, "UO":UO,"UUN":UUN} 
                results = ihd_calculation(inputs)                              
                
                if isinstance(results, dict):
                    st.header("Output Data")

                    for key,value in results.items():
                        if isinstance(value, float):
                            results[key]=round(value,2) 
                        elif isinstance(value,datetime.datetime):
                            results[key] = value.strftime("%d/%m/%Y") 
                        else:                         
                            results[key] = value

                    def format_float(val):
                        if isinstance(val, float):
                            return f"{val:.2f}"  # Format to 2 decimal place
                        return val

                    output_data = {
                        '#': [
                              1,2,3,
                              4,5,6,
                              7,8,9,
                              10,11,12,
                              13,14,15,
                              16,17,18
                              ],
                        'Output': [
                                   "Total Dialyzer Urea Clearance",
                                   "Single pool Kt/V",
                                   "Equilibrated Kt/V",
                                   "Urea distribution volume (double pool)",
                                   "Protein catabolic rate (g/kg/day)",
                                   "Renal urea clearance (calculated)",
                                   "KRU normalized per V 35 l",
                                   "Equivalent Renal Clearance per V 35 l ",
                                   "EKRUN_variable target (10-1.5 KRUN)*",
                                   "EKR35 ≥10 – 1.5 KRUN *",
                                   "Standard Kt/V",
                                   "StdKt/V ≥ 2.1",
                                   "Ultrafiltration rate",
                                   "UFR ≤ 13 ml/h/kg",
                                   "TD needed for UFR=13 ml/h/kg",
                                   "Weekly net Ultrafiltration",
                                   "eKt/V to get EKRUN=12-KRUN",
                                   "eKt/V to be prescribed to get stdKt/V=2.3"
                                   ], 
                        'Symbols':["Kd Tot","spKt/V","eKt/V",
                                   "Vdp","PCRn","KRU",
                                   "KRUN","EKR35","EKRU_VTM",
                                   "Adequacy","StdKt/V","Adequacy",
                                   "UFR","Adequacy","TDN",
                                   "UFwk","eKt/V","eKt/V"],
                        'Units': [
                                "ml/min","dimensionless","dimensionless",
                                "l","(g/kg/day)","ml/min",
                                "ml/min per 35l V","ml/min per 35l V","ml/min per 35l V",
                                "Yes/No","Volume/wk","Yes/No",
                                "ml/h per kg","Yes/No","min per session",
                                "dimensionless","dimensionless","(l)"
                                ],                    
                        'Result': [
                                results['KTOT'],results['SPKTV'],results['EKTV'],                                   
                                results['VDP'],results["PCRN"],results['Kru'],
                                results['krun'],results['ekrun'],results['ekrun_min'],
                                results['AdeqEKR'],results['STDKTV'],results['AdeqStdKTV'],
                                results['UFR'],results['AdeqUFR'],results['TDN'],
                                results["Ufwk"],results["Ektv_ekru"],results['Ektv_stdktv']
                                ]                                 
                    }                   
                    df_output = pd.DataFrame(output_data)                
                    st.dataframe(df_output.style.format(format_float), 
                                column_config={"Output": st.column_config.Column(width="large")},
                                hide_index=True) # Set the table width to 100%                
                                                                                                            

                    pdf = create_pdf(
                        input_data ={
                        "Patient Identifier":patient_id,"Lab Date":date.strftime("%d/%m/%Y"), "Number of Hemodialysis sessions per week":NHDWK, "Preceding inter-dialytic interval":PIDI, 
                        "Pre-dialysis Body Weight (kg)":BW0,"Post-dialysis Body weight (kg)":BWT,"Session length (min)":T,"Blood Flow Rate (ml/min)":QB,
                        "Pre-dilution infusion rate (ml/min)":HDFPRE,
                        "Post-dilution infusion rate (ml/min)":HDFPOST, "Dialysate flow rate ":QD,
                        "Dialyzer urea KoA in vitro ":KOAvitro,
                        "Pre-dialysis Blood or Serum Urea Nitrogen":C0,"Post-dialysis Blood or Serum Urea Nitrogen":CT,"Renal urea clearance (999 if urine)":KRUw,
                        "Urinary Output ":UO,"Urinary Urea Nitrogen":UUN},
                        output_data={"Patient Identifier":patient_id,
                                    "Total Dialyzer Urea Clearance ":results['KTOT'],
                                    "Single pool Kt/V ":results['SPKTV'],
                                    "Equilibrated Kt/V ":results['EKTV'],
                                    "Urea distribution volume (double pool)":results['VDP'],
                                    "Protein catabolic rate (g/kg/day)":results["PCRN"],
                                    "Renal urea clearance (calculated)":results['Kru'],
                                    "KRU normalized per V 35 l":results['krun'],
                                    "Equivalent Renal Clearance per V 35 l ":results['ekrun'],
                                    "EKRUN_variable target_ min = 10-1.5 KRUN":results['ekrun_min'],                                  
                                    "EKR35 ≥10 – 1.5 KRUN *":results['AdeqEKR'],
                                    "Standard Kt/V":results['STDKTV'],
                                    "StdKt/V ≥ 2.1":results['AdeqStdKTV'],
                                    "Ultrafiltration rate ":results['UFR'],
                                    "UFR ≤ 13 ml/h/kg":results['AdeqUFR'],
                                    "TD needed for UFR=13 ml/h/kg":results['TDN'],
                                    "Weekly net Ultrafiltration":results['Ufwk'],
                                    "eKt/V to get EKRUN=12-KRUN ":results['Ektv_ekru'],
                                    "eKt/V to be prescribed to get stdKt/V=2.3":results['Ektv_stdktv'],
                                    },
                        pageBreak=True
                    )
                   
                    # Provide download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name=f"{patient_id}_{date}-adequacy.pdf",
                        mime="application/pdf"
                    )                    
                else:
                    st.write(results)  # Print the error message
                                    