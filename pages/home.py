import streamlit as st
import pandas as pd

def home_page():
    st.title("EuReCa App")
    st.markdown("""
         <style>
            p {text-align: justify;}
        </style>
        """,
        unsafe_allow_html=True
    ) 
    st.subheader("About the App and Authors")

    st.write("""
    The authors of the **“EuReCa”** app (acronym for Eu.ropean Re.nal Ca.lculator) are Francesco Gaetano Casino (Nephrologist), Antonio Casino (Management Engineer) and Carlo Basile (Nephrologist).

    As detailed in the **"Key Information for Nephrologists on Using the EuReCa App"** section, the app, in addition to assessing dialysis adequacy, can provide prescription guidance for key HD operating parameters, such as total weekly clearance (kidney + dialysis), treatment frequency, dialysis dose, dialyser clearance, blood flow rate, and session duration, taking into account the native kidney urea clearance (KRU). As such, the app is particularly useful for assessing and prescribing **incremental HD (iHD)**.

    Casino and Basile have long experience in iHD (1,2) and have already produced a tool for iHD prescription, called **“SPEEDY”**, acronym for **“S.preadsheet for the P.rescription of incrE.mental haE.moD.ialY,sis”** (3), which uses the same equations as “Solute-solver” (4), the software recommended by the KDOQI clinical practice guidelines for HD adequacy (5) and provides comparable results.

    EuReCa app is an updated version of SPEEDY (3) and aims to further simplify the assessment and prescription of iHD. The latter consists of initiating HD in patients with significant KRU with a low frequency of sessions and/or a low dialysis dose (eKt/V), to be increased progressively and appropriately as KRU decreases. Interest in iHD is growing because reducing dialysis could improve patients' quality of life and reduce costs to the healthcare system.

    In accordance with HD adequacy guidelines (5,6), the current methods for calculating the dose of dialysis required to compensate for KRU reduction are based on the principle according to which the total weekly clearance must always be at least equal to the level of adequate clearance established for anuric patients on the conventional thrice-weekly HD (3HD/wk) regimen: in practice, at any time, the adequate dialytic clearance is given by the total adequate clearance minus KRU (7-10).

    The total weekly clearance is expressed by the so-called **equivalent continuous clearance (ECC) of urea**, which is a hypothetical continuous clearance capable of removing in a weekly period the same amount of urea jointly removed by both intermittent HD and continuous KRU in a given patient (7,9).

    There are two different ECCs, namely, the **standard Kt/V urea (stdKt/V)** (5,8) and the **Equivalent Renal Urea Clearance (EKRU)** (7,9), with different targets and consequent different dose and/or frequency of HD to be prescribed. In the absence of evidence on which ECC is preferable, EuReCa provides prescription and assessment for both to allow the nephrologist to choose based on his or her own judgment.

    According to 2015 KDOQI guidelines (5) the prescription should aim at a stdKt/V target of 2.3 volumes/week (v/wk), with a minimum stdKt/V to be delivered of 2.1. According to Casino and Basile (2,9) the prescription target of EKRUN is 12 – KRUN, with a minimum EKRUN to be delivered of 10 – 1.5 x KRUN. For clarity, EKRUN is the normalized EKRU = EKRU/V x 35 L, and KRUN is normalized KRUN = KRU/V x 35 L, while V is the patient's urea volume.
    """)

    # ---
    # References Section
    # ---
    st.subheader("References")
    st.write("""
    1. Casino FG, Lopez T, Santarsia G, et al. Could incremental haemodialysis be a new standard of care? A suggestion from a long-term observational study. G Ital Nefrol 2022; 39:3.
    2. Casino FG, Basile C, Kirmizis D, et al; Eudial Working Group of ERA-EDTA. The reasons for a clinical trial on incremental haemodialysis. Nephrol Dial Transplant 2020; 35: 2015–2019.
    3. Casino FG, Basile C. A user-friendly tool for incremental haemodialysis prescription. Nephrol Dial Transplant. 2018;33(6): 1046-1053. https://doi.org/10.1093/ndt/gfx343 pub 5/1/2018 EID: 2-s2.0-85044593750
    4. Daugirdas JT, Depner TA, Greene T et al. Solute-solver: a web-based tool for modeling urea kinetics for a broad range of hemodialysis schedules in multiple patients. Am J Kidney Dis 2009; 54: 798–809
    5. National Kidney Foundation. KDOQI clinical practice guidelines for hemodialysis adequacy: 2015 update. Am J Kidney Dis 2015; 66: 884–930
    6. European Best Practice Guidelines. II.3 Haemodialysis dose and residual renal function (Kr). Nephrol Dial Transplant 2002; 17 (Suppl 7): 24.
    7. Casino FG, Lopez T. The equivalent renal urea clearance: a new parameter to assess dialysis dose. Nephrol Dial Transplant 1996; 11: 1574–1581.
    8. Gotch FA: The current place of urea kinetic modelling with respect to different dialysis modalities. Nephrol Dial Transplant 13:S10-S145, 1998 (suppl 6)
    9. Casino FG, Basile C. The variable target model: a paradigm shift in the incremental haemodialysis prescription. Nephrol Dial Transplant 2017; 32:182–190, doi: 10.1093/ndt/gfw339.
    10. Casino FG, Casino A, Tarrio-Herva E, Basile C. New formulas for calculating dialysis dose in incremental haemodialysis. Nephrology Dialysis Transplantation https://doi.org/10.1093/ndt/gfaf147
    """)

    # ---
    # Disclaimer Section (using an expander)
    # ---
    with st.expander("Disclaimer"):
        st.subheader("1. THIS CALCULATION PROGRAM DOES NOT PROVIDE MEDICAL ADVICE")
        st.write("""
        The calculation program provided is available to you for informational purposes only. Although the calculation program provides educational information about healthcare, it does not provide medical diagnoses or recommendations regarding an individual’s medical treatment.
        This software is to be used as a guide only, and health care professionals should use sound clinical judgement and individualize therapy to each specific patient care situation. All calculations must be confirmed before clinical use or diagnostic purposes by qualified medical professionals.
        """)

        st.subheader("2. DISCLAIMER OF WARRANTIES")
        st.write("""
        You understand that we cannot and do not guarantee or warrant that files available for downloading from the Internet or this Site will be free of viruses or other destructive code. You are responsible for implementing sufficient procedures and checkpoints to satisfy your particular requirements for anti-virus protection and accuracy of data input and output, and for maintaining a means external to our site for any reconstruction of the lost data.
        We do not warrant that: (a) this calculation program will meet your requirements or will be available on an uninterrupted, timely, secure, or error-free basis; (b) the content will be up-to-date, complete, comprehensive or accurate; (c) the results that may be obtained from the use of this calculation program will be accurate or reliable; (d) defects, if any, will be corrected.
        """)

        st.subheader("3. LIMITATION OF LIABILITY")
        st.write("""
        In no event shall the authors be liable to any party for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this software and its documentation, even if the authors have been advised of the possibility of such damage. The authors specifically disclaim any warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose.
        The software provided hereunder is on an 'as is' basis, and the authors have no obligations to provide maintenance, support, updates, enhancements, or modifications.
        """)

        st.subheader("4. LIMITATIONS OF THE CALCULATION PROGRAM")
        st.write("""
        The code is quite complex, and it has not yet been extensively validated or tested, and there is no experience as of yet in using it in the pediatric population. The urea kinetic model depends on a stable level of both residual kidney function and urea generation rate and is intended for modeling chronic patients only; it is not applicable to modeling adequacy in patients with acute kidney injury.
        """)

    