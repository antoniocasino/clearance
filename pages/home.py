import streamlit as st
import pandas as pd

def home_page():
    st.title("App EuReCa")
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

    The App “EuReCa” (acronym for Eu.ropean Re.nal Ca.lculator) is an updated version of the software “SPEEDY”, acronym for “S.preadsheet for the P.rescription of incrE.mental haEmoD.alYsis” (1), which uses the same equations as “Solute-solver” (2), the software recommended by the KDOQI clinical practice guidelines for HD adequacy (3), and provides comparable results.  

    The App EuReCa provides guidance for the assessment and prescription of haemodialysis (HD) in general and of incremental HD in particular. It is particularly useful in the early stages of kidney replacement treatment (KRT), where the presence of some residual kidney function (RKF) may allow an incremental approach to KRT. The latter consists of starting HD with a low frequency of sessions and/or low dialysis dose (Kt/V), to be increased progressively and appropriately as RKF decreases, to maintain the amount of dialysis delivered during the week in an adequate range, i.e., above the minimum permitted level. This entails the need to monthly monitor both RKF, expressed by the residual renal clearance of urea (Kru), and total weekly clearance (dialysis + renal), expressed by one of the two current adequacy indices, i.e., the standard Kt/V (stdKt/V) (3-5) and/or the equivalent renal clearance of urea (EKRU) (6,7) to verify that they are at least equal to 2.1 volumes/week (3) or 10 - 1.5 x Kru (8), respectively.

    Of note, in the App EuReCa, the current equation that computes the stdKt/V (3) has been replaced by a new equation (*) which gives very similar values of stdKt/V, but has the advantage that it can be solved to directly give the value of eKt/V to be prescribed to reach the target stdKt/V of 2.3 volumes/week. Similarly, the previous cubic equation to calculate EKRU has been replaced by a linear equation that can be solved to directly give the value of eKt/V to be prescribed to reach the target EKRU of 12 – Kru (ml/min pe 35 l V) (*).

    <span style="font-style: italic;">* Francesco Gaetano Casino, Antonio Casino, Elisa Tarrio Helva, and Carlo Basile. New formulas for calculating the adequacy of incremental haemodialysis (submitted). </i>


    The App EuReCa is reserved exclusively for nephrologists involved in the treatment of adult patients on maintenance HD, as all calculations must necessarily be confirmed by qualified medical professionals before clinical use or for diagnostic purposes.                

    The App is made up of 5 subroutines:
    
    The first subroutine, called "<strong>Adequacy</strong>", is the main program that calculates all the main parameters of the double pool urea kinetic model (UKM): it shows the dialysis dose values (eKt/V) necessary to prescribe adequacy with one, two, and three weekly HD sessions, respectively, according to criteria based alternately on stdKt/V or EKRU with variable target (7), in order to choose the most suitable frequency and dose for the individual patient (Table 1).

    The second subroutine, called “<strong>stdKt/V & EKRU</strong>”, calculates these two parameters for given values of eKt/V, length of the previous interdialytic interval and associated weight gain, Kru and urea distribution volume (V) of the patient (Table 2).            

    The third subroutine, called “<strong>eKt/V</strong>”, calculates the dialysis doses to be prescribed to achieve targets based on both stdKt/V and EKRU with the selected treatment schedule, for given values of length of the previous interdialytic interval and associated weight gain, Kru and V of the patient (Table 3).        
        
    The fourth subroutine, called "<strong>Kd&Qb</strong>", first calculates the dialysis clearance (Kd) of urea necessary (Kdn) to reach the target eKt/V as a function of V and Kru, and then the blood flow rate necessary (Qbn) to reach Kdn, based on the characteristics of the dialyzer, i.e., the dialyzer mass transfer coefficient for urea (KoA), and the values of the other parameters that determine Kd (Table 4).
                
    The fifth subroutine, called "<strong>KoA</strong>", calculates the in vitro value of KoA, starting from the Kd data reported in the technical sheet of the dialyzer together with the other relevant parameters (Table 5).  

    Below are the respective input and output values for the three subroutines, with symbols, units of measurement, minimum and maximum levels of acceptability, and an example value:    
    """, unsafe_allow_html=True)

    st.header("Table 1: Input and Output values of the subroutine “Adequacy”")

    input_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17],
        'Input': ["Patient id","Lab date","Number of HD per week","Preceding interdialytic interval","Pre-dialysis body weight","Post-dialysis body weight",
                  "Session length","Blood flow rate","Pre-dialyzer infusion rate","Post-dialyzer infusion rate","Dialysate flow rate ",
                  "Dialyzer urea KoA in vitro ","Pre-dialysis Blood or Serum Urea Nitrogen","Post-dialysis Blood or Serum Urea Nitrogen","Renal urea clearance (999 if urine)* ",
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
    st.markdown("""<span>* If the patient has forgotten to collect urine,
                 a recent Kru value can be used, which should range from 0 
                to 7 ml/min. If urine is available, enter 999 as the Kru input, which will allow the new Kru value to be calculated.</span><br/>""",
                unsafe_allow_html=True)

    output_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18],
        'Output': ["Total Dialyzer Urea Clearance","Single pool Kt/V","Equilibrated Kt/V","Urea distribution volume (double pool)","Protein catabolic rate (g/kg/day)","Renal urea clearance (calculated)","KRU normalized per V 35 l","Equivalent Renal Clearance per V 35 l ","EKRUN_variable target (10-1.5 KRUN)*","EKR35 ≥10 – 1.5 KRUN *","Standard Kt/V","StdKt/V ≥ 2.1","Ultrafiltration rate",
                   "UFR ≤ 13 ml/h/kg","TD needed for UFR=13 ml/h/kg","Weekly net Ultrafiltration","eKt/V to get EKRUN=12-KRUN ","eKt/V to be prescribed to get stdKt/V=2.3"],
        'Symbol': ["Kd Tot","spKt/V","eKt/V","Vdp","PCRn","KRU","KRUN","EKR35","EKRU_VTM","Adequacy","StdKt/V","Adequacy","UFR","Adequacy","TDN ","UFwk","eKt/V","eKt/V"],
        'Units': ["ml/min","dimensionless","dimensionless","(l)","(g/kg/day)","ml/min","ml/min per 35l V","ml/min per 35l V","ml/min per 35l V","Yes/No","Volume/wk","Yes/No","ml/h per kg","Yes/No","min per session","dimensionless","dimensionless","(l)"],
        'Min': ["","","","","","","","","","","","","","","","","",""],
        'Max': ["","","","","","","","","","","","","","","","","",""],
        'Example': ["192.5","1.14","1.01","40.76","1.00","4.35","3.74","9.94","4.40","Yes","2.39","Yes","10.71","Yes","197.80","5.22","0.70","0.91"]
    }

    df_output = pd.DataFrame(output_data)        
    st.markdown("""<div class="section-title"><strong>Output Data</strong></div>""",unsafe_allow_html=True) 
    st.dataframe(df_output,hide_index=True) # or st.table(df_output) for a static table
    st.markdown("""<br/>* According to the variable target model of EKR, the adequate EKR35UN varies as a function of normalized KRU, (according to the following equation: EKRUN ≥10 – 1.5 KRUN), from the minimum value of 4 ml/min pe V 35 l, which corresponds to a glomerular filtration rate of about 6 ml/min/1.73 m2. It can be used as a reasonable theoretical KRU threshold to start HD, to the maximum value of 10 ml/min per V 35 l, which corresponds to the adequate level of eKt/V=1.05 in anuric patients on thrice weekly HD.""",unsafe_allow_html=True) 
    

    input_table_2 = {
        '#': [1, 2, 3, 4, 5, 6],
        'Input': ["Patient id","Number of HD per week","Normalised Kru","eKt/V","Preceding interdialytic interval","Weight gain during PIDI"],
        'Symbol': ["PTID", "NHDWK", "KRUN", "eKt/V", "PIDI", "IDWG"],
        'Units': ["", "Days", "ml/min per 35 l V", "dimensionless", "Days", "kg"],
        'Min': ["", "1", "0", "0.5", "2", "0"],
        'Max': ["", "3", "7", "2", "7", "5"],
        'Example': ["PTID", "2", "3.7", "1.01", "4", "3"],
    }
    df_input_table_2 = pd.DataFrame(input_table_2)
    st.header("Table 2: Input and Output values of the subroutine “stdKt/V & EKRU”")
    st.markdown("""<div class="section-title">Input Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_input_table_2,hide_index=True) # or st.table(df_output) for a static table

    output_table_2 = {
        '#': [7, 8, 9, 10, 11],
        'Output': ["Weekly net Ultrafiltration", "stdKt/V  (v/wk) ", "EKRUN  ", "EKRUN variable target=12-KRUN", "EKRUN_min_adequate"],
        'Symbol': ["UFwk", "stdKt/V", "EKRUN", "EKRUN_VTM", "EKRUN_min"],
        'Units': ["", "", "ml/min per 35 l V", "ml/min per 35 l V", "ml/min per 35 l V"],
        'Min': ["", "", "", "", "", ],
        'Max': ["", "", "", "", "", ],
        'Example': ["5.25", "2.37", "9.88", "8.6", "4.45"],
    }
    df_output_table_2 = pd.DataFrame(output_table_2)
    st.markdown("""<div class="section-title">Output Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_output_table_2,hide_index=True)

    input_table_3 = {
        '#': [1, 2, 3, 4, 5],
        'Input': ["Patient id","Selected number of HD per week","Normalised Kru","Preceding interdialytic interval","Weight gain during PIDI"],      
        'Symbol': ["PTID", "NHDWK", "KRUN", "PIDI", "IDWG"],
        'Units':  ["", "Days ", "ml/min per 35 l V", "Days", "kg"],
        'Min':  ["", "1", "0", "2", "0"],
        'Max':  ["", "3", "7", "7", "5"],
        'Example': ["PTID","1","4","7","2"]
    }
    df_input_table_3 = pd.DataFrame(input_table_3)
    st.header("Table 3: Input and Output values of the subroutine “eKt/V” to be prescribed")
    st.markdown("""<div class="section-title">Input Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_input_table_3,hide_index=True) 

    output_table_3 = {
        '#': [6, 7, 8],
        'Output': ["Weekly net Ultrafiltration","eKtV to get EKRUN = 12 - KRUN","eKtV to get stdKt/V = 2.3"],      
        'Symbol': ["UFwk", "eKt/V", "eKt/V"],
        'Units':  ["l", "dimensionless ", "dimensionless"],
        'Min':  ["", "", ""],
        'Max':  ["", "", ""],
        'Example': ["2.0", "1.44", "2.16"],
    }
    df_output_table_3 = pd.DataFrame(output_table_3)
    st.markdown("""<div class="section-title">Output Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_output_table_3,hide_index=True) 


    input_table_4 = {
        '#': [1, 2, 3, 4, 5,6,7,8,9],
        'Input': ["Patient id","Patient’s urea distribution volume ","Expected intradialysis weight loss ",
                  "KoA of the dialyzer in vitro","Pre-dialyzer infusion rate","Post-dialyzer infusion rate",
                  "Dialysate flow rate","Session length","Target eKt/V of the current prescription"],      
        'Symbol': ["PTID", "V", "UF", "KoA", "HDFPRE","HDFPOST","Qd","TD","eKt/V"],
        'Units':  ["", "L ", "L or kg", "ml/min", "ml/min", "ml/min", "ml/min", "min","dimensionless"],
        'Min':  ["", "20", "0.1", "600", "0", "0","100","60","0.3"],
        'Max':  ["", "50", "5", "2000", "250", "150","1000","480","2.0"],
        'Example': ["PTID","35","2","1200","0","0","500","240","1.4"]
    }
    df_input_table_4 = pd.DataFrame(input_table_4)
    st.header("Table 4: Input and Output values of the subroutine “Kd&Qb”")
    st.markdown("""<div class="section-title">Input Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_input_table_4,hide_index=True) 

    output_table_4 = {
        '#': [10, 11],
        'Ouput': ["Dialyzer Urea Clearance needed to attain the target eKt/V *","Dialyzer Urea Clearance needed to attain the target eKt/V *"],      
        'Symbol': ["Kdn", "Qbn"],
        'Units':  ["ml/min", "ml/min "],
        'Min':  ["100", "100"],
        'Max':  ["300", "450"],
        'Example': ["239", "351"],
    }
    df_output_table_4 = pd.DataFrame(output_table_4)
    st.markdown("""<div class="section-title">Output Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_output_table_4,hide_index=True) 
    st.markdown("""
    <p>*The calculated values for Kdn and Qbn are theoretical estimates under ideal conditions. The actual values can be influenced by various factors, such as the measurement method used, variability of blood and dialysis flow rates, presence of vascular access recirculation, etc…</p>
    """, unsafe_allow_html=True)

    st.header("Table 5: Input and Output values of the subroutine “KoA”")
    
    input_table_5 = {
        '#': [1, 2, 3, 4],
        'Input': ["Dialyzer name","Dialysate flow rate","Ultrafiltration rate","Dialyzer Urea clearance*"],
        'Symbol': ["Dz name","Qd ","Qf","Kd"],
        'Units': ["","ml/min","ml/min","ml/min"],
        'Min': ["","500","0","100"],
        'Max': ["","800","30","350"],
        'Example   ': ["Dzname", "500","10","50"]
    }
    df_input_table_5 = pd.DataFrame(input_table_5)
    st.markdown("""<div class="section-title"><strong>Input Data</strong></div>""",unsafe_allow_html=True)    
    st.dataframe(df_input_table_5,hide_index=True)  # or st.table(df_input) for a static table

    output_table_5 = {
        '#': [1, 2],
        'Output': ["Diffusive Kd ","KoA of the dialyzer in vitro"],
        'Symbol': ["Kd0","KoA"],
        'Units': ["ml/min","ml/min"],
        'Min': ["", ""],
        'Max': ["", ""],
        'Example': ["248","824"]
    }    
    df_output_table_5 = pd.DataFrame(output_table_5)
    st.markdown("""<div class="section-title">Output Data</div>""",unsafe_allow_html=True) 
    st.dataframe(df_output_table_5,hide_index=True) 
    st.markdown("""
    <p>* * From specific sheet, calculated in vitro without significant ultrafiltration (Qf≤30 ml/min)</p>
    """, unsafe_allow_html=True)    

    st.header("References")

    st.markdown("""
    1.	Casino FG, Basile C. A user-friendly tool for incremental haemodialysis prescription. Nephrol Dial Transplant. 2018;33(6): 1046-1053. https://doi.org/10.1093/ndt/gfx343 
    pub 5/1/2018  EID: 2-s2.0-85044593750 
    2.	Daugirdas JT, Depner TA, Greene T et al. Solute-solver: a web-based tool for modeling urea kinetics for a broad range of hemodialysis schedules in multiple patients. Am J Kidney Dis 2009; 54: 798–809
    3.	National Kidney Foundation. KDOQI clinical practice guidelines for hemodialysis adequacy: 2015 update. Am J Kidney Dis 2015; 66: 884–930 
    4.	Gotch FA: The current place of urea kinetic modelling with respect to different dialysis modalities. Nephrol Dial Transplant 13:S10-S145, 1998 (suppl 6)
    5.	Daugirdas JT, Depner TA, Greene T et al. Standard Kt/Vurea: a method of calculation that includes effects of fluid removal and residual kidney clearance. Kidney Int 2010; 77: 637–644
    6.	Casino FG, Lopez T: The equivalent renal urea clearance: A new parameter to assess dialysis dose. Nephrol Dial Transplant 11:1574-1581, 1996 
    7.	Casino FG, Basile C. The variable target model: a paradigm shift in the incremental haemodialysis prescription. Nephrol Dial Transplant 2017; 32:182–190, doi: 10.1093/ndt/gfw339.
    8.	Basile C and Casino FG, on behalf of the EUDIAL Working Group of ERA-EDTA. Incremental haemodialysis and residual kidney function: more and more observations but no trials. Nephrol Dial Transplant (2019) 34: 1806–1811.doi: 10.1093/ndt/gfz035 
    """, unsafe_allow_html=True)

    st.markdown("""<strong>DISCLAIMER</strong><br/>
                <br/><strong>1. THIS CALCULATION PROGRAM DOES NOT PROVIDE MEDICAL ADVICE</strong>
                <br/>The calculation program provided is available to you for informational purposes only. Although the calculation program provides educational information about healthcare, it does not provide medical diagnoses or recommendations regarding an individual’s medical treatment. 
                <br/>This software is to be used as a guide only, and health care professionals should use sound clinical judgement and individualize therapy to each specific patient care situation. All calculations must be confirmed before clinical use or diagnostic purposes by qualified medical professionals.                 
                <br/><strong>2. DISCLAIMER OF WARRANTIES</strong>
                <br/>You understand that we cannot and do not guarantee or warrant that files available for downloading from the Internet or this Site will be free of viruses or other destructive code. You are responsible for
                implementing sufficient procedures and checkpoints to satisfy your particular requirements for anti-virus protection and accuracy of data input and output, and for maintaining a means external to our site for any reconstruction of the lost data.
                <br/>We do not warrant that: (a) this calculation program will meet your requirements or will be available on an uninterrupted, timely, secure, or error-free basis; (b) the content will be up-to-date, complete, comprehensive or accurate; (c) the results that may be obtained from the use of this calculation program will be accurate or reliable; (d) defects, if any, will be corrected                
                <br/><strong>3. LIMITATION OF LIABILITY</strong>
                <br/>In no event shall the authors be liable to any party for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this software and its documentation, even if the authors have been advised of the possibility of such damage. the authors specifically disclaim any warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose.
                <br/>The software provided hereunder is on an 'as is' basis, and the authors have no obligations to provide maintenance, support, updates, enhancements, or modifications.                
                <br/><strong>4. LIMITATIONS OF THE CALCULATION PROGRAM</strong>
                <br/>The code is quite complex, and it has not yet been extensively validated or tested, and there is no experience as of yet in using it in the pediatric population. The urea kinetic model depends on a stable level of both residual kidney function and urea generation rate, and is intended for modeling chronic patients only; it is not applicable to modeling adequacy in patients with acute kidney injury.""", unsafe_allow_html=True)
    