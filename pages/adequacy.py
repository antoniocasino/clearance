import streamlit as st
import datetime
from components.ihd_calculator import calculate_ihd
from components.pdf_builder import create_pdf
import pandas as pd

def adequacy_page():    
    st.title("Prescription of incremental HD based on urea kinetics") 
    st.markdown("""
        <style>
            [data-testid="stWidgetLabel"] > div {
                height: 40px !important;
                font-size: 20px;
            }
            [data-testid="stNumberInputField"] {
                font-size: 24px !important;
                height: 40px !important;
            }
            .font-bigger{
                font-size: 20px;
            }           
        </style>
        """,
        unsafe_allow_html=True
    )   
           
    def PIDI_value():
        if NHDWK ==1:
            return 7       
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
            
    def KRU_max():
        if UO >0 and UUN >0:
            return 999
        else:
            return 7
        
    def KRU_min():
        if UO >0 and UUN >0:
            return 999
        else:
            return 0  
          
    def KRU_value():
        if UO >0 and UUN >0:
            return 999 
        else:
            return 0              
                

    patient_id = st.text_input("Patient Identifier", key="ihd_id", value="001")
    date = st.date_input(
        "Lab Date (dd/mm/yy)",
        value=datetime.datetime.now(),
        format="DD/MM/YYYY",
    )
    NHDWK = st.number_input(
        "Number of Hemodialysis sessions per week",
        min_value=1,
        max_value=3,               
        step=1
    )   

    PIDI = st.number_input(
        "Preceding inter-dialytic interval",
        min_value=PIDI_min(),
        max_value=PIDI_max(),
        step=1,
        value=PIDI_value()        
    )  
    
    BW0 = st.number_input(
        "Pre-dialysis Body Weight (kg)",
        min_value=20,
        max_value=140,            
        step=1,        
    )                       
    BWT = st.number_input(
        "Post-dialysis Body weight (kg)",
        min_value=20,
        max_value=140,             
        step=1
    )
    T = st.number_input(
        "Session length (min)",
        key="idh_time",
        min_value=60,
        max_value=480,          
        step=1
    )  
    QB = st.number_input(
        "Blood Flow Rate (ml/min)",
        min_value=100,
        max_value=400,                    
        step=1
    )
    HDFPRE = st.number_input(
        "Pre-dilution infusion rate (ml/min)",
        min_value=0,
        max_value=250,     
        step=1
    )
   
    HDFPOST = st.number_input(
        "Post-dilution infusion rate (ml/min)",
        min_value=0,
        max_value=150,            
        step=1,        
    )   
    QD = st.number_input(
        "Dialysate flow rate (ml/min)",
        min_value=300,
        max_value=800,            
        step=1
    )
    KOAvitro = st.number_input(
        "Dialyzer Urea KoA in vitro (KoA_vitro, ml/min)",
        min_value=600,
        max_value=2000,         
        step=1
    )   
    C0 = st.number_input(
        "Pre-dialysis Serum Urea Nitrogen (C0, mg/dl)",
        min_value=20,
        max_value=200,            
        step=1,        
    )
    CT = st.number_input(
        "Post-dialysis Serum Urea Nitrogen (CT, mg/dl)",
        min_value=5,
        max_value=150,            
        step=1
    )  
       
    UO = st.number_input(
        "Urinary Output (UO, ml/24 h)",
        min_value=0,
        max_value=4000,  
        value=0,      
        step=1
    )   
    UUN = st.number_input(
        "Urinary Urea Nitrogen (UUN, mg/dl)",
        min_value=0,
        max_value=1000,
        value=0,
        step=1,         
    ) 
    KRUw = st.number_input(
        "Renal urea clearance in serum water conc. (KRU, ml/min : 0-7, 999 if urine)",
        min_value=KRU_min(),
        max_value=KRU_max(),            
        value=KRU_value(),
        step=1
    )
   

    
    ihd_button = st.button(key="ihd", label="Calculate")
    
    if ihd_button:
        with st.spinner("Extracting... it takes time..."):            
            results = calculate_ihd({"PTID":patient_id,"LABDATE":date, "NHDWK":NHDWK, "PIDI":PIDI, 
                                     "BW0":BW0,"BWT":BWT,"T":T,"QB":QB,"HDFPRE":HDFPRE,
                                     "HDFPOST":HDFPOST, "QD":QD,"KOAvitro":KOAvitro,
                                     "C0":C0,"CT":CT,"KRUw":KRUw, "UO":UO,"UUN":UUN})                              
            
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
                    '#': [1,2,3,4,5,6,7,8,9,10,11,12,13,14],
                    'Output': ["Kd tot","spKt/V","eKt/V",
                               "Vdp (L)","Kru","KR35",
                               "EKR35","Adequacy based EKR35 ≥ minimum variable target (10 -1.5 KR35)","StdKt/V",
                               "Adequacy based on StdKt/V≥2.1 v/wk ","Hourly Ultrafiltration rate per kg of postdialysis Body weight ",
                               "Adequacy based on UF ≤ 13 ml/h per kg ",
                               "Duration of HD session needed to achieve UFR =13 ml/h per kg",
                               "PCRn"],                    
                    'Units': ["ml/min","","ml/min",
                              "ml/min","ml/min","ml/min",
                              "ml/min","","v/wk",
                              "","(ml/h per kg)","",
                              "min",""],                    
                    'Result': [results['KTOT'],results['SPKTV'],results['EKTV'],
                               results['VDP'],results['Kru'],results['KR35'],
                               results['EKR35'],results['AdeqEKR'],results['STDKTV'],
                               results['AdeqStdKTV'],results['UFR'],results['AdeqUFR'],
                               results['TDN'],results['PCRn']
                            ]
                }
                df_output = pd.DataFrame(output_data)                
                st.dataframe(df_output.style.format(format_float), 
                             column_config={"Output": st.column_config.Column(width="large")},
                             hide_index=True) # Set the table width to 100%                

                                                                                       
                st.header("eKt/V needed to achieve adequacy on 1, 2, or 3 sessions per week")    
                prescription_data = {
                    '#': [1,2,3,4,5,6],
                    'Output': ["to get EKRU35=12-Krun on 1HD/wk",
                               "to get EKRU35=12-Krun on 2HD/wk",
                               "to get EKRU35=12-Krun on 3HD/wk",
                               "to get stdKt/V=2.3 on 1HD/wk",
                               "to get stdKt/V=2.3 on 2HD/wk",
                               "to get stdKt/V=2.3 on 3HD/wk",
                            ],                                                  
                    'Result': [results['EKTV_1HDwk_EKRVTM'],results['EKTV_2HDwk_EKRVTM'],
                               results['EKTV_3HDwk_EKRVTM'],results['EKTV_1HDwk_STDKTV'],                               
                               results['EKTV_2HDwk_STDKTV'],results['EKTV_3HDwk_STDKTV']                               
                            ]
                }
                df_prescription = pd.DataFrame(prescription_data)                                
                st.dataframe(df_prescription.style.format(format_float),
                             column_config={"Output": st.column_config.Column(width="large")},
                             hide_index=True) # Set the table width to 100%                
                

                pdf = create_pdf(
                    input_data ={
                    "Patient Identifier":patient_id,"Lab Date":date.strftime("%d/%m/%Y"), "Number of Hemodialysis sessions per week":NHDWK, "Preceding inter-dialytic interval":PIDI, 
                    "Pre-dialysis Body Weight (kg)":BW0,"Post-dialysis Body weight (kg)":BWT,"Session length (min)":T,"Blood Flow Rate (ml/min)":QB,
                    "Pre-dilution infusion rate (ml/min)":HDFPRE,
                    "Post-dilution infusion rate (ml/min)":HDFPOST, "Dialysate flow rate ":QD,
                    "Dialyzer urea KoA in vitro ":KOAvitro,
                    "Pre-dialysis Serum Urea Nitrogen":C0,"Post-dialysis Serum Urea Nitrogen":CT,"Renal urea clearance (999 if urine)":KRUw,
                    "Urinary Output ":UO,"Urinary Urea Nitrogen":UUN},
                    output_data={"Patient Identifier":patient_id,
                                 "Total Dialyzer Urea Clearance ":results['KTOT'],
                                 "Single pool Kt/V ":results['SPKTV'],
                                 "Equilibrated Kt/V ":results['EKTV'],
                                 "Urea distribution volume (double pool)":results['VDP'],
                                 "Renal urea clearance (calculated)":results['Kru'],
                                 "KRU normalized per V 35 l ":results['KR35'],
                                 "Equivalent Renal Clearance per V 35 l ":results['EKR35'],
                                 "EKR35 ≥10 – 1.5 KRUN *":results['AdeqEKR'],
                                 "Standard Kt/V":results['STDKTV'],
                                 "StdKt/V ≥ 2.1":results['AdeqStdKTV'],
                                 "Ultrafiltration rate ":results['UFR'],
                                 "UFR ≤ 13 ml/h/kg":results['AdeqUFR'],
                                 "TD needed for UFR=13 ml/h/kg":results['TDN'],
                                 "Protein Catabolic rate normalized":results['PCRn'],
                                 "EKR35 = 12-KRUN on 1HD/wk":results['EKTV_1HDwk_EKRVTM'],
                                 "EKR35 = 12-KRUN on 2HD/wk":results['EKTV_2HDwk_EKRVTM'],
                                 "EKR35 = 12-KRUN on 3HD/wk":results['EKTV_3HDwk_EKRVTM'],
                                 "stdKt/V=2.3 on 1 HD/wk":results['EKTV_1HDwk_STDKTV'],
                                 "stdKt/V=2.3 on 2 HD/wk":results['EKTV_2HDwk_STDKTV'],
                                 "stdKt/V=2.3 on 3 HD/wk":results['EKTV_3HDwk_STDKTV']},
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
                                   