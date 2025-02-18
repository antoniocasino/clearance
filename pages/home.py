import streamlit as st
import pandas as pd

def home_page():
    st.title("Haemodialysis Prescription Calculator")
    st.markdown("""
         <style>
            p {text-align: justify;}
        </style>
        """,
        unsafe_allow_html=True
    )  
    st.markdown("""
    Francesco Gaetano Casino<sup>1</sup>, Carlo Basile<sup>1</sup>, and Antonio Casino<sup>2</sup>

    <sup>1</sup> Associazione Nefrologica Gabriella Sebastio, Martina Franca, Italy<br/>
    <sup>2</sup> Engineer at Cronos Europa, Milano, Italy <br/>

    The App “Haemodialysis prescription calculator” provides guidance for the assessment and prescription of haemodialysis (HD) in general and of incremental HD (IHD) in particular. It is reserved exclusively for nephrologists involved in the treatment of patients on maintenance HD, as all calculations must necessarily be confirmed by qualified medical professionals before clinical use or for diagnostic purposes. 

    This App is an updated version of the software “SPEEDY”, acronym for “Spreadsheet for the Prescription of incrEmental haEmoDalYsis” (1), which uses the same equations as “Solute Solver” (2), the software recommended by the KDOQI clinical practice guidelines for HD adequacy (3), and provides comparable results.  

    The App is particularly useful in the early stages of kidney replacement treatment (KRT), where the presence of some residual kidney function (RKF) may allow an incremental approach to KRT. The latter consists of starting HD with a low frequency of sessions and/or low dialysis dose (Kt/V), to be increased progressively and appropriately as RKF decreases, to maintain the amount of dialysis delivered during the week in an adequate range, i.e., above the minimum permitted level. This entails the need to monthly monitor both RKF, expressed by the residual renal clearance of urea (KRU), and total weekly clearance (dialysis + renal), expressed by one of the two current adequacy indices, i.e., the standard Kt/V (stdKt/V) (3,4,5) and/or the equivalent renal clearance of urea (EKR) (6,7) to verify that they are at least equal to 2.1 volumes/week (3) or 10 - 1.5 x KRU (8), respectively.

    The App is made up of 3 subroutines. The first one, called "<strong>Adequacy</strong>", calculates all the main parameters of the double pool urea kinetic model (UKM), and shows the dialysis dose values (eKt/V) necessary to prescribe adequacy with one, two, and three weekly sessions, respectively, according to criteria based alternately on stdKt/V or EKR with variable target (7), in order to choose the most suitable frequency and dose for the individual patient (Table 1). 

    The second subroutine, called "<strong>Kd&Qb</strong>", first calculates the dialysis clearance (Kd) of urea necessary (Kdn) to reach the target eKt/V as a function of urea distribution volume (V) and KRU, and then the blood flow rate necessary (Qbn) to reach Kdn, based on the characteristics of the dialyzer, i.e., the dialyzer mass transfer coefficient for urea (KoA), and the values of the other parameters that determine Kd (Table 2). 

    The third subroutine, called <strong>KoA</strong>, calculates the in vitro value of KoA, starting from the Kd data reported in the technical data sheet of the dialyzer together with the other relevant parameters (Table 3).

    Below are the respective input and output values for the three subroutines, with symbols, units of measurement, minimum and maximum levels of acceptability, and an example value:
    """, unsafe_allow_html=True)

    st.header("Table 1: Input and Output values of the subroutine “Adequacy”")

    input_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17],
        'Input': ["Patient id","Lab date","Number of HD per week","Preceding interdialytic interval","Pre-dialysis body weight","Post-dialysis body weight",
                  "Session length","Blood flow rate","Pre-dialyzer infusion rate","Post-dialyzer infusion rate","Dialysate flow rate ",
                  "Dialyzer urea KoA in vitro ","Pre-dialysis Serum Urea Nitrogen","Post-dialysis Serum Urea Nitrogen","Renal urea clearance (999 if urine)",
                  "Urinary Output ","Urinary Urea Nitrogen"],
        'Symbol': ["PTID","Lab date  ","NHDWK","PIDI","BW0","BWT","TD","Qb","HDFPRE","HDFPOST","Qd","KoA","C0","CT","KRU","UO","UUN"],
        'Units': ["", 	"(dd/mm/wk)","Days","Days","kg","kg","min","ml/min","ml/min","ml/min","ml/min","ml/min","mg/dl","mg/dl","ml/min","ml/day","mg/dl"],
        'Min': ["", "","1","2","20","20","60","100","0","0","100","600","20","10","0","0","0"],
        'Max': ["", "","3","7","140","140","480","450","250","150","1000","2000","200","100","7","4000","1000"],
        'Example   ': ["PTID", "12/01/2025","2","4","73","70","240","300","0","0","500","800","80","30","999","1000","500"]
    }
    
    df_input = pd.DataFrame(input_data)
    st.markdown("""<div class="section-title"><strong>Input Data</strong></div>""",unsafe_allow_html=True)    
    st.dataframe(df_input,hide_index=True)  # or st.table(df_input) for a static table

    output_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14],
        'Output': ["Total Dialyzer Urea Clearance ","Single pool Kt/V","Equilibrated Kt/V ","Urea distribution volume (double pool)","Renal urea clearance (calculated)","KRU normalized per V 35 l ","Equivalent Renal Clearance per V 35 l ","EKR35 ≥10 – 1.5 KRUN *","Standard Kt/V","StdKt/V ≥ 2.1","Ultrafiltration rate ","UFR ≤ 13 ml/h/kg","TD needed for UFR=13 ml/h/kg","Protein Catabolic rate normalized"],
        'Symbol': ["Kd Tot","spKt/V","eKt/V","Vdp","KRU","KRUN","EKR35","Adequacy","StdKt/V","Adequacy","UFR","Adequacy","TDN ","PCRn"],
        'Units': ["ml/min","dimensionless","dimensionless","(l)","ml/min","ml/min per 35l V","ml/min per 35l V","Yes/No","Volume/wk","Yes/No","ml/h per kg","Yes/No","min per session","g/kg/day "],
        'Min': ["", "","", "","", "","", "","", "","", "","", ""],
        'Max': ["", "","", "","", "","", "","", "","", "","", ""],
        'Example': ["192.5","1.13","1.01","41.1","4.35","3.70","10.21","Yes","2.39","Yes","10.7","Yes","198","0.99"]
    }

    df_output = pd.DataFrame(output_data)

    st.markdown("""<div class="section-title"><strong>Output Data</strong></div>""",unsafe_allow_html=True) 
    st.dataframe(df_output,hide_index=True) # or st.table(df_output) for a static table

    
    prescription = {
        '#': [1, 2, 3, 4, 5, 6],
        'Prescription': ["EKR35 = 12-KRUN on 1HD/wk","EKR35 = 12-KRUN on 1HD/wk","EKR35 = 12-KRUN on 1HD/wk","stdKt/V=2.3 on 1 HD/wk","stdKt/V=2.3 on 2 HD/wk","stdKt/V=2.3 on 3 HD/wk"],      
        'Symbol': ["", "", "", "", "", ""],
        'Units':  ["", "", "", "", "", ""],
        'Min':  ["", "", "", "", "", ""],
        'Max':  ["", "", "", "", "", ""],
        'Example': ["1.76","0.70","0.46","3.20","0.85","0.50"]
    }
    df_prescription = pd.DataFrame(prescription)
    st.markdown("""<div class="section-title"><strong>eKt/V to be prescribed to attain</strong></div>""",unsafe_allow_html=True) 
    st.dataframe(df_prescription,hide_index=True) # or st.table(df_output) for a static table

    st.markdown("""
    <p>* The calculated values for Kdn and Qbn are theoretical estimates under ideal conditions. The actual values can be influenced by various factors, such as the measurement method used, variability of blood and dialysis flows, presence of vascular access recirculation, etc.</p>
    """, unsafe_allow_html=True)

    st.header("Table 2: Input and Output values of the subroutine “Kd&Qb ”")


    input_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'Input': ["Patient id","Patient’s urea distribution volume ","Expected intradialysis weight loss ","KoA of the dialyzer in vitro","Pre-dialyzer infusion rate ","Post-dialyzer infusion rate ","Dialysate flow rate ","Session length","Target eKt/V of the current prescription"],
        'Symbol': ["PTID","V ","UF","KoA","HDFPRE","HDFPOST","Qd","TD","eKt/V"],
        'Units': ["","L","L or kg","ml/min","ml/min","ml/min","ml/min","min","dimensionless"],
        'Min': ["","20","0.1","600","0","0","100","60","0.3"],
        'Max': ["","50","5","2000","250","150","1000","480","2.0"],
        'Example   ': ["PTID", "35","2","1200","0","0","500","240","1.4"]
    }
    df_input = pd.DataFrame(input_data)
    st.markdown("""<div class="section-title"><strong>Input Data</strong></div>""",unsafe_allow_html=True)    
    st.dataframe(df_input,hide_index=True)  # or st.table(df_input) for a static table

    output_data = {
        '#': [1, 2],
        'Output': ["Dialyzer Urea Clearance needed to attain the target eKt/V * ","Blood flow rate needed to attain the necessary Kdn value *"],
        'Symbol': ["Kdn","Qbn"],
        'Units': ["ml/min","ml/min"],
        'Min': ["100", "100"],
        'Max': ["300", "300"],
        'Example': ["239","531"]
    }
    df_output = pd.DataFrame(output_data)

    st.markdown("""<div class="section-title"><strong>Output Data</strong></div>""",unsafe_allow_html=True) 
    st.dataframe(df_output,hide_index=True) # or st.table(df_output) for a static table


    st.markdown("""
    <p>* The calculated values ​​for Kdn and Qbn are theoretical estimates under ideal conditions. The actual values ​​can be influenced by various factors, such as the measurement method used, variability of blood and dialysis flow rates, presence of vascular access recirculation, etc…</p>
    """, unsafe_allow_html=True)


    st.header("Table 3: Input and Output values of the subroutine “KoA”")

    input_data = {
        '#': [1, 2, 3, 4],
        'Input': ["Dialyzer name","Dialysate flow rate ","Ultrafiltration rate ","Dialyzer Urea clearance*"],
        'Symbol': ["Dz name","Qd","Qf","Kd"],
        'Units': ["","ml/min","ml/min","ml/min"],
        'Min': ["","500","0","100"],
        'Max': ["","800","30","350"],
        'Example': ["Dzname","500","10","250"]
    }
    df_input = pd.DataFrame(input_data)
    st.markdown("""<div class="section-title"><strong>Input Data</strong></div>""",unsafe_allow_html=True)    
    st.dataframe(df_input,hide_index=True)  # or st.table(df_input) for a static table

    output_data = {
        '#': [1, 2],
        'Output': ["Diffusive Kd ","KoA of the dialyzer in vitro"],
        'Symbol': ["Kd0","KoA"],
        'Units': ["ml/min","ml/min"],
        'Min': ["", ""],
        'Max': ["", ""],
        'Example': ["248","824"]
    }
    df_output = pd.DataFrame(output_data)

    st.markdown("""<div class="section-title"><strong>Output Data</strong></div>""",unsafe_allow_html=True) 
    st.dataframe(df_output,hide_index=True) # or st.table(df_output) for a static table

    st.markdown("""    
    <p>* From specific sheet, calculated in vitro and in absence uf significant ultrafiltration (Qf≤30 ml/min)</p>
    """, unsafe_allow_html=True)


    st.header("References")

    st.markdown("""
    1. Casino FG, Basile C. A user-friendly tool for incremental haemodialysis prescription. Nephrol Dial Transplant. 2018;33(6): 1046-1053. https://doi.org/10.1093/ndt/gfx343 
    pub 5/1/2018  EID: 2-s2.0-85044593750 
    2. Daugirdas JT, Depner TA, Greene T et al. Solute-solver: a web-based tool for modeling urea kinetics for a broad range of hemodialysis schedules in multiple patients. Am J Kidney Dis 2009; 54: 798–809
    3. National Kidney Foundation. KDOQI clinical practice guidelines for hemodialysis adequacy: 2015 update. Am J Kidney Dis 2015; 66: 884–930 
    4. Gotch FA: The current place of urea kinetic modelling with respect to different dialysis modalities. Nephrol Dial Transplant 13:S10-S145, 1998 (suppl 6)
    5. Daugirdas JT, Depner TA, Greene T et al. Standard Kt/Vurea: a method of calculation that includes effects of fluid removal and residual kidney clearance. Kidney Int 2010; 77: 637–644
    6. Casino FG, Lopez T: The equivalent renal urea clearance: A new parameter to assess dialysis dose. Nephrol Dial Transplant 11:1574-1581, 1996 
    7. Casino FG, Basile C. The variable target model: a paradigm shift in the incremental haemodialysis prescription. Nephrol Dial Transplant 2017; 32:182–190, doi: 10.1093/ndt/gfw339.
    8. Basile C and Casino FG, on behalf of the EUDIAL Working Group of ERA-EDTA. Incremental haemodialysis and residual kidney function: more and more observations but no trials. Nephrol Dial Transplant (2019) 34: 1806–1811.doi: 10.1093/ndt/gfz035
    """, unsafe_allow_html=True)
