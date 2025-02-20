import streamlit as st
import datetime
from components.ihd_calculator import calculate_ihd
from components.pdf_builder import create_pdf

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
                
                col1, col2 = st.columns([8,1])
                with col1:
                    st.markdown(f"<span class='font-bigger'>Kd tot (ml/min)</span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>spKt/V </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>eKt/V (ml/min) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Vdp (L) (ml/min) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Kru (ml/min) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>KR35 (ml/min per 35 L V) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>EKR35 (ml/min per 35 L V) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Adequacy based EKR35 ≥ minimum variable target (10 -1.5 KR35) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>StdKt/V (v/wk)</span>" , unsafe_allow_html=True)                
                    st.markdown(f"<span class='font-bigger'>Adequacy based on StdKt/V≥2.1 v/wk </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Hourly Ultrafiltration rate per kg of postdialysis Body weight (ml/h per kg) </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Adequacy based on UF ≤ 13 ml/h per kg </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>Duration of HD session needed to achieve UFR =13 ml/h per kg  (min) </span>" , unsafe_allow_html=True)                
                    st.markdown(f"<span class='font-bigger'>PCRn </span>" , unsafe_allow_html=True)                                
                    st.markdown("<br/>", unsafe_allow_html=True)                         
                                    
                with col2: 
                    st.markdown(f" <span class='font-bigger'><strong>{results['KTOT']}</strong></span>", unsafe_allow_html=True)
                    st.markdown(f" <span class='font-bigger'><strong>{results['SPKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['VDP']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['Kru']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['KR35']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKR35']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['AdeqEKR']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['STDKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['AdeqStdKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['UFR']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['AdeqUFR']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['TDN']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['PCRn']}</strong></span>", unsafe_allow_html=True)   
                
                st.header("eKt/V needed to achieve adequacy on 1, 2, or 3 sessions per week")    
                col3, col4 = st.columns([8,1])
                with col3:
                    st.markdown(f"<span class='font-bigger'>to get EKRU35=12-Krun on 1HD/wk </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>to get EKRU35=12-Krun on 2HD/wk </span>" , unsafe_allow_html=True)                
                    st.markdown(f"<span class='font-bigger'>to get EKRU35=12-Krun on 3HD/wk </span>" , unsafe_allow_html=True)                
                    st.markdown(f"<span class='font-bigger'>to get stdKt/V=2.3 on 1HD/wk </span>" , unsafe_allow_html=True)
                    st.markdown(f"<span class='font-bigger'>to get stdKt/V=2.3 on 2HD/wk </span>" , unsafe_allow_html=True)                
                    st.markdown(f"<span class='font-bigger'>to get stdKt/V=2.3 on 3HD/wk </span>" , unsafe_allow_html=True)                
                
                with col4: 
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_1HDwk_EKRVTM']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_2HDwk_EKRVTM']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_3HDwk_EKRVTM']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_1HDwk_STDKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_2HDwk_STDKTV']}</strong></span>", unsafe_allow_html=True)   
                    st.markdown(f" <span class='font-bigger'><strong>{results['EKTV_3HDwk_STDKTV']}</strong></span>", unsafe_allow_html=True)   
               

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
                                   