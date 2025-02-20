import streamlit as st
import datetime
from components.ihd_calculator import calculate_ihd
from components.pdf_builder import create_pdf

def adequacy_page():    
    st.title("PRESCRIPTION OF INCREMENTAL HD BASED ON UREA KINETICS") 
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
    
    if "previous_value" not in st.session_state:
        st.session_state.previous_value = 0   
    
    def PIDI_value():
        if NHDWK ==1:
            return 7
        elif NHDWK ==2:
            return 3
        elif NHDWK ==3:
            return 2
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
        value=2,     
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
        value=20,
    )                       
    BWT = st.number_input(
        "Post-dialysis Body weight (kg)",
        min_value=20,
        max_value=140,
        value=20,            
        step=1
    )
    T = st.number_input(
        "Session length (min)",
        key="idh_time",
        min_value=60,
        max_value=480,  
        value=240,          
        step=1
    )  
    QB = st.number_input(
        "Blood Flow Rate (ml/min)",
        min_value=100,
        max_value=400,            
        value=100,
        step=1
    )
    HDFPRE = st.number_input(
        "Pre-dilution infusion rate (ml/min)",
        min_value=0,
        max_value=250, 
        value=200,           
        step=1
    )
   
    HDFPOST = st.number_input(
        "Post-dilution infusion rate (ml/min)",
        min_value=0,
        max_value=150,            
        step=1,
        value=100        
    )   
    QD = st.number_input(
        "Dialysate flow rate (ml/min)",
        min_value=300,
        max_value=800,            
        value=300,
        step=1
    )
    KOAvitro = st.number_input(
        "Dialyzer Urea KoA in vitro (KoA_vitro, ml/min)",
        min_value=600,
        max_value=2000, 
        value=600,           
        step=1
    )   
    C0 = st.number_input(
        "Pre-dialysis Serum Urea Nitrogen (C0, mg/dl)",
        min_value=20,
        max_value=200,            
        step=1,
        value=20
    )
    CT = st.number_input(
        "Post-dialysis Serum Urea Nitrogen (CT, mg/dl)",
        min_value=5,
        max_value=150,            
        step=1,
        value=5
    )   
    KRUw = st.number_input(
        "Renal urea clearance in serum water conc. (KRU, ml/min : 0-7, 999 if urine)",
        min_value=0,
        max_value=7,            
        value=0,
        step=1
    )
    UO = st.number_input(
        "Urinary Output (UO, ml/24 h)",
        min_value=0,
        max_value=4000, 
        value=500,           
        step=1
    )   
    UUN = st.number_input(
        "Urinary Urea Nitrogen (UUN, mg/dl)",
        min_value=0,
        max_value=1000,            
        step=1,
        value=500        
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
                        results[key]=round(value,1) 
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
                    "PTID":patient_id,"LABDATE":date, "NHDWK":NHDWK, "PIDI":PIDI, 
                    "BW0":BW0,"BWT":BWT,"T":T,"QB":QB,"HDFPRE":HDFPRE,
                    "HDFPOST":HDFPOST, "QD":QD,"KOAvitro":KOAvitro,
                    "C0":C0,"CT":CT,"KRUw":KRUw, "UO":UO,"UUN":UUN},
                    output_data=results,
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
                                   